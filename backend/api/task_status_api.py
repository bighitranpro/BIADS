"""
Task Status API
Real-time task status updates via polling
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from core.database import get_db, Task, Account
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/task", tags=["Task Status"])


@router.get("/{task_id}/status")
async def get_task_status(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy status của một task cụ thể
    
    Returns:
    - task_id: ID của task
    - status: pending, processing, completed, failed, cancelled
    - progress: 0-100
    - started_at: Thời gian bắt đầu
    - completed_at: Thời gian hoàn thành (nếu có)
    - result: Kết quả (nếu có)
    - error_message: Lỗi (nếu có)
    """
    try:
        result = await db.execute(
            select(Task).where(Task.task_id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "task_name": task.task_name,
            "status": task.status,
            "progress": task.progress,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "created_at": task.created_at.isoformat(),
            "result": task.result,
            "error_message": task.error_message,
            "account_id": task.account_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_task_logs(
    task_id: Optional[str] = Query(None, description="Filter by task ID"),
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200, description="Max number of logs"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy task logs với filters
    
    Query params:
    - task_id: Filter theo task ID
    - account_id: Filter theo account ID
    - status: Filter theo status
    - limit: Số lượng tối đa (default 50, max 200)
    - offset: Bỏ qua bao nhiêu records
    """
    try:
        query = select(Task).order_by(Task.created_at.desc())
        
        conditions = []
        if task_id:
            conditions.append(Task.task_id == task_id)
        if account_id:
            conditions.append(Task.account_id == account_id)
        if status:
            conditions.append(Task.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        logs = []
        for task in tasks:
            logs.append({
                "task_id": task.task_id,
                "task_type": task.task_type,
                "task_name": task.task_name,
                "status": task.status,
                "progress": task.progress,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "created_at": task.created_at.isoformat(),
                "result": task.result,
                "error_message": task.error_message,
                "account_id": task.account_id
            })
        
        return {
            "success": True,
            "logs": logs,
            "count": len(logs),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/running")
async def get_running_tasks(
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy tất cả tasks đang chạy (status = processing hoặc pending)
    
    Returns list of running tasks với thông tin account
    """
    try:
        query = select(Task).where(
            or_(Task.status == 'processing', Task.status == 'pending')
        ).order_by(Task.created_at.desc())
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        running_tasks = []
        for task in tasks:
            # Get account info
            account_result = await db.execute(
                select(Account).where(Account.id == task.account_id)
            )
            account = account_result.scalar_one_or_none()
            
            running_tasks.append({
                "task_id": task.task_id,
                "task_type": task.task_type,
                "task_name": task.task_name,
                "status": task.status,
                "progress": task.progress,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "created_at": task.created_at.isoformat(),
                "account": {
                    "id": account.id,
                    "uid": account.uid,
                    "name": account.name,
                    "username": account.username
                } if account else None
            })
        
        return {
            "success": True,
            "running_tasks": running_tasks,
            "count": len(running_tasks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_tasks(
    hours: int = Query(24, ge=1, le=168, description="Get tasks from last X hours (default 24, max 168)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy tasks gần đây trong X giờ
    
    Query params:
    - hours: Lấy tasks từ X giờ trước (default 24, max 168 = 7 days)
    """
    try:
        since = datetime.now() - timedelta(hours=hours)
        
        query = select(Task).where(
            Task.created_at >= since
        ).order_by(Task.created_at.desc())
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        recent_tasks = []
        for task in tasks:
            recent_tasks.append({
                "task_id": task.task_id,
                "task_type": task.task_type,
                "task_name": task.task_name,
                "status": task.status,
                "progress": task.progress,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "created_at": task.created_at.isoformat(),
                "account_id": task.account_id
            })
        
        return {
            "success": True,
            "recent_tasks": recent_tasks,
            "count": len(recent_tasks),
            "hours": hours
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run")
async def run_task(
    task_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a new task
    
    Body:
    - task_type: Type of task (check_account, join_groups, etc.)
    - account_id: ID of account to use
    - params: Task parameters (optional)
    """
    try:
        from core import crud
        import uuid
        
        task_type = task_data.get('task_type')
        account_id = task_data.get('account_id')
        params = task_data.get('params', {})
        
        if not task_type or not account_id:
            raise HTTPException(status_code=400, detail="task_type and account_id are required")
        
        # Check if account exists
        account = await crud.get_account(db, account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create task
        task_id = f"{task_type}_{uuid.uuid4().hex[:8]}"
        task = Task(
            task_id=task_id,
            account_id=account_id,
            task_type=task_type,
            task_name=task_type.replace('_', ' ').title(),
            params=str(params),
            status='pending',
            progress=0,
            created_at=datetime.now()
        )
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task {task_type} created successfully",
            "task": {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
