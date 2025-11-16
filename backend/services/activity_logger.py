"""
Activity Logger Service
Tự động log tất cả các hành động trong hệ thống
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from core.database import ActivityLog, Account
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json


class ActivityLogger:
    """Service để log các hoạt động trong hệ thống"""
    
    @staticmethod
    async def log(
        db: AsyncSession,
        action: str,
        message: str,
        level: str = "info",
        account_id: Optional[int] = None,
        task_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> ActivityLog:
        """
        Tạo log mới
        
        Args:
            db: Database session
            action: Loại hành động (assign_proxy, check_account, run_task, etc.)
            message: Mô tả chi tiết
            level: Mức độ (info, success, warning, error)
            account_id: ID tài khoản liên quan
            task_id: ID task liên quan
            extra_data: Dữ liệu bổ sung dạng dict
        
        Returns:
            ActivityLog object đã được tạo
        """
        log_entry = ActivityLog(
            account_id=account_id,
            task_id=task_id,
            action=action,
            message=message,
            level=level,
            extra_data=json.dumps(extra_data) if extra_data else None,
            created_at=datetime.now()
        )
        
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        
        return log_entry
    
    @staticmethod
    async def get_logs(
        db: AsyncSession,
        account_id: Optional[int] = None,
        action: Optional[str] = None,
        level: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Lấy danh sách logs với filter
        
        Args:
            db: Database session
            account_id: Filter theo account ID
            action: Filter theo loại action
            level: Filter theo level
            start_date: Filter từ ngày
            end_date: Filter đến ngày
            limit: Số lượng tối đa
            offset: Bỏ qua bao nhiêu records
        
        Returns:
            List các log entries với thông tin account
        """
        # Build query với filters
        query = select(ActivityLog).order_by(ActivityLog.created_at.desc())
        
        conditions = []
        if account_id:
            conditions.append(ActivityLog.account_id == account_id)
        if action:
            conditions.append(ActivityLog.action == action)
        if level:
            conditions.append(ActivityLog.level == level)
        if start_date:
            conditions.append(ActivityLog.created_at >= start_date)
        if end_date:
            conditions.append(ActivityLog.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        # Convert to dict và thêm account info
        logs_data = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "account_id": log.account_id,
                "task_id": log.task_id,
                "action": log.action,
                "message": log.message,
                "level": log.level,
                "extra_data": json.loads(log.extra_data) if log.extra_data else None,
                "created_at": log.created_at.isoformat(),
                "account_info": None
            }
            
            # Lấy thông tin account nếu có
            if log.account_id:
                account_result = await db.execute(
                    select(Account).where(Account.id == log.account_id)
                )
                account = account_result.scalar_one_or_none()
                if account:
                    log_dict["account_info"] = {
                        "uid": account.uid,
                        "name": account.name,
                        "username": account.username
                    }
            
            logs_data.append(log_dict)
        
        return logs_data
    
    @staticmethod
    async def get_stats(db: AsyncSession) -> Dict[str, Any]:
        """
        Lấy thống kê tổng quan về logs
        
        Returns:
            Dict chứa các thống kê
        """
        # Total logs
        total_result = await db.execute(select(ActivityLog))
        total_logs = len(total_result.scalars().all())
        
        # Count by level
        info_result = await db.execute(
            select(ActivityLog).where(ActivityLog.level == "info")
        )
        info_count = len(info_result.scalars().all())
        
        success_result = await db.execute(
            select(ActivityLog).where(ActivityLog.level == "success")
        )
        success_count = len(success_result.scalars().all())
        
        warning_result = await db.execute(
            select(ActivityLog).where(ActivityLog.level == "warning")
        )
        warning_count = len(warning_result.scalars().all())
        
        error_result = await db.execute(
            select(ActivityLog).where(ActivityLog.level == "error")
        )
        error_count = len(error_result.scalars().all())
        
        # Recent 24h
        yesterday = datetime.now() - timedelta(days=1)
        recent_result = await db.execute(
            select(ActivityLog).where(ActivityLog.created_at >= yesterday)
        )
        recent_count = len(recent_result.scalars().all())
        
        return {
            "total_logs": total_logs,
            "info_count": info_count,
            "success_count": success_count,
            "warning_count": warning_count,
            "error_count": error_count,
            "recent_24h": recent_count
        }
    
    @staticmethod
    async def clear_old_logs(
        db: AsyncSession,
        days: int = 30
    ) -> int:
        """
        Xóa logs cũ hơn số ngày chỉ định
        
        Args:
            db: Database session
            days: Xóa logs cũ hơn bao nhiêu ngày
        
        Returns:
            Số lượng logs đã xóa
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        result = await db.execute(
            select(ActivityLog).where(ActivityLog.created_at < cutoff_date)
        )
        old_logs = result.scalars().all()
        
        count = len(old_logs)
        
        for log in old_logs:
            await db.delete(log)
        
        await db.commit()
        
        return count


# Helper functions để dễ sử dụng
async def log_proxy_assign(db: AsyncSession, account_id: int, proxy_id: int):
    """Log khi gán proxy"""
    await ActivityLogger.log(
        db,
        action="assign_proxy",
        message=f"Gán proxy #{proxy_id} cho tài khoản",
        level="success",
        account_id=account_id,
        extra_data={"proxy_id": proxy_id}
    )


async def log_proxy_remove(db: AsyncSession, account_id: int):
    """Log khi gỡ proxy"""
    await ActivityLogger.log(
        db,
        action="remove_proxy",
        message="Gỡ proxy khỏi tài khoản",
        level="info",
        account_id=account_id
    )


async def log_account_check(db: AsyncSession, account_id: int, status: str, task_id: str = None):
    """Log khi check account"""
    await ActivityLogger.log(
        db,
        action="check_account",
        message=f"Kiểm tra tài khoản - Kết quả: {status}",
        level="success" if status == "live" else "error",
        account_id=account_id,
        task_id=task_id,
        extra_data={"status": status}
    )


async def log_task_run(db: AsyncSession, task_id: str, task_type: str, account_id: int = None):
    """Log khi chạy task"""
    await ActivityLogger.log(
        db,
        action="run_task",
        message=f"Bắt đầu chạy task: {task_type}",
        level="info",
        account_id=account_id,
        task_id=task_id,
        extra_data={"task_type": task_type}
    )


async def log_task_complete(db: AsyncSession, task_id: str, task_type: str, success: bool, account_id: int = None):
    """Log khi task hoàn thành"""
    await ActivityLogger.log(
        db,
        action="task_complete",
        message=f"Task {task_type} {'thành công' if success else 'thất bại'}",
        level="success" if success else "error",
        account_id=account_id,
        task_id=task_id,
        extra_data={"task_type": task_type, "success": success}
    )


async def log_account_delete(db: AsyncSession, account_uid: str):
    """Log khi xóa account"""
    await ActivityLogger.log(
        db,
        action="delete_account",
        message=f"Xóa tài khoản {account_uid}",
        level="warning",
        extra_data={"account_uid": account_uid}
    )


async def log_chrome_session(db: AsyncSession, account_id: int, action: str, headless: bool = None):
    """Log các thao tác với Chrome session"""
    messages = {
        "create": "Tạo Chrome session mới",
        "close": "Đóng Chrome session",
        "toggle": f"Chuyển Chrome sang chế độ {'headless' if headless else 'visible'}"
    }
    
    await ActivityLogger.log(
        db,
        action=f"chrome_{action}",
        message=messages.get(action, f"Chrome action: {action}"),
        level="info",
        account_id=account_id,
        extra_data={"action": action, "headless": headless}
    )
