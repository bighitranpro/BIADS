"""
Bi Ads - Miscellaneous Features API
Author: Bi Ads Team
Version: 2.0.0
Endpoints for miscellaneous features (poke, cancel request, invite to group, etc.)
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import re

from core.database import get_db, Account, Task, ActivityLog

router = APIRouter(prefix="/api/misc", tags=["Miscellaneous Features"])

# ============================================
# PYDANTIC MODELS
# ============================================

class PokeFriendsRequest(BaseModel):
    """Model for poking friends"""
    account_id: int = Field(..., description="Account ID")
    friend_uids: List[str] = Field(..., description="Friend UIDs to poke")
    delay_between: int = Field(10, description="Delay between pokes (seconds)")
    
    @validator('friend_uids')
    def validate_uids(cls, v):
        for uid in v:
            if not re.match(r'^\d{10,20}$', uid):
                raise ValueError(f'Invalid UID format: {uid}')
        return v

class CancelFriendRequestRequest(BaseModel):
    """Model for cancelling friend requests"""
    account_id: int = Field(..., description="Account ID")
    target_uids: List[str] = Field(..., description="UIDs to cancel requests")
    
    @validator('target_uids')
    def validate_uids(cls, v):
        for uid in v:
            if not re.match(r'^\d{10,20}$', uid):
                raise ValueError(f'Invalid UID format: {uid}')
        return v

class InviteToGroupRequest(BaseModel):
    """Model for inviting friends to group"""
    account_id: int = Field(..., description="Account ID")
    group_id: str = Field(..., description="Group ID")
    friend_uids: List[str] = Field(..., description="Friend UIDs to invite")
    delay_between: int = Field(5, description="Delay between invites (seconds)")
    
    @validator('friend_uids')
    def validate_uids(cls, v):
        for uid in v:
            if not re.match(r'^\d{10,20}$', uid):
                raise ValueError(f'Invalid UID format: {uid}')
        return v

class JoinViaUIDRequest(BaseModel):
    """Model for joining group via UID"""
    account_id: int = Field(..., description="Account ID")
    group_uids: List[str] = Field(..., description="Group UIDs to join")
    delay_between: int = Field(10, description="Delay between joins (seconds)")

class DeletePostRequest(BaseModel):
    """Model for deleting posts"""
    account_id: int = Field(..., description="Account ID")
    post_ids: List[str] = Field(..., description="Post IDs to delete")
    confirm_delete: bool = Field(False, description="Confirm deletion")

class SharePostRequest(BaseModel):
    """Model for sharing posts (alternative method)"""
    account_id: int = Field(..., description="Account ID")
    post_url: str = Field(..., description="Post URL to share")
    share_to: str = Field("timeline", description="Where to share: timeline, group, story")
    message: Optional[str] = Field(None, description="Share message")
    target_group_id: Optional[str] = Field(None, description="Group ID if sharing to group")

class UpdateBioRequest(BaseModel):
    """Model for updating profile bio"""
    account_id: int = Field(..., description="Account ID")
    bio_text: str = Field(..., description="New bio text", max_length=101)
    work_info: Optional[str] = Field(None, description="Work information")
    education_info: Optional[str] = Field(None, description="Education information")
    location: Optional[str] = Field(None, description="Current location")
    hometown: Optional[str] = Field(None, description="Hometown")
    relationship_status: Optional[str] = Field(None, description="Relationship status")

class MiscActionResponse(BaseModel):
    """Response for miscellaneous actions"""
    success: bool
    message: str
    task_id: Optional[str]
    processed_count: Optional[int]

# ============================================
# HELPER FUNCTIONS
# ============================================

async def log_activity(db: AsyncSession, account_id: int, action: str, message: str, level: str = "info"):
    """Log miscellaneous activity"""
    log_entry = ActivityLog(
        account_id=account_id,
        action=action,
        message=message,
        level=level,
        created_at=datetime.now()
    )
    db.add(log_entry)
    await db.commit()

async def create_misc_task(
    db: AsyncSession,
    account_id: int,
    task_type: str,
    params: Dict[str, Any]
) -> str:
    """Create a miscellaneous task"""
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
# MISCELLANEOUS ENDPOINTS
# ============================================

@router.post("/poke-friends", response_model=MiscActionResponse)
async def poke_friends(
    poke_data: PokeFriendsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Poke friends
    Sidebar task: poke-friends
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == poke_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create poke task
        task_id = await create_misc_task(
            db,
            poke_data.account_id,
            "poke_friends",
            {
                "friend_uids": poke_data.friend_uids,
                "delay_between": poke_data.delay_between,
                "total_pokes": len(poke_data.friend_uids)
            }
        )
        
        # Log activity
        await log_activity(
            db,
            poke_data.account_id,
            "poke_friends",
            f"Poking {len(poke_data.friend_uids)} friends",
            "info"
        )
        
        return MiscActionResponse(
            success=True,
            message=f"Poking {len(poke_data.friend_uids)} friends",
            task_id=task_id,
            processed_count=0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error poking friends: {str(e)}")

@router.post("/cancel-friend-request", response_model=MiscActionResponse)
async def cancel_friend_requests(
    cancel_data: CancelFriendRequestRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel sent friend requests
    Sidebar task: cancel-request
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == cancel_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create cancel task
        task_id = await create_misc_task(
            db,
            cancel_data.account_id,
            "cancel_friend_request",
            {
                "target_uids": cancel_data.target_uids,
                "total_cancellations": len(cancel_data.target_uids)
            }
        )
        
        # Log activity
        await log_activity(
            db,
            cancel_data.account_id,
            "cancel_friend_request",
            f"Cancelling {len(cancel_data.target_uids)} friend requests",
            "warning"
        )
        
        return MiscActionResponse(
            success=True,
            message=f"Cancelling {len(cancel_data.target_uids)} friend requests",
            task_id=task_id,
            processed_count=0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling requests: {str(e)}")

@router.post("/invite-to-group", response_model=MiscActionResponse)
async def invite_friends_to_group(
    invite_data: InviteToGroupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Invite friends to a group
    Sidebar task: invite-to-group
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == invite_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create invite task
        task_id = await create_misc_task(
            db,
            invite_data.account_id,
            "invite_to_group",
            {
                "group_id": invite_data.group_id,
                "friend_uids": invite_data.friend_uids,
                "delay_between": invite_data.delay_between,
                "total_invites": len(invite_data.friend_uids)
            }
        )
        
        # Log activity
        await log_activity(
            db,
            invite_data.account_id,
            "invite_to_group",
            f"Inviting {len(invite_data.friend_uids)} friends to group {invite_data.group_id}",
            "info"
        )
        
        return MiscActionResponse(
            success=True,
            message=f"Inviting {len(invite_data.friend_uids)} friends to group",
            task_id=task_id,
            processed_count=0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inviting to group: {str(e)}")

@router.post("/join-via-uid", response_model=MiscActionResponse)
async def join_groups_via_uid(
    join_data: JoinViaUIDRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Join groups using group UIDs
    Sidebar task: join-via-uid
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == join_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create join task
        task_id = await create_misc_task(
            db,
            join_data.account_id,
            "join_via_uid",
            {
                "group_uids": join_data.group_uids,
                "delay_between": join_data.delay_between,
                "total_groups": len(join_data.group_uids)
            }
        )
        
        # Log activity
        await log_activity(
            db,
            join_data.account_id,
            "join_via_uid",
            f"Joining {len(join_data.group_uids)} groups via UID",
            "info"
        )
        
        return MiscActionResponse(
            success=True,
            message=f"Joining {len(join_data.group_uids)} groups",
            task_id=task_id,
            processed_count=0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error joining groups: {str(e)}")

@router.post("/delete-post", response_model=MiscActionResponse)
async def delete_posts(
    delete_data: DeletePostRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete posts from timeline
    Sidebar task: delete-post
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == delete_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        if not delete_data.confirm_delete:
            raise HTTPException(status_code=400, detail="Must confirm deletion")
        
        # Create delete task
        task_id = await create_misc_task(
            db,
            delete_data.account_id,
            "delete_post",
            {
                "post_ids": delete_data.post_ids,
                "total_deletions": len(delete_data.post_ids)
            }
        )
        
        # Log activity
        await log_activity(
            db,
            delete_data.account_id,
            "delete_post",
            f"Deleting {len(delete_data.post_ids)} posts",
            "warning"
        )
        
        return MiscActionResponse(
            success=True,
            message=f"Deleting {len(delete_data.post_ids)} posts",
            task_id=task_id,
            processed_count=0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting posts: {str(e)}")

@router.post("/share-post-2", response_model=MiscActionResponse)
async def share_post_alternative(
    share_data: SharePostRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Share post (alternative method)
    Sidebar task: share-post-2
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == share_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create share task
        task_id = await create_misc_task(
            db,
            share_data.account_id,
            "share_post_2",
            {
                "post_url": share_data.post_url,
                "share_to": share_data.share_to,
                "message": share_data.message,
                "target_group_id": share_data.target_group_id
            }
        )
        
        # Log activity
        await log_activity(
            db,
            share_data.account_id,
            "share_post_2",
            f"Sharing post to {share_data.share_to}",
            "info"
        )
        
        return MiscActionResponse(
            success=True,
            message=f"Post shared to {share_data.share_to}",
            task_id=task_id,
            processed_count=1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sharing post: {str(e)}")

@router.post("/update-bio", response_model=MiscActionResponse)
async def update_profile_bio(
    bio_data: UpdateBioRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update profile bio and information
    Sidebar task: update-bio
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == bio_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create update bio task
        task_id = await create_misc_task(
            db,
            bio_data.account_id,
            "update_bio",
            {
                "bio_text": bio_data.bio_text,
                "work_info": bio_data.work_info,
                "education_info": bio_data.education_info,
                "location": bio_data.location,
                "hometown": bio_data.hometown,
                "relationship_status": bio_data.relationship_status
            }
        )
        
        # Log activity
        await log_activity(
            db,
            bio_data.account_id,
            "update_bio",
            "Updated profile bio and information",
            "success"
        )
        
        return MiscActionResponse(
            success=True,
            message="Profile bio updated successfully",
            task_id=task_id,
            processed_count=1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating bio: {str(e)}")

@router.get("/tasks/{account_id}", response_model=List[Dict[str, Any]])
async def get_misc_tasks(
    account_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get miscellaneous tasks for an account"""
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Get tasks
        query = select(Task).where(
            Task.account_id == account_id,
            Task.task_type.in_([
                'poke_friends', 'cancel_friend_request', 'invite_to_group',
                'join_via_uid', 'delete_post', 'share_post_2', 'update_bio'
            ])
        ).order_by(Task.created_at.desc()).limit(limit)
        
        task_result = await db.execute(query)
        tasks = task_result.scalars().all()
        
        return [
            {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "task_name": task.task_name,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            for task in tasks
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")
