"""
Friend Management API

Handles friend requests, friend list management, and friend-related operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
import json

from core.database import get_db, Account, FacebookID
from services.activity_logger import ActivityLogger

router = APIRouter(prefix="/api/friends", tags=["Friend Management"])

# Pydantic Models
class FriendRequest(BaseModel):
    account_id: int = Field(..., description="Account ID to perform action")
    target_uid: str = Field(..., description="Target user UID")
    target_name: Optional[str] = Field(None, description="Target user name")
    
    @validator('target_uid')
    def validate_uid(cls, v):
        if not v or len(v) < 10 or len(v) > 20:
            raise ValueError('Invalid UID format')
        if not v.isdigit():
            raise ValueError('UID must contain only digits')
        return v

class BulkFriendRequest(BaseModel):
    account_id: int = Field(..., description="Account ID to perform action")
    target_uids: List[str] = Field(..., description="List of target UIDs")
    delay_min: int = Field(5, ge=1, le=60, description="Minimum delay between actions (seconds)")
    delay_max: int = Field(15, ge=1, le=120, description="Maximum delay between actions (seconds)")

class FriendScanRequest(BaseModel):
    account_id: int = Field(..., description="Account ID to scan friends")
    source_type: str = Field("profile", description="Source type: profile, group, post")
    source_id: Optional[str] = Field(None, description="Source ID (group ID or post ID)")
    limit: int = Field(100, ge=1, le=1000, description="Maximum friends to scan")

class FriendStats(BaseModel):
    total_friends: int
    pending_requests_sent: int
    pending_requests_received: int
    friends_added_today: int
    friends_added_this_week: int
    friends_removed_today: int
    mutual_friends_avg: int

class FriendTaskResponse(BaseModel):
    success: bool
    message: str
    task_id: str
    account_id: int
    status: str = "pending"
    total_targets: int = 0
    processed: int = 0

class FriendListResponse(BaseModel):
    uid: str
    name: Optional[str]
    username: Optional[str]
    profile_url: Optional[str]
    is_friend: bool
    friendship_status: str  # friend, pending_sent, pending_received, not_friend
    mutual_friends_count: Optional[int]
    added_at: Optional[datetime]
    source: Optional[str]

# API Endpoints

@router.post("/add", response_model=FriendTaskResponse)
async def add_friend(
    request_data: FriendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send friend request to a single user
    """
    try:
        # Verify account exists
        account_query = select(Account).where(Account.id == request_data.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Check if target already exists in FacebookID table
        existing_query = select(FacebookID).where(FacebookID.uid == request_data.target_uid)
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if not existing:
            # Create new FacebookID entry
            new_fb_id = FacebookID(
                uid=request_data.target_uid,
                name=request_data.target_name,
                status='valid',
                is_friend=False,
                source='manual',
                collected_by_account_id=request_data.account_id
            )
            db.add(new_fb_id)
            await db.commit()
        
        # Create task ID
        task_id = f"add_friend_{request_data.account_id}_{int(datetime.now().timestamp())}"
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            account_id=request_data.account_id,
            action="add_friend",
            message=f"Sending friend request to {request_data.target_uid}",
            level="info",
            extra_data={"target_uid": request_data.target_uid, "task_id": task_id}
        )
        
        return FriendTaskResponse(
            success=True,
            message="Friend request task created",
            task_id=task_id,
            account_id=request_data.account_id,
            status="pending",
            total_targets=1,
            processed=0
        )
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add friend: {str(e)}")


@router.post("/add-bulk", response_model=FriendTaskResponse)
async def add_friends_bulk(
    request_data: BulkFriendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send friend requests to multiple users
    """
    try:
        # Verify account exists
        account_query = select(Account).where(Account.id == request_data.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Validate UIDs
        valid_uids = []
        for uid in request_data.target_uids:
            if uid and len(uid) >= 10 and len(uid) <= 20 and uid.isdigit():
                valid_uids.append(uid)
        
        if not valid_uids:
            raise HTTPException(status_code=400, detail="No valid UIDs provided")
        
        # Create task ID
        task_id = f"add_friends_bulk_{request_data.account_id}_{int(datetime.now().timestamp())}"
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            account_id=request_data.account_id,
            action="add_friends_bulk",
            message=f"Bulk adding {len(valid_uids)} friends",
            level="info",
            extra_data={
                "task_id": task_id,
                "total_uids": len(valid_uids),
                "delay_range": f"{request_data.delay_min}-{request_data.delay_max}s"
            }
        )
        
        return FriendTaskResponse(
            success=True,
            message=f"Bulk friend request task created for {len(valid_uids)} users",
            task_id=task_id,
            account_id=request_data.account_id,
            status="pending",
            total_targets=len(valid_uids),
            processed=0
        )
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create bulk task: {str(e)}")


@router.post("/unfriend", response_model=dict)
async def unfriend_user(
    request_data: FriendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Unfriend a user
    """
    try:
        # Verify account exists
        account_query = select(Account).where(Account.id == request_data.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Update FacebookID entry if exists
        fb_id_query = select(FacebookID).where(FacebookID.uid == request_data.target_uid)
        fb_id_result = await db.execute(fb_id_query)
        fb_id = fb_id_result.scalar_one_or_none()
        
        if fb_id:
            fb_id.is_friend = False
            await db.commit()
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            account_id=request_data.account_id,
            action="unfriend",
            message=f"Unfriended {request_data.target_uid}",
            level="warning",
            extra_data={"target_uid": request_data.target_uid}
        )
        
        return {
            "success": True,
            "message": f"Successfully unfriended {request_data.target_uid}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to unfriend: {str(e)}")


@router.post("/accept-request", response_model=dict)
async def accept_friend_request(
    request_data: FriendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Accept a friend request
    """
    try:
        # Verify account exists
        account_query = select(Account).where(Account.id == request_data.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Update or create FacebookID entry
        fb_id_query = select(FacebookID).where(FacebookID.uid == request_data.target_uid)
        fb_id_result = await db.execute(fb_id_query)
        fb_id = fb_id_result.scalar_one_or_none()
        
        if fb_id:
            fb_id.is_friend = True
        else:
            new_fb_id = FacebookID(
                uid=request_data.target_uid,
                name=request_data.target_name,
                is_friend=True,
                source='friend_request',
                collected_by_account_id=request_data.account_id
            )
            db.add(new_fb_id)
        
        await db.commit()
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            account_id=request_data.account_id,
            action="accept_friend_request",
            message=f"Accepted friend request from {request_data.target_uid}",
            level="success",
            extra_data={"target_uid": request_data.target_uid}
        )
        
        return {
            "success": True,
            "message": f"Successfully accepted friend request from {request_data.target_uid}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to accept request: {str(e)}")


@router.post("/reject-request", response_model=dict)
async def reject_friend_request(
    request_data: FriendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a friend request
    """
    try:
        # Verify account exists
        account_query = select(Account).where(Account.id == request_data.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            account_id=request_data.account_id,
            action="reject_friend_request",
            message=f"Rejected friend request from {request_data.target_uid}",
            level="info",
            extra_data={"target_uid": request_data.target_uid}
        )
        
        return {
            "success": True,
            "message": f"Successfully rejected friend request from {request_data.target_uid}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reject request: {str(e)}")


@router.post("/scan", response_model=dict)
async def scan_friends(
    scan_data: FriendScanRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Scan and collect friend list from account/group/post
    """
    try:
        # Verify account exists
        account_query = select(Account).where(Account.id == scan_data.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create task ID
        task_id = f"scan_friends_{scan_data.account_id}_{int(datetime.now().timestamp())}"
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            account_id=scan_data.account_id,
            action="scan_friends",
            message=f"Scanning friends from {scan_data.source_type}",
            level="info",
            extra_data={
                "task_id": task_id,
                "source_type": scan_data.source_type,
                "source_id": scan_data.source_id,
                "limit": scan_data.limit
            }
        )
        
        return {
            "success": True,
            "message": f"Friend scan task created",
            "task_id": task_id,
            "source_type": scan_data.source_type,
            "limit": scan_data.limit
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to scan friends: {str(e)}")


@router.get("/list", response_model=List[FriendListResponse])
async def get_friend_list(
    account_id: Optional[int] = Query(None, description="Filter by account"),
    is_friend: Optional[bool] = Query(None, description="Filter by friend status"),
    search: Optional[str] = Query(None, description="Search by name or UID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of friends/potential friends
    """
    try:
        query = select(FacebookID)
        
        conditions = []
        if account_id:
            conditions.append(FacebookID.collected_by_account_id == account_id)
        if is_friend is not None:
            conditions.append(FacebookID.is_friend == is_friend)
        if search:
            conditions.append(
                or_(
                    FacebookID.uid.ilike(f"%{search}%"),
                    FacebookID.name.ilike(f"%{search}%"),
                    FacebookID.username.ilike(f"%{search}%")
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(FacebookID.created_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        friends = result.scalars().all()
        
        return [
            FriendListResponse(
                uid=f.uid,
                name=f.name,
                username=f.username,
                profile_url=f.profile_url,
                is_friend=f.is_friend,
                friendship_status='friend' if f.is_friend else 'not_friend',
                mutual_friends_count=None,
                added_at=f.created_at,
                source=f.source
            )
            for f in friends
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get friend list: {str(e)}")


@router.get("/stats", response_model=FriendStats)
async def get_friend_stats(
    account_id: Optional[int] = Query(None, description="Filter by account"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get friend management statistics
    """
    try:
        base_query = select(FacebookID)
        if account_id:
            base_query = base_query.where(FacebookID.collected_by_account_id == account_id)
        
        # Total friends
        friends_query = select(func.count(FacebookID.id)).where(FacebookID.is_friend == True)
        if account_id:
            friends_query = friends_query.where(FacebookID.collected_by_account_id == account_id)
        friends_result = await db.execute(friends_query)
        total_friends = friends_result.scalar() or 0
        
        # Friends added today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_query = select(func.count(FacebookID.id)).where(
            and_(
                FacebookID.is_friend == True,
                FacebookID.created_at >= today_start
            )
        )
        if account_id:
            today_query = today_query.where(FacebookID.collected_by_account_id == account_id)
        today_result = await db.execute(today_query)
        friends_today = today_result.scalar() or 0
        
        # Friends added this week
        week_start = datetime.now() - timedelta(days=7)
        week_query = select(func.count(FacebookID.id)).where(
            and_(
                FacebookID.is_friend == True,
                FacebookID.created_at >= week_start
            )
        )
        if account_id:
            week_query = week_query.where(FacebookID.collected_by_account_id == account_id)
        week_result = await db.execute(week_query)
        friends_week = week_result.scalar() or 0
        
        return FriendStats(
            total_friends=total_friends,
            pending_requests_sent=0,  # Placeholder - would need additional tracking
            pending_requests_received=0,  # Placeholder - would need additional tracking
            friends_added_today=friends_today,
            friends_added_this_week=friends_week,
            friends_removed_today=0,  # Placeholder - would need additional tracking
            mutual_friends_avg=0  # Placeholder - would need API integration
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/import", response_model=dict)
async def import_friend_list(
    account_id: int = Query(..., description="Account ID"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Import friend list from file (UIDs, one per line)
    """
    try:
        # Verify account exists
        account_query = select(Account).where(Account.id == account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Parse UIDs
        lines = content_str.strip().split('\n')
        uids = []
        for line in lines:
            line = line.strip()
            if line and len(line) >= 10 and len(line) <= 20 and line.isdigit():
                uids.append(line)
        
        if not uids:
            raise HTTPException(status_code=400, detail="No valid UIDs found in file")
        
        # Import UIDs
        imported = 0
        skipped = 0
        
        for uid in uids:
            # Check if already exists
            existing_query = select(FacebookID).where(FacebookID.uid == uid)
            existing_result = await db.execute(existing_query)
            existing = existing_result.scalar_one_or_none()
            
            if existing:
                skipped += 1
                continue
            
            # Create new entry
            new_fb_id = FacebookID(
                uid=uid,
                status='valid',
                is_friend=False,
                source='import',
                collected_by_account_id=account_id
            )
            db.add(new_fb_id)
            imported += 1
        
        await db.commit()
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            account_id=account_id,
            action="import_friend_list",
            message=f"Imported {imported} UIDs, skipped {skipped} duplicates",
            level="success",
            extra_data={"imported": imported, "skipped": skipped}
        )
        
        return {
            "success": True,
            "message": f"Imported {imported} UIDs",
            "imported": imported,
            "skipped": skipped,
            "total": len(uids)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to import: {str(e)}")
