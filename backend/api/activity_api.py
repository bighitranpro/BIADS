"""
Activity Log API
REST endpoints cho quản lý activity logs
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from services.activity_logger import ActivityLogger
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/activity", tags=["Activity Logs"])


# Pydantic Schemas
class ActivityLogCreate(BaseModel):
    """Schema để tạo log mới"""
    action: str
    message: str
    level: str = "info"
    account_id: Optional[int] = None
    task_id: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class ActivityLogResponse(BaseModel):
    """Schema response cho log"""
    id: int
    account_id: Optional[int]
    task_id: Optional[str]
    action: str
    message: str
    level: str
    extra_data: Optional[Dict[str, Any]]
    created_at: str
    account_info: Optional[Dict[str, Any]]


class ActivityStatsResponse(BaseModel):
    """Schema response cho thống kê"""
    total_logs: int
    info_count: int
    success_count: int
    warning_count: int
    error_count: int
    recent_24h: int


# API Endpoints
@router.get("/", response_model=List[ActivityLogResponse])
async def get_activity_logs(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    level: Optional[str] = Query(None, description="Filter by level (info, success, warning, error)"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=500, description="Max number of logs"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách activity logs với filters
    
    Query params:
    - account_id: Filter theo account
    - action: Filter theo loại action
    - level: Filter theo level
    - start_date: Filter từ ngày (ISO format)
    - end_date: Filter đến ngày (ISO format)
    - limit: Số lượng tối đa (default 100, max 500)
    - offset: Bỏ qua bao nhiêu records (pagination)
    """
    try:
        # Parse dates nếu có
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if start_date else None
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None
        
        logs = await ActivityLogger.get_logs(
            db=db,
            account_id=account_id,
            action=action,
            level=level,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit,
            offset=offset
        )
        
        return logs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching logs: {str(e)}")


@router.post("/", response_model=Dict[str, Any])
async def create_activity_log(
    log_data: ActivityLogCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo activity log mới
    
    Body:
    - action: Loại hành động (VD: "assign_proxy", "check_account")
    - message: Mô tả chi tiết
    - level: Mức độ (info, success, warning, error)
    - account_id: ID tài khoản (optional)
    - task_id: ID task (optional)
    - extra_data: Dữ liệu bổ sung (optional)
    """
    try:
        log_entry = await ActivityLogger.log(
            db=db,
            action=log_data.action,
            message=log_data.message,
            level=log_data.level,
            account_id=log_data.account_id,
            task_id=log_data.task_id,
            extra_data=log_data.extra_data
        )
        
        return {
            "success": True,
            "message": "Activity log created successfully",
            "log_id": log_entry.id,
            "created_at": log_entry.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating log: {str(e)}")


@router.get("/stats", response_model=ActivityStatsResponse)
async def get_activity_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy thống kê tổng quan về activity logs
    
    Returns:
    - total_logs: Tổng số logs
    - info_count: Số logs level info
    - success_count: Số logs level success
    - warning_count: Số logs level warning
    - error_count: Số logs level error
    - recent_24h: Số logs trong 24h gần đây
    """
    try:
        stats = await ActivityLogger.get_stats(db=db)
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@router.delete("/clear-old")
async def clear_old_logs(
    days: int = Query(30, ge=1, le=365, description="Delete logs older than X days"),
    db: AsyncSession = Depends(get_db)
):
    """
    Xóa logs cũ hơn số ngày chỉ định
    
    Query params:
    - days: Xóa logs cũ hơn bao nhiêu ngày (default 30, max 365)
    """
    try:
        deleted_count = await ActivityLogger.clear_old_logs(db=db, days=days)
        
        return {
            "success": True,
            "message": f"Deleted {deleted_count} old logs",
            "deleted_count": deleted_count,
            "days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing logs: {str(e)}")


@router.get("/actions")
async def get_available_actions():
    """
    Lấy danh sách các action types có trong hệ thống
    """
    actions = [
        {"value": "assign_proxy", "label": "Gán Proxy"},
        {"value": "remove_proxy", "label": "Gỡ Proxy"},
        {"value": "check_account", "label": "Kiểm tra tài khoản"},
        {"value": "run_task", "label": "Chạy Task"},
        {"value": "task_complete", "label": "Task hoàn thành"},
        {"value": "delete_account", "label": "Xóa tài khoản"},
        {"value": "chrome_create", "label": "Tạo Chrome session"},
        {"value": "chrome_close", "label": "Đóng Chrome session"},
        {"value": "chrome_toggle", "label": "Toggle Chrome visibility"},
        {"value": "add_account", "label": "Thêm tài khoản"},
        {"value": "update_account", "label": "Cập nhật tài khoản"},
        {"value": "import_accounts", "label": "Import tài khoản"},
        {"value": "export_accounts", "label": "Export tài khoản"}
    ]
    
    return {
        "success": True,
        "actions": actions
    }


@router.get("/levels")
async def get_available_levels():
    """
    Lấy danh sách các log levels
    """
    levels = [
        {"value": "info", "label": "Info", "color": "#3b82f6"},
        {"value": "success", "label": "Success", "color": "#10b981"},
        {"value": "warning", "label": "Warning", "color": "#f59e0b"},
        {"value": "error", "label": "Error", "color": "#ef4444"}
    ]
    
    return {
        "success": True,
        "levels": levels
    }
