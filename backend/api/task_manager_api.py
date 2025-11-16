"""
Task Manager API
Manages task history and Chrome sessions
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime

from core.database import get_db, Task, Account
from core import crud
from services.chrome_manager import chrome_manager

router = APIRouter(prefix="/api/tasks", tags=["task-manager"])


# ============================================
# PYDANTIC MODELS
# ============================================

class ChromeSessionCreate(BaseModel):
    account_id: int
    headless: bool = True


class ChromeSessionToggle(BaseModel):
    account_id: int


class TaskHistoryResponse(BaseModel):
    id: int
    task_id: str
    account_id: int
    account_uid: str
    account_name: Optional[str]
    task_type: str
    task_name: str
    status: str
    progress: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    error_message: Optional[str]
    result: Optional[str]
    
    class Config:
        from_attributes = True


class ChromeSessionResponse(BaseModel):
    account_id: int
    account_uid: str
    is_headless: bool
    status: str
    created_at: str
    last_activity: str
    has_proxy: bool
    proxy_ip: Optional[str]


# ============================================
# TASK HISTORY ENDPOINTS
# ============================================

@router.get("/history", response_model=List[TaskHistoryResponse])
async def get_task_history(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get task history with filtering"""
    try:
        query = select(Task).order_by(desc(Task.created_at))
        
        if status:
            query = query.filter(Task.status == status)
        
        if task_type:
            query = query.filter(Task.task_type == task_type)
        
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        # Join with account data
        response = []
        for task in tasks:
            account = await crud.get_account(db, task.account_id)
            
            response.append(TaskHistoryResponse(
                id=task.id,
                task_id=task.task_id,
                account_id=task.account_id,
                account_uid=account.uid if account else "Unknown",
                account_name=account.name if account else None,
                task_type=task.task_type,
                task_name=task.task_name,
                status=task.status,
                progress=task.progress,
                started_at=task.started_at,
                completed_at=task.completed_at,
                created_at=task.created_at,
                error_message=task.error_message,
                result=task.result
            ))
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching task history: {str(e)}")


@router.get("/history/{task_id}")
async def get_task_detail(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get detailed information about a specific task"""
    try:
        query = select(Task).filter(Task.task_id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        account = await crud.get_account(db, task.account_id)
        
        return {
            "success": True,
            "task": TaskHistoryResponse(
                id=task.id,
                task_id=task.task_id,
                account_id=task.account_id,
                account_uid=account.uid if account else "Unknown",
                account_name=account.name if account else None,
                task_type=task.task_type,
                task_name=task.task_name,
                status=task.status,
                progress=task.progress,
                started_at=task.started_at,
                completed_at=task.completed_at,
                created_at=task.created_at,
                error_message=task.error_message,
                result=task.result
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching task detail: {str(e)}")


@router.delete("/history/{task_id}")
async def delete_task_history(task_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a task from history"""
    try:
        query = select(Task).filter(Task.task_id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        await db.delete(task)
        await db.commit()
        
        return {
            "success": True,
            "message": "Task deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")


@router.post("/history/clear")
async def clear_task_history(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """Clear task history (optionally by status)"""
    try:
        query = select(Task)
        
        if status:
            query = query.filter(Task.status == status)
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        count = len(tasks)
        
        for task in tasks:
            await db.delete(task)
        
        await db.commit()
        
        return {
            "success": True,
            "message": f"Cleared {count} tasks from history",
            "count": count
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")


# ============================================
# CHROME SESSION MANAGEMENT
# ============================================

@router.post("/chrome/create", response_model=ChromeSessionResponse)
async def create_chrome_session(request: ChromeSessionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new Chrome session for an account"""
    try:
        # Get account info
        account = await crud.get_account(db, request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Get proxy if assigned
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
            proxy=proxy,
            headless=request.headless
        )
        
        return ChromeSessionResponse(**session.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Chrome session: {str(e)}")


@router.get("/chrome/sessions", response_model=List[ChromeSessionResponse])
async def get_chrome_sessions():
    """Get all active Chrome sessions"""
    try:
        sessions = chrome_manager.get_all_sessions()
        return [ChromeSessionResponse(**s) for s in sessions]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sessions: {str(e)}")


@router.get("/chrome/session/{account_id}")
async def get_chrome_session(account_id: int):
    """Get specific Chrome session info"""
    try:
        session = await chrome_manager.get_session(account_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Chrome session not found for this account")
        
        return {
            "success": True,
            "session": ChromeSessionResponse(**session.to_dict())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching session: {str(e)}")


@router.post("/chrome/toggle/{account_id}")
async def toggle_chrome_visibility(account_id: int):
    """Toggle between headless and visible mode for a Chrome session"""
    try:
        success = await chrome_manager.toggle_session_visibility(account_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Chrome session not found or toggle failed")
        
        session = await chrome_manager.get_session(account_id)
        
        return {
            "success": True,
            "message": f"Toggled to {'visible' if not session.is_headless else 'headless'} mode",
            "session": ChromeSessionResponse(**session.to_dict())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling visibility: {str(e)}")


@router.delete("/chrome/session/{account_id}")
async def close_chrome_session(account_id: int):
    """Close a specific Chrome session"""
    try:
        await chrome_manager.close_session(account_id)
        
        return {
            "success": True,
            "message": f"Chrome session closed for account {account_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error closing session: {str(e)}")


@router.post("/chrome/close-all")
async def close_all_chrome_sessions():
    """Close all active Chrome sessions"""
    try:
        await chrome_manager.close_all_sessions()
        
        return {
            "success": True,
            "message": "All Chrome sessions closed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error closing all sessions: {str(e)}")


@router.get("/stats")
async def get_task_stats(db: AsyncSession = Depends(get_db)):
    """Get task statistics"""
    try:
        # Count tasks by status
        query = select(Task)
        result = await db.execute(query)
        all_tasks = result.scalars().all()
        
        stats = {
            'total': len(all_tasks),
            'pending': sum(1 for t in all_tasks if t.status == 'pending'),
            'processing': sum(1 for t in all_tasks if t.status == 'processing'),
            'completed': sum(1 for t in all_tasks if t.status == 'completed'),
            'failed': sum(1 for t in all_tasks if t.status == 'failed'),
            'cancelled': sum(1 for t in all_tasks if t.status == 'cancelled'),
            'active_chrome_sessions': chrome_manager.get_session_count()
        }
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")
