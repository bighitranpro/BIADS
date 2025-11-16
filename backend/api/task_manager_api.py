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


class TaskCreateRequest(BaseModel):
    account_id: int
    task_type: str
    task_name: str
    params: Optional[Dict[str, Any]] = None


class TaskUpdateStatusRequest(BaseModel):
    status: str  # pending, processing, completed, failed, cancelled
    progress: Optional[int] = None
    error_message: Optional[str] = None
    result: Optional[str] = None


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
# TASK CRUD ENDPOINTS
# ============================================

@router.post("/create")
async def create_task(request: TaskCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new task
    
    - Validates account exists
    - Generates unique task_id
    - Creates task in pending status
    - Logs task creation
    """
    try:
        # Validate account exists
        account = await crud.get_account(db, request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Generate unique task ID
        task_id = f"{request.task_type}_{request.account_id}_{int(datetime.now().timestamp())}"
        
        # Create task
        task = await crud.create_task(db, {
            'task_id': task_id,
            'account_id': request.account_id,
            'task_type': request.task_type,
            'task_name': request.task_name,
            'params': str(request.params) if request.params else None,
            'status': 'pending',
            'progress': 0
        })
        
        # Log activity
        await crud.create_log(db, {
            'account_id': request.account_id,
            'task_id': task_id,
            'action': 'create_task',
            'message': f"Created task: {request.task_name}",
            'level': 'info'
        })
        
        return {
            "success": True,
            "message": "Task created successfully",
            "task_id": task_id,
            "task": {
                "id": task.id,
                "task_id": task.task_id,
                "account_id": task.account_id,
                "task_type": task.task_type,
                "task_name": task.task_name,
                "status": task.status,
                "created_at": task.created_at.isoformat()
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


@router.put("/{task_id}/status")
async def update_task_status(
    task_id: str,
    request: TaskUpdateStatusRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update task status and progress
    
    - Updates task status (pending, processing, completed, failed, cancelled)
    - Updates progress (0-100)
    - Sets error_message or result
    - Logs status change
    """
    try:
        # Get task
        query = select(Task).filter(Task.task_id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Valid statuses
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Update task fields
        task.status = request.status
        
        if request.progress is not None:
            task.progress = min(100, max(0, request.progress))  # Clamp between 0-100
        
        if request.error_message:
            task.error_message = request.error_message
        
        if request.result:
            task.result = request.result
        
        # Set timestamps
        if request.status == 'processing' and not task.started_at:
            task.started_at = datetime.now()
        
        if request.status in ['completed', 'failed', 'cancelled']:
            task.completed_at = datetime.now()
        
        await db.commit()
        await db.refresh(task)
        
        # Log activity
        await crud.create_log(db, {
            'account_id': task.account_id,
            'task_id': task_id,
            'action': 'update_task_status',
            'message': f"Task status updated to: {request.status}",
            'level': 'success' if request.status == 'completed' else 'info'
        })
        
        return {
            "success": True,
            "message": f"Task status updated to: {request.status}",
            "task": {
                "id": task.id,
                "task_id": task.task_id,
                "status": task.status,
                "progress": task.progress,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "error_message": task.error_message,
                "result": task.result
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating task status: {str(e)}")


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """
    Cancel a pending or processing task
    
    - Only cancels tasks that are pending or processing
    - Sets status to cancelled
    - Logs cancellation
    """
    try:
        # Get task
        query = select(Task).filter(Task.task_id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Check if task can be cancelled
        if task.status not in ['pending', 'processing']:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel task with status: {task.status}. Only pending or processing tasks can be cancelled."
            )
        
        # Cancel task
        task.status = 'cancelled'
        task.completed_at = datetime.now()
        task.error_message = "Task cancelled by user"
        
        await db.commit()
        await db.refresh(task)
        
        # Log activity
        await crud.create_log(db, {
            'account_id': task.account_id,
            'task_id': task_id,
            'action': 'cancel_task',
            'message': f"Task cancelled: {task.task_name}",
            'level': 'warning'
        })
        
        return {
            "success": True,
            "message": "Task cancelled successfully",
            "task": {
                "id": task.id,
                "task_id": task.task_id,
                "status": task.status,
                "completed_at": task.completed_at.isoformat()
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error cancelling task: {str(e)}")


@router.post("/{task_id}/retry")
async def retry_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """
    Retry a failed task
    
    - Only retries failed tasks
    - Resets status to pending
    - Clears error_message
    - Resets progress to 0
    - Logs retry action
    """
    try:
        # Get task
        query = select(Task).filter(Task.task_id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Check if task can be retried
        if task.status != 'failed':
            raise HTTPException(
                status_code=400,
                detail=f"Cannot retry task with status: {task.status}. Only failed tasks can be retried."
            )
        
        # Reset task for retry
        task.status = 'pending'
        task.progress = 0
        task.error_message = None
        task.result = None
        task.started_at = None
        task.completed_at = None
        
        await db.commit()
        await db.refresh(task)
        
        # Log activity
        await crud.create_log(db, {
            'account_id': task.account_id,
            'task_id': task_id,
            'action': 'retry_task',
            'message': f"Task retry initiated: {task.task_name}",
            'level': 'info'
        })
        
        return {
            "success": True,
            "message": "Task reset for retry",
            "task": {
                "id": task.id,
                "task_id": task.task_id,
                "status": task.status,
                "progress": task.progress
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error retrying task: {str(e)}")


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
