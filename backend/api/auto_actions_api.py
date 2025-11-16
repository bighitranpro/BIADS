"""
Bi Ads - Auto Actions API
Author: Bi Ads Team
Version: 2.0.0
Endpoints for automated actions (view news, watch videos, hide notifications, approve tags)
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from core.database import get_db, Account, Task, ActivityLog

router = APIRouter(prefix="/api/auto-actions", tags=["Auto Actions"])

# ============================================
# PYDANTIC MODELS
# ============================================

class AutoViewNewsConfig(BaseModel):
    """Configuration for auto-viewing news feed"""
    account_id: int = Field(..., description="Account ID")
    enabled: bool = Field(True, description="Enable/disable auto-view")
    view_count: int = Field(20, description="Number of posts to view")
    view_duration: int = Field(5, description="Seconds per post")
    scroll_behavior: str = Field("natural", description="Scroll behavior: natural, fast, random")
    interaction_rate: float = Field(0.3, description="Chance to interact (0-1)")
    auto_like_enabled: bool = Field(False, description="Auto-like while viewing")
    auto_react_enabled: bool = Field(False, description="Auto-react while viewing")
    interval_minutes: int = Field(60, description="Run interval in minutes")
    
    @validator('view_count')
    def validate_view_count(cls, v):
        if v < 1 or v > 100:
            raise ValueError('View count must be between 1 and 100')
        return v
    
    @validator('interaction_rate')
    def validate_interaction_rate(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Interaction rate must be between 0 and 1')
        return v

class AutoWatchVideoConfig(BaseModel):
    """Configuration for auto-watching videos"""
    account_id: int = Field(..., description="Account ID")
    enabled: bool = Field(True, description="Enable/disable auto-watch")
    max_videos: int = Field(10, description="Maximum videos to watch")
    watch_duration: int = Field(30, description="Seconds per video")
    video_source: str = Field("feed", description="Source: feed, watch, suggested")
    auto_like: bool = Field(False, description="Auto-like videos")
    auto_comment: bool = Field(False, description="Auto-comment on videos")
    comment_templates: Optional[List[str]] = Field(None, description="Comment templates")
    skip_ads: bool = Field(True, description="Skip video ads")
    interval_minutes: int = Field(120, description="Run interval in minutes")
    
    @validator('max_videos')
    def validate_max_videos(cls, v):
        if v < 1 or v > 50:
            raise ValueError('Max videos must be between 1 and 50')
        return v

class HideNotificationConfig(BaseModel):
    """Configuration for hiding notifications"""
    account_id: int = Field(..., description="Account ID")
    notification_types: List[str] = Field(..., description="Types to hide: all, friend_requests, likes, comments, shares, tags")
    auto_hide_interval: int = Field(30, description="Check interval in minutes")
    keep_important: bool = Field(True, description="Keep important notifications")
    mark_as_read: bool = Field(True, description="Mark as read before hiding")

class ApproveTagConfig(BaseModel):
    """Configuration for approving tags"""
    account_id: int = Field(..., description="Account ID")
    auto_approve: bool = Field(False, description="Auto-approve all tags")
    auto_approve_from_friends: bool = Field(True, description="Auto-approve from friends only")
    whitelist_uids: Optional[List[str]] = Field(None, description="Always approve from these UIDs")
    blacklist_uids: Optional[List[str]] = Field(None, description="Never approve from these UIDs")
    approve_in_posts: bool = Field(True, description="Approve tags in posts")
    approve_in_photos: bool = Field(True, description="Approve tags in photos")
    approve_in_videos: bool = Field(True, description="Approve tags in videos")
    check_interval: int = Field(15, description="Check interval in minutes")

class AutoActionResponse(BaseModel):
    """Response for auto action operations"""
    success: bool
    message: str
    task_id: Optional[str]
    config_saved: bool

class AutoActionStats(BaseModel):
    """Statistics for auto actions"""
    news_views_today: int
    videos_watched_today: int
    notifications_hidden_today: int
    tags_approved_today: int
    active_auto_actions: int
    total_interactions_today: int

# ============================================
# HELPER FUNCTIONS
# ============================================

async def log_activity(db: AsyncSession, account_id: int, action: str, message: str, level: str = "info"):
    """Log auto action activity"""
    log_entry = ActivityLog(
        account_id=account_id,
        action=action,
        message=message,
        level=level,
        created_at=datetime.now()
    )
    db.add(log_entry)
    await db.commit()

async def create_auto_action_task(
    db: AsyncSession,
    account_id: int,
    task_type: str,
    params: Dict[str, Any]
) -> str:
    """Create an auto action task"""
    task_id = f"{task_type}_{int(datetime.now().timestamp())}"
    
    task = Task(
        task_id=task_id,
        account_id=account_id,
        task_type=task_type,
        task_name=task_type.replace('_', ' ').title(),
        params=json.dumps(params),
        status='pending',
        progress=0,
        created_at=datetime.now()
    )
    
    db.add(task)
    await db.commit()
    
    return task_id

# ============================================
# AUTO ACTIONS ENDPOINTS
# ============================================

@router.post("/auto-view-news", response_model=AutoActionResponse)
async def configure_auto_view_news(
    config: AutoViewNewsConfig,
    db: AsyncSession = Depends(get_db)
):
    """
    Configure automatic news feed viewing
    Sidebar task: auto-view-news
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == config.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create auto-view task if enabled
        task_id = None
        if config.enabled:
            task_id = await create_auto_action_task(
                db,
                config.account_id,
                "auto_view_news",
                {
                    "view_count": config.view_count,
                    "view_duration": config.view_duration,
                    "scroll_behavior": config.scroll_behavior,
                    "interaction_rate": config.interaction_rate,
                    "auto_like_enabled": config.auto_like_enabled,
                    "auto_react_enabled": config.auto_react_enabled,
                    "interval_minutes": config.interval_minutes
                }
            )
        
        # Log activity
        status = "enabled" if config.enabled else "disabled"
        await log_activity(
            db,
            config.account_id,
            "auto_view_news",
            f"Auto-view news {status} - viewing {config.view_count} posts",
            "success"
        )
        
        return AutoActionResponse(
            success=True,
            message=f"Auto-view news {status} successfully",
            task_id=task_id,
            config_saved=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configuring auto-view: {str(e)}")

@router.post("/auto-watch-video", response_model=AutoActionResponse)
async def configure_auto_watch_video(
    config: AutoWatchVideoConfig,
    db: AsyncSession = Depends(get_db)
):
    """
    Configure automatic video watching
    Sidebar task: auto-watch-video
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == config.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create auto-watch task if enabled
        task_id = None
        if config.enabled:
            task_id = await create_auto_action_task(
                db,
                config.account_id,
                "auto_watch_video",
                {
                    "max_videos": config.max_videos,
                    "watch_duration": config.watch_duration,
                    "video_source": config.video_source,
                    "auto_like": config.auto_like,
                    "auto_comment": config.auto_comment,
                    "comment_templates": config.comment_templates or [],
                    "skip_ads": config.skip_ads,
                    "interval_minutes": config.interval_minutes
                }
            )
        
        # Log activity
        status = "enabled" if config.enabled else "disabled"
        await log_activity(
            db,
            config.account_id,
            "auto_watch_video",
            f"Auto-watch video {status} - watching up to {config.max_videos} videos",
            "success"
        )
        
        return AutoActionResponse(
            success=True,
            message=f"Auto-watch video {status} successfully",
            task_id=task_id,
            config_saved=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configuring auto-watch: {str(e)}")

@router.post("/hide-notifications", response_model=AutoActionResponse)
async def configure_hide_notifications(
    config: HideNotificationConfig,
    db: AsyncSession = Depends(get_db)
):
    """
    Configure automatic notification hiding
    Sidebar task: hide-notif
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == config.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create hide notifications task
        task_id = await create_auto_action_task(
            db,
            config.account_id,
            "hide_notifications",
            {
                "notification_types": config.notification_types,
                "auto_hide_interval": config.auto_hide_interval,
                "keep_important": config.keep_important,
                "mark_as_read": config.mark_as_read
            }
        )
        
        # Log activity
        await log_activity(
            db,
            config.account_id,
            "hide_notifications",
            f"Hide notifications configured for types: {', '.join(config.notification_types)}",
            "success"
        )
        
        return AutoActionResponse(
            success=True,
            message="Notification hiding configured successfully",
            task_id=task_id,
            config_saved=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configuring hide notifications: {str(e)}")

@router.post("/approve-tags", response_model=AutoActionResponse)
async def configure_approve_tags(
    config: ApproveTagConfig,
    db: AsyncSession = Depends(get_db)
):
    """
    Configure automatic tag approval
    Sidebar task: approve-tag
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == config.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create approve tags task
        task_id = await create_auto_action_task(
            db,
            config.account_id,
            "approve_tags",
            {
                "auto_approve": config.auto_approve,
                "auto_approve_from_friends": config.auto_approve_from_friends,
                "whitelist_uids": config.whitelist_uids or [],
                "blacklist_uids": config.blacklist_uids or [],
                "approve_in_posts": config.approve_in_posts,
                "approve_in_photos": config.approve_in_photos,
                "approve_in_videos": config.approve_in_videos,
                "check_interval": config.check_interval
            }
        )
        
        # Log activity
        mode = "all tags" if config.auto_approve else "friends only" if config.auto_approve_from_friends else "selective"
        await log_activity(
            db,
            config.account_id,
            "approve_tags",
            f"Tag approval configured - mode: {mode}",
            "success"
        )
        
        return AutoActionResponse(
            success=True,
            message="Tag approval configured successfully",
            task_id=task_id,
            config_saved=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configuring tag approval: {str(e)}")

@router.get("/stats", response_model=AutoActionStats)
async def get_auto_action_stats(
    account_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for auto actions"""
    try:
        # Get today's date
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count auto actions today
        query = select(func.count(Task.id)).where(
            Task.created_at >= today,
            Task.task_type.in_([
                'auto_view_news', 'auto_watch_video',
                'hide_notifications', 'approve_tags'
            ])
        )
        
        if account_id:
            query = query.where(Task.account_id == account_id)
        
        result = await db.execute(query)
        total_actions = result.scalar() or 0
        
        # Count active auto action tasks
        active_query = select(func.count(Task.id)).where(
            Task.status.in_(['pending', 'processing']),
            Task.task_type.in_([
                'auto_view_news', 'auto_watch_video',
                'hide_notifications', 'approve_tags'
            ])
        )
        
        if account_id:
            active_query = active_query.where(Task.account_id == account_id)
        
        active_result = await db.execute(active_query)
        active_actions = active_result.scalar() or 0
        
        return AutoActionStats(
            news_views_today=0,  # TODO: Implement detailed tracking
            videos_watched_today=0,
            notifications_hidden_today=0,
            tags_approved_today=0,
            active_auto_actions=active_actions,
            total_interactions_today=total_actions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@router.get("/configs/{account_id}", response_model=Dict[str, Any])
async def get_auto_action_configs(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get current auto action configurations for an account"""
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Get recent auto action tasks for this account
        query = select(Task).where(
            Task.account_id == account_id,
            Task.task_type.in_([
                'auto_view_news', 'auto_watch_video',
                'hide_notifications', 'approve_tags'
            ]),
            Task.status.in_(['pending', 'processing'])
        ).order_by(Task.created_at.desc())
        
        task_result = await db.execute(query)
        tasks = task_result.scalars().all()
        
        configs = {}
        for task in tasks:
            configs[task.task_type] = {
                "task_id": task.task_id,
                "status": task.status,
                "params": json.loads(task.params) if task.params else {},
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
        
        return configs
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching configs: {str(e)}")

@router.delete("/stop/{task_id}", response_model=dict)
async def stop_auto_action(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Stop a running auto action task"""
    try:
        # Find task
        result = await db.execute(select(Task).where(Task.task_id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update task status
        task.status = 'cancelled'
        task.completed_at = datetime.now()
        await db.commit()
        
        # Log activity
        await log_activity(
            db,
            task.account_id,
            "stop_auto_action",
            f"Stopped auto action task {task_id}",
            "warning"
        )
        
        return {
            "success": True,
            "message": "Auto action stopped successfully",
            "task_id": task_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping task: {str(e)}")
