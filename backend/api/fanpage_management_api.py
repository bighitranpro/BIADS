"""
Bi Ads - Fanpage Management API
Author: Bi Ads Team
Version: 2.0.0
Endpoints for managing Facebook fanpages
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import re

from core.database import get_db, Account, Task, ActivityLog

router = APIRouter(prefix="/api/fanpages", tags=["Fanpage Management"])

# ============================================
# PYDANTIC MODELS
# ============================================

class FanpageCreate(BaseModel):
    """Model for creating a fanpage"""
    page_id: str = Field(..., description="Facebook Page ID")
    page_name: str = Field(..., description="Page name")
    page_url: Optional[str] = Field(None, description="Page URL")
    account_id: int = Field(..., description="Managing account ID")
    category: Optional[str] = Field("business", description="Page category")
    access_token: Optional[str] = Field(None, description="Page access token")
    status: str = Field("active", description="Page status")
    
    @validator('page_id')
    def validate_page_id(cls, v):
        if not re.match(r'^\d{10,20}$', v):
            raise ValueError('Invalid Page ID format')
        return v

class FanpagePostCreate(BaseModel):
    """Model for posting to fanpage"""
    account_id: int = Field(..., description="Account ID")
    page_id: str = Field(..., description="Target page ID")
    content: str = Field(..., description="Post content")
    images: Optional[List[str]] = Field(None, description="Image URLs")
    scheduled_time: Optional[datetime] = Field(None, description="Schedule post time")

class FanpageInteractionConfig(BaseModel):
    """Model for auto-interaction configuration"""
    account_id: int = Field(..., description="Account ID")
    page_id: str = Field(..., description="Target page ID")
    auto_like: bool = Field(True, description="Auto like posts")
    auto_comment: bool = Field(False, description="Auto comment")
    auto_share: bool = Field(False, description="Auto share")
    comment_templates: Optional[List[str]] = Field(None, description="Comment templates")
    interaction_interval: int = Field(300, description="Interval in seconds")

class FanpageLikeInvite(BaseModel):
    """Model for inviting friends to like page"""
    account_id: int = Field(..., description="Account ID")
    page_id: str = Field(..., description="Target page ID")
    friend_uids: List[str] = Field(..., description="Friend UIDs to invite")
    delay_between: int = Field(10, description="Delay between invites (seconds)")

class FanpageMessageSend(BaseModel):
    """Model for sending message to page"""
    account_id: int = Field(..., description="Account ID")
    page_id: str = Field(..., description="Target page ID")
    message: str = Field(..., description="Message content")

class FanpageShareRequest(BaseModel):
    """Model for sharing fanpage"""
    account_id: int = Field(..., description="Account ID")
    page_id: str = Field(..., description="Page ID to share")
    share_type: str = Field("profile", description="Where to share: profile, group, story")
    message: Optional[str] = Field(None, description="Share message")
    target_group_id: Optional[str] = Field(None, description="Group ID if sharing to group")

class FanpagePostDelete(BaseModel):
    """Model for deleting fanpage post"""
    account_id: int = Field(..., description="Account ID")
    page_id: str = Field(..., description="Page ID")
    post_id: str = Field(..., description="Post ID to delete")

class FanpageEdit(BaseModel):
    """Model for editing fanpage info"""
    account_id: int = Field(..., description="Account ID")
    page_id: str = Field(..., description="Page ID")
    page_name: Optional[str] = Field(None, description="New page name")
    description: Optional[str] = Field(None, description="New description")
    category: Optional[str] = Field(None, description="New category")
    cover_photo_url: Optional[str] = Field(None, description="Cover photo URL")
    profile_photo_url: Optional[str] = Field(None, description="Profile photo URL")

class FanpageResponse(BaseModel):
    """Response model for fanpage"""
    id: int
    page_id: str
    page_name: str
    page_url: Optional[str]
    category: str
    status: str
    followers_count: int
    likes_count: int
    posts_count: int
    created_at: datetime
    updated_at: datetime

class FanpageStats(BaseModel):
    """Statistics for fanpages"""
    total_pages: int
    active_pages: int
    inactive_pages: int
    total_followers: int
    total_posts_today: int
    total_interactions_today: int
    top_performing_pages: List[Dict[str, Any]]

# ============================================
# HELPER FUNCTIONS
# ============================================

async def log_activity(db: AsyncSession, account_id: int, action: str, message: str, level: str = "info"):
    """Log fanpage activity"""
    log_entry = ActivityLog(
        account_id=account_id,
        action=action,
        message=message,
        level=level,
        created_at=datetime.now()
    )
    db.add(log_entry)
    await db.commit()

async def create_fanpage_task(
    db: AsyncSession,
    account_id: int,
    task_type: str,
    params: Dict[str, Any]
) -> str:
    """Create a fanpage management task"""
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
# FANPAGE MANAGEMENT ENDPOINTS
# ============================================

@router.get("/", response_model=List[FanpageResponse])
async def get_fanpages(
    account_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get list of managed fanpages"""
    try:
        # For now, return mock data since we don't have Fanpage model yet
        # In production, you'd query actual fanpages from database
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fanpages: {str(e)}")

@router.post("/manage", response_model=dict)
async def manage_fanpage(
    fanpage_data: FanpageCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Add fanpage to management
    Sidebar task: manage-fanpage
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == fanpage_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create task to add fanpage
        task_id = await create_fanpage_task(
            db,
            fanpage_data.account_id,
            "manage_fanpage",
            {
                "page_id": fanpage_data.page_id,
                "page_name": fanpage_data.page_name,
                "page_url": fanpage_data.page_url,
                "category": fanpage_data.category,
                "action": "add_to_management"
            }
        )
        
        # Log activity
        await log_activity(
            db,
            fanpage_data.account_id,
            "manage_fanpage",
            f"Added fanpage {fanpage_data.page_name} (ID: {fanpage_data.page_id}) to management",
            "success"
        )
        
        return {
            "success": True,
            "message": f"Fanpage {fanpage_data.page_name} added to management",
            "task_id": task_id,
            "page_id": fanpage_data.page_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error managing fanpage: {str(e)}")

@router.post("/post", response_model=dict)
async def post_to_fanpage(
    post_data: FanpagePostCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Post content to fanpage
    Sidebar task: post-fanpage
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == post_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create posting task
        task_id = await create_fanpage_task(
            db,
            post_data.account_id,
            "post_fanpage",
            {
                "page_id": post_data.page_id,
                "content": post_data.content,
                "images": post_data.images or [],
                "scheduled_time": post_data.scheduled_time.isoformat() if post_data.scheduled_time else None
            }
        )
        
        # Log activity
        await log_activity(
            db,
            post_data.account_id,
            "post_fanpage",
            f"Created post on fanpage {post_data.page_id}",
            "info"
        )
        
        return {
            "success": True,
            "message": "Fanpage post created successfully",
            "task_id": task_id,
            "scheduled": post_data.scheduled_time is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error posting to fanpage: {str(e)}")

@router.post("/auto-like", response_model=dict)
async def configure_auto_like_fanpage(
    config: FanpageInteractionConfig,
    db: AsyncSession = Depends(get_db)
):
    """
    Configure auto-like for fanpage posts
    Sidebar task: like-fanpage-auto
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == config.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create auto-like task
        task_id = await create_fanpage_task(
            db,
            config.account_id,
            "like_fanpage_auto",
            {
                "page_id": config.page_id,
                "auto_like": config.auto_like,
                "auto_comment": config.auto_comment,
                "auto_share": config.auto_share,
                "comment_templates": config.comment_templates or [],
                "interaction_interval": config.interaction_interval
            }
        )
        
        # Log activity
        await log_activity(
            db,
            config.account_id,
            "like_fanpage_auto",
            f"Configured auto-like for fanpage {config.page_id}",
            "success"
        )
        
        return {
            "success": True,
            "message": "Auto-like configured successfully",
            "task_id": task_id,
            "config": {
                "auto_like": config.auto_like,
                "auto_comment": config.auto_comment,
                "auto_share": config.auto_share,
                "interval": config.interaction_interval
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configuring auto-like: {str(e)}")

@router.post("/invite-likes", response_model=dict)
async def invite_friends_to_like_fanpage(
    invite_data: FanpageLikeInvite,
    db: AsyncSession = Depends(get_db)
):
    """
    Invite friends to like fanpage
    Sidebar task: invite-like-fanpage
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == invite_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create invite task
        task_id = await create_fanpage_task(
            db,
            invite_data.account_id,
            "invite_like_fanpage",
            {
                "page_id": invite_data.page_id,
                "friend_uids": invite_data.friend_uids,
                "delay_between": invite_data.delay_between,
                "total_invites": len(invite_data.friend_uids)
            }
        )
        
        # Log activity
        await log_activity(
            db,
            invite_data.account_id,
            "invite_like_fanpage",
            f"Inviting {len(invite_data.friend_uids)} friends to like fanpage {invite_data.page_id}",
            "info"
        )
        
        return {
            "success": True,
            "message": f"Inviting {len(invite_data.friend_uids)} friends to like fanpage",
            "task_id": task_id,
            "total_invites": len(invite_data.friend_uids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inviting friends: {str(e)}")

@router.post("/interact", response_model=dict)
async def interact_with_fanpage(
    config: FanpageInteractionConfig,
    db: AsyncSession = Depends(get_db)
):
    """
    Configure interactions with fanpage (like, comment, share)
    Sidebar task: interact-fanpage
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == config.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create interaction task
        task_id = await create_fanpage_task(
            db,
            config.account_id,
            "interact_fanpage",
            {
                "page_id": config.page_id,
                "auto_like": config.auto_like,
                "auto_comment": config.auto_comment,
                "auto_share": config.auto_share,
                "comment_templates": config.comment_templates or [],
                "interaction_interval": config.interaction_interval
            }
        )
        
        # Log activity
        await log_activity(
            db,
            config.account_id,
            "interact_fanpage",
            f"Configured interactions for fanpage {config.page_id}",
            "success"
        )
        
        return {
            "success": True,
            "message": "Fanpage interactions configured",
            "task_id": task_id,
            "interactions": {
                "like": config.auto_like,
                "comment": config.auto_comment,
                "share": config.auto_share
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configuring interactions: {str(e)}")

@router.post("/send-inbox", response_model=dict)
async def send_inbox_to_fanpage(
    message_data: FanpageMessageSend,
    db: AsyncSession = Depends(get_db)
):
    """
    Send message to fanpage inbox
    Sidebar task: send-inbox-fanpage
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == message_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create send message task
        task_id = await create_fanpage_task(
            db,
            message_data.account_id,
            "send_inbox_fanpage",
            {
                "page_id": message_data.page_id,
                "message": message_data.message
            }
        )
        
        # Log activity
        await log_activity(
            db,
            message_data.account_id,
            "send_inbox_fanpage",
            f"Sent message to fanpage {message_data.page_id}",
            "info"
        )
        
        return {
            "success": True,
            "message": "Message sent to fanpage inbox",
            "task_id": task_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@router.post("/send-message", response_model=dict)
async def send_message_to_fanpage(
    message_data: FanpageMessageSend,
    db: AsyncSession = Depends(get_db)
):
    """
    Send message to fanpage (alternative endpoint)
    Sidebar task: message-fanpage
    """
    try:
        # Reuse send_inbox_to_fanpage logic
        return await send_inbox_to_fanpage(message_data, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@router.post("/share", response_model=dict)
async def share_fanpage(
    share_data: FanpageShareRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Share fanpage to profile/group/story
    Sidebar task: share-fanpage
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == share_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create share task
        task_id = await create_fanpage_task(
            db,
            share_data.account_id,
            "share_fanpage",
            {
                "page_id": share_data.page_id,
                "share_type": share_data.share_type,
                "message": share_data.message,
                "target_group_id": share_data.target_group_id
            }
        )
        
        # Log activity
        await log_activity(
            db,
            share_data.account_id,
            "share_fanpage",
            f"Shared fanpage {share_data.page_id} to {share_data.share_type}",
            "info"
        )
        
        return {
            "success": True,
            "message": f"Fanpage shared to {share_data.share_type}",
            "task_id": task_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sharing fanpage: {str(e)}")

@router.post("/delete-post", response_model=dict)
async def delete_fanpage_post(
    delete_data: FanpagePostDelete,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a post from fanpage
    Sidebar task: delete-fanpage-post
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == delete_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create delete task
        task_id = await create_fanpage_task(
            db,
            delete_data.account_id,
            "delete_fanpage_post",
            {
                "page_id": delete_data.page_id,
                "post_id": delete_data.post_id
            }
        )
        
        # Log activity
        await log_activity(
            db,
            delete_data.account_id,
            "delete_fanpage_post",
            f"Deleted post {delete_data.post_id} from fanpage {delete_data.page_id}",
            "warning"
        )
        
        return {
            "success": True,
            "message": "Fanpage post deleted successfully",
            "task_id": task_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting post: {str(e)}")

@router.post("/edit", response_model=dict)
async def edit_fanpage_info(
    edit_data: FanpageEdit,
    db: AsyncSession = Depends(get_db)
):
    """
    Edit fanpage information
    Sidebar task: edit-fanpage
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == edit_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create edit task
        task_id = await create_fanpage_task(
            db,
            edit_data.account_id,
            "edit_fanpage",
            {
                "page_id": edit_data.page_id,
                "page_name": edit_data.page_name,
                "description": edit_data.description,
                "category": edit_data.category,
                "cover_photo_url": edit_data.cover_photo_url,
                "profile_photo_url": edit_data.profile_photo_url
            }
        )
        
        # Log activity
        await log_activity(
            db,
            edit_data.account_id,
            "edit_fanpage",
            f"Edited fanpage {edit_data.page_id} information",
            "info"
        )
        
        return {
            "success": True,
            "message": "Fanpage information updated",
            "task_id": task_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error editing fanpage: {str(e)}")

@router.get("/stats", response_model=FanpageStats)
async def get_fanpage_stats(
    account_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get fanpage statistics"""
    try:
        # Mock stats for now
        return FanpageStats(
            total_pages=0,
            active_pages=0,
            inactive_pages=0,
            total_followers=0,
            total_posts_today=0,
            total_interactions_today=0,
            top_performing_pages=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")
