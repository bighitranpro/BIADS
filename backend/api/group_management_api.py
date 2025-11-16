"""
Group Management API

Handles Facebook group operations: join, leave, post, scan members.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from core.database import get_db, Account
from services.activity_logger import ActivityLogger

router = APIRouter(prefix="/api/groups", tags=["Group Management"])

# Pydantic Models
class GroupAction(BaseModel):
    account_id: int
    group_id: str = Field(..., description="Facebook group ID")
    group_name: Optional[str] = None

class BulkGroupAction(BaseModel):
    account_id: int
    group_ids: List[str] = Field(..., min_items=1)
    delay_min: int = Field(5, ge=1)
    delay_max: int = Field(15, ge=1)

class GroupPostCreate(BaseModel):
    account_id: int
    group_id: str
    content: str = Field(..., min_length=1)
    image_urls: List[str] = []
    schedule_time: Optional[datetime] = None

class GroupMemberScan(BaseModel):
    account_id: int
    group_id: str
    limit: int = Field(100, ge=1, le=1000)
    save_to_db: bool = True

class GroupStats(BaseModel):
    total_groups_joined: int
    total_groups_pending: int
    posts_in_groups_today: int
    members_scanned: int
    active_group_tasks: int

# Endpoints

@router.post("/join", response_model=dict)
async def join_group(action: GroupAction, db: AsyncSession = Depends(get_db)):
    """Join a Facebook group"""
    try:
        account = await db.execute(select(Account).where(Account.id == action.account_id))
        if not account.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Account not found")
        
        task_id = f"join_group_{action.account_id}_{int(datetime.now().timestamp())}"
        
        await ActivityLogger.log_activity(
            db=db, account_id=action.account_id, action="join_group",
            message=f"Joining group {action.group_id}", level="info",
            extra_data={"group_id": action.group_id, "task_id": task_id}
        )
        
        return {"success": True, "message": "Join group task created", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/leave", response_model=dict)
async def leave_group(action: GroupAction, db: AsyncSession = Depends(get_db)):
    """Leave a Facebook group"""
    try:
        account = await db.execute(select(Account).where(Account.id == action.account_id))
        if not account.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Account not found")
        
        await ActivityLogger.log_activity(
            db=db, account_id=action.account_id, action="leave_group",
            message=f"Left group {action.group_id}", level="warning"
        )
        
        return {"success": True, "message": f"Successfully left group {action.group_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/join-bulk", response_model=dict)
async def join_groups_bulk(action: BulkGroupAction, db: AsyncSession = Depends(get_db)):
    """Join multiple groups"""
    try:
        account = await db.execute(select(Account).where(Account.id == action.account_id))
        if not account.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Account not found")
        
        task_id = f"join_groups_bulk_{action.account_id}_{int(datetime.now().timestamp())}"
        
        await ActivityLogger.log_activity(
            db=db, account_id=action.account_id, action="join_groups_bulk",
            message=f"Bulk joining {len(action.group_ids)} groups", level="info",
            extra_data={"total_groups": len(action.group_ids), "task_id": task_id}
        )
        
        return {
            "success": True,
            "message": f"Bulk join task created for {len(action.group_ids)} groups",
            "task_id": task_id,
            "total_groups": len(action.group_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/post", response_model=dict)
async def post_to_group(post_data: GroupPostCreate, db: AsyncSession = Depends(get_db)):
    """Post content to a group"""
    try:
        account = await db.execute(select(Account).where(Account.id == post_data.account_id))
        if not account.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Account not found")
        
        task_id = f"group_post_{post_data.account_id}_{int(datetime.now().timestamp())}"
        
        await ActivityLogger.log_activity(
            db=db, account_id=post_data.account_id, action="post_to_group",
            message=f"Posting to group {post_data.group_id}", level="info",
            extra_data={"group_id": post_data.group_id, "task_id": task_id}
        )
        
        return {
            "success": True,
            "message": "Group post task created",
            "task_id": task_id,
            "scheduled": post_data.schedule_time is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scan-members", response_model=dict)
async def scan_group_members(scan_data: GroupMemberScan, db: AsyncSession = Depends(get_db)):
    """Scan and collect group members"""
    try:
        account = await db.execute(select(Account).where(Account.id == scan_data.account_id))
        if not account.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Account not found")
        
        task_id = f"scan_members_{scan_data.account_id}_{int(datetime.now().timestamp())}"
        
        await ActivityLogger.log_activity(
            db=db, account_id=scan_data.account_id, action="scan_group_members",
            message=f"Scanning members from group {scan_data.group_id}", level="info",
            extra_data={"group_id": scan_data.group_id, "limit": scan_data.limit, "task_id": task_id}
        )
        
        return {
            "success": True,
            "message": "Member scan task created",
            "task_id": task_id,
            "limit": scan_data.limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=GroupStats)
async def get_group_stats(
    account_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get group management statistics"""
    try:
        return GroupStats(
            total_groups_joined=0,
            total_groups_pending=0,
            posts_in_groups_today=0,
            members_scanned=0,
            active_group_tasks=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
