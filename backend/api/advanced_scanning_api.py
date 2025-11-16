"""
Bi Ads - Advanced Scanning API
Author: Bi Ads Team
Version: 2.0.0
Endpoints for advanced scanning operations
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import re

from core.database import get_db, Account, FacebookID, Task, ActivityLog

router = APIRouter(prefix="/api/scanning", tags=["Advanced Scanning"])

# ============================================
# PYDANTIC MODELS
# ============================================

class ScanPostsRequest(BaseModel):
    """Model for scanning posts"""
    account_id: int = Field(..., description="Account ID")
    source_type: str = Field(..., description="Source type: profile, group, page")
    source_id: str = Field(..., description="Source ID (UID/Group ID/Page ID)")
    scan_type: str = Field("recent", description="Scan type: recent, top, all")
    max_posts: int = Field(50, description="Maximum posts to scan")
    collect_uids: bool = Field(True, description="Collect UIDs from posts")
    
    @validator('max_posts')
    def validate_max_posts(cls, v):
        if v < 1 or v > 500:
            raise ValueError('Max posts must be between 1 and 500')
        return v

class ScanGroupMembersRequest(BaseModel):
    """Model for scanning group members"""
    account_id: int = Field(..., description="Account ID")
    group_id: str = Field(..., description="Facebook Group ID")
    max_members: int = Field(100, description="Maximum members to scan")
    member_type: str = Field("all", description="Member type: all, admins, moderators, new")
    collect_profile_info: bool = Field(True, description="Collect detailed profile info")
    
    @validator('max_members')
    def validate_max_members(cls, v):
        if v < 1 or v > 5000:
            raise ValueError('Max members must be between 1 and 5000')
        return v

class ScanFollowersRequest(BaseModel):
    """Model for scanning followers"""
    account_id: int = Field(..., description="Account ID")
    target_uid: str = Field(..., description="Target profile UID")
    max_followers: int = Field(100, description="Maximum followers to scan")
    scan_depth: str = Field("basic", description="Scan depth: basic, detailed")
    
    @validator('target_uid')
    def validate_uid(cls, v):
        if not re.match(r'^\d{10,20}$', v):
            raise ValueError('Invalid UID format')
        return v

class ScanRecentFriendsRequest(BaseModel):
    """Model for scanning recent friends"""
    account_id: int = Field(..., description="Account ID")
    target_uid: Optional[str] = Field(None, description="Target UID (if None, use account's own)")
    days_back: int = Field(30, description="How many days back to scan")
    max_friends: int = Field(100, description="Maximum friends to collect")
    
    @validator('days_back')
    def validate_days(cls, v):
        if v < 1 or v > 365:
            raise ValueError('Days must be between 1 and 365')
        return v

class ScanFriendSuggestionsRequest(BaseModel):
    """Model for scanning friend suggestions"""
    account_id: int = Field(..., description="Account ID")
    max_suggestions: int = Field(50, description="Maximum suggestions to collect")
    filter_mutual_friends: bool = Field(False, description="Only with mutual friends")
    min_mutual_friends: int = Field(0, description="Minimum mutual friends count")

class ScanResponse(BaseModel):
    """Response for scan operations"""
    success: bool
    message: str
    task_id: str
    total_found: int
    collection_status: str

class ScanStats(BaseModel):
    """Statistics for scanning operations"""
    total_scans_today: int
    posts_scanned_today: int
    members_scanned_today: int
    followers_scanned_today: int
    total_uids_collected: int
    recent_scans: List[Dict[str, Any]]

# ============================================
# HELPER FUNCTIONS
# ============================================

async def log_activity(db: AsyncSession, account_id: int, action: str, message: str, level: str = "info"):
    """Log scanning activity"""
    log_entry = ActivityLog(
        account_id=account_id,
        action=action,
        message=message,
        level=level,
        created_at=datetime.now()
    )
    db.add(log_entry)
    await db.commit()

async def create_scan_task(
    db: AsyncSession,
    account_id: int,
    task_type: str,
    params: Dict[str, Any]
) -> str:
    """Create a scanning task"""
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

async def save_collected_uids(
    db: AsyncSession,
    account_id: int,
    uids: List[Dict[str, Any]],
    source: str,
    source_id: str
):
    """Save collected UIDs to database"""
    saved_count = 0
    
    for uid_data in uids:
        # Check if UID already exists
        result = await db.execute(
            select(FacebookID).where(FacebookID.uid == uid_data['uid'])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            fb_id = FacebookID(
                uid=uid_data['uid'],
                name=uid_data.get('name'),
                username=uid_data.get('username'),
                profile_url=uid_data.get('profile_url'),
                source=source,
                source_id=source_id,
                collected_by_account_id=account_id,
                created_at=datetime.now()
            )
            db.add(fb_id)
            saved_count += 1
    
    await db.commit()
    return saved_count

# ============================================
# SCANNING ENDPOINTS
# ============================================

@router.post("/scan-posts", response_model=ScanResponse)
async def scan_posts(
    scan_data: ScanPostsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Scan posts from profile/group/page and collect UIDs
    Sidebar task: scan-posts-action, scanned-posts
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == scan_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create scanning task
        task_id = await create_scan_task(
            db,
            scan_data.account_id,
            "scan_posts",
            {
                "source_type": scan_data.source_type,
                "source_id": scan_data.source_id,
                "scan_type": scan_data.scan_type,
                "max_posts": scan_data.max_posts,
                "collect_uids": scan_data.collect_uids
            }
        )
        
        # Log activity
        await log_activity(
            db,
            scan_data.account_id,
            "scan_posts",
            f"Started scanning posts from {scan_data.source_type} {scan_data.source_id}",
            "info"
        )
        
        return ScanResponse(
            success=True,
            message=f"Scanning {scan_data.max_posts} posts from {scan_data.source_type}",
            task_id=task_id,
            total_found=0,
            collection_status="pending"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning posts: {str(e)}")

@router.post("/scan-group-members", response_model=ScanResponse)
async def scan_group_members(
    scan_data: ScanGroupMembersRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Scan group members and collect UIDs
    Sidebar task: scanned-group-members
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == scan_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create scanning task
        task_id = await create_scan_task(
            db,
            scan_data.account_id,
            "scan_group_members",
            {
                "group_id": scan_data.group_id,
                "max_members": scan_data.max_members,
                "member_type": scan_data.member_type,
                "collect_profile_info": scan_data.collect_profile_info
            }
        )
        
        # Log activity
        await log_activity(
            db,
            scan_data.account_id,
            "scan_group_members",
            f"Started scanning members from group {scan_data.group_id}",
            "info"
        )
        
        return ScanResponse(
            success=True,
            message=f"Scanning up to {scan_data.max_members} members from group",
            task_id=task_id,
            total_found=0,
            collection_status="pending"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning group members: {str(e)}")

@router.post("/scan-followers", response_model=ScanResponse)
async def scan_followers(
    scan_data: ScanFollowersRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Scan followers from a profile
    Sidebar task: scanned-followers
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == scan_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create scanning task
        task_id = await create_scan_task(
            db,
            scan_data.account_id,
            "scan_followers",
            {
                "target_uid": scan_data.target_uid,
                "max_followers": scan_data.max_followers,
                "scan_depth": scan_data.scan_depth
            }
        )
        
        # Log activity
        await log_activity(
            db,
            scan_data.account_id,
            "scan_followers",
            f"Started scanning followers from profile {scan_data.target_uid}",
            "info"
        )
        
        return ScanResponse(
            success=True,
            message=f"Scanning up to {scan_data.max_followers} followers",
            task_id=task_id,
            total_found=0,
            collection_status="pending"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning followers: {str(e)}")

@router.post("/scan-recent-friends", response_model=ScanResponse)
async def scan_recent_friends(
    scan_data: ScanRecentFriendsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Scan recently added friends
    Sidebar task: scanned-recent-friends
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == scan_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Use account's own UID if target_uid not provided
        target_uid = scan_data.target_uid or account.uid
        
        # Create scanning task
        task_id = await create_scan_task(
            db,
            scan_data.account_id,
            "scan_recent_friends",
            {
                "target_uid": target_uid,
                "days_back": scan_data.days_back,
                "max_friends": scan_data.max_friends
            }
        )
        
        # Log activity
        await log_activity(
            db,
            scan_data.account_id,
            "scan_recent_friends",
            f"Started scanning recent friends from last {scan_data.days_back} days",
            "info"
        )
        
        return ScanResponse(
            success=True,
            message=f"Scanning friends added in last {scan_data.days_back} days",
            task_id=task_id,
            total_found=0,
            collection_status="pending"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning recent friends: {str(e)}")

@router.post("/scan-friend-suggestions", response_model=ScanResponse)
async def scan_friend_suggestions(
    scan_data: ScanFriendSuggestionsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Scan friend suggestions
    Sidebar task: scanned-friend-suggestions
    """
    try:
        # Verify account exists
        result = await db.execute(select(Account).where(Account.id == scan_data.account_id))
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create scanning task
        task_id = await create_scan_task(
            db,
            scan_data.account_id,
            "scan_friend_suggestions",
            {
                "max_suggestions": scan_data.max_suggestions,
                "filter_mutual_friends": scan_data.filter_mutual_friends,
                "min_mutual_friends": scan_data.min_mutual_friends
            }
        )
        
        # Log activity
        await log_activity(
            db,
            scan_data.account_id,
            "scan_friend_suggestions",
            f"Started scanning up to {scan_data.max_suggestions} friend suggestions",
            "info"
        )
        
        return ScanResponse(
            success=True,
            message=f"Scanning up to {scan_data.max_suggestions} friend suggestions",
            task_id=task_id,
            total_found=0,
            collection_status="pending"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning suggestions: {str(e)}")

@router.get("/stats", response_model=ScanStats)
async def get_scanning_stats(
    account_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get scanning statistics"""
    try:
        # Get today's date
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count scans today
        query = select(func.count(Task.id)).where(
            Task.created_at >= today,
            Task.task_type.in_([
                'scan_posts', 'scan_group_members', 'scan_followers',
                'scan_recent_friends', 'scan_friend_suggestions'
            ])
        )
        
        if account_id:
            query = query.where(Task.account_id == account_id)
        
        result = await db.execute(query)
        total_scans = result.scalar() or 0
        
        # Count total UIDs collected
        uid_query = select(func.count(FacebookID.id))
        if account_id:
            uid_query = uid_query.where(FacebookID.collected_by_account_id == account_id)
        
        uid_result = await db.execute(uid_query)
        total_uids = uid_result.scalar() or 0
        
        # Get recent scans
        recent_query = select(Task).where(
            Task.task_type.in_([
                'scan_posts', 'scan_group_members', 'scan_followers',
                'scan_recent_friends', 'scan_friend_suggestions'
            ])
        ).order_by(Task.created_at.desc()).limit(10)
        
        if account_id:
            recent_query = recent_query.where(Task.account_id == account_id)
        
        recent_result = await db.execute(recent_query)
        recent_tasks = recent_result.scalars().all()
        
        recent_scans = [
            {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": task.status,
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
            for task in recent_tasks
        ]
        
        return ScanStats(
            total_scans_today=total_scans,
            posts_scanned_today=0,  # TODO: Implement detailed counting
            members_scanned_today=0,
            followers_scanned_today=0,
            total_uids_collected=total_uids,
            recent_scans=recent_scans
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@router.get("/collected-uids", response_model=List[Dict[str, Any]])
async def get_collected_uids(
    source: Optional[str] = None,
    account_id: Optional[int] = None,
    limit: int = 100,
    skip: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get list of collected UIDs from scanning"""
    try:
        query = select(FacebookID).order_by(FacebookID.created_at.desc())
        
        if source:
            query = query.where(FacebookID.source == source)
        
        if account_id:
            query = query.where(FacebookID.collected_by_account_id == account_id)
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        uids = result.scalars().all()
        
        return [
            {
                "id": uid.id,
                "uid": uid.uid,
                "name": uid.name,
                "username": uid.username,
                "source": uid.source,
                "source_id": uid.source_id,
                "created_at": uid.created_at.isoformat() if uid.created_at else None
            }
            for uid in uids
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching UIDs: {str(e)}")
