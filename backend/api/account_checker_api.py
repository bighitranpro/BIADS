"""
Account Checker API
Check Facebook account status using Chrome automation
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from core.database import get_db, Task
from core import crud
from services.chrome_manager import chrome_manager
from services.facebook_automator import FacebookAutomator
from services.activity_logger import log_account_check, log_chrome_session

router = APIRouter(prefix="/api/accounts", tags=["account-checker"])


class CheckAccountRequest(BaseModel):
    account_id: int


class CheckMultipleAccountsRequest(BaseModel):
    account_ids: List[int]


async def check_account_task(account_id: int, db: AsyncSession):
    """Background task to check account status"""
    account = None
    session = None
    task = None
    
    try:
        # Get account
        account = await crud.get_account(db, account_id)
        if not account:
            return
        
        # Create task record
        task_id = f"check_{account.uid}_{uuid.uuid4().hex[:8]}"
        task = Task(
            task_id=task_id,
            account_id=account.id,
            task_type='check_account',
            task_name=f'Check Account {account.uid}',
            status='processing',
            progress=0,
            started_at=datetime.now()
        )
        db.add(task)
        await db.commit()
        
        # Get proxy if available
        proxy = None
        if account.proxy_id:
            proxy_obj = await crud.get_proxy(db, account.proxy_id)
            if proxy_obj:
                proxy = {
                    'ip': proxy_obj.ip,
                    'port': proxy_obj.port,
                    'username': proxy_obj.username,
                    'password': proxy_obj.password,
                    'protocol': proxy_obj.protocol
                }
        
        # Create Chrome session
        session = await chrome_manager.create_session(
            account_id=account.id,
            account_uid=account.uid,
            cookies=account.cookies,
            email=account.email,
            password=account.password,
            two_fa_key=account.two_fa_key,
            proxy=proxy,
            headless=True
        )
        
        # Log Chrome session creation
        await log_chrome_session(db, account.id, "create", headless=True)
        
        # Update task progress
        task.progress = 30
        await db.commit()
        
        # Create automator
        automator = FacebookAutomator(session)
        
        # Check account status
        result = await automator.check_account_live()
        
        # Update account status in database
        if result['status'] == 'live':
            account.status = 'active'
            if 'account_name' in result:
                account.name = result['account_name']
        elif result['status'] == 'checkpoint':
            account.status = 'checkpoint'
        elif result['status'] == 'die':
            account.status = 'inactive'
        else:
            account.status = 'unknown'
        
        account.last_used = datetime.now()
        
        # Update task
        task.status = 'completed'
        task.progress = 100
        task.completed_at = datetime.now()
        task.result = str(result)
        
        await db.commit()
        
        # Log account check result
        await log_account_check(
            db,
            account_id=account.id,
            status=result['status'],
            task_id=task_id
        )
        
        # Log
        await crud.create_log(
            db,
            level='success' if result['success'] else 'error',
            message=f"Account check completed: {result['message']}",
            details=f"Account: {account.uid}, Status: {result['status']}"
        )
        
    except Exception as e:
        if task:
            task.status = 'failed'
            task.error_message = str(e)
            task.completed_at = datetime.now()
            await db.commit()
        
        if account:
            await crud.create_log(
                db,
                level='error',
                message=f"Account check failed: {str(e)}",
                details=f"Account: {account.uid}"
            )
    
    finally:
        # Keep Chrome session open for potential reuse
        # User can close it manually from Chrome Sessions panel
        pass


@router.post("/check")
async def check_account_status(
    request: CheckAccountRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Check single account status"""
    try:
        account = await crud.get_account(db, request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Add to background tasks
        background_tasks.add_task(check_account_task, request.account_id, db)
        
        return {
            'success': True,
            'message': f'Started checking account {account.uid}',
            'account_id': account.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-multiple")
async def check_multiple_accounts(
    request: CheckMultipleAccountsRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Check multiple accounts status"""
    try:
        accounts = []
        for account_id in request.account_ids:
            account = await crud.get_account(db, account_id)
            if account:
                accounts.append(account)
                # Add each check as background task
                background_tasks.add_task(check_account_task, account_id, db)
        
        return {
            'success': True,
            'message': f'Started checking {len(accounts)} accounts',
            'account_count': len(accounts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
