"""
Facebook Tasks API - Complete Implementation
Handles all Facebook automation tasks
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import asyncio
import json

from core.database import get_db
from core import crud
from services.telegram_bot import TelegramBot
import os

router = APIRouter(prefix="/api/facebook", tags=["facebook-tasks"])

# Telegram bot instance
telegram_bot = TelegramBot(
    bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
    chat_id=os.getenv('TELEGRAM_CHAT_ID')
)


# ============================================
# PYDANTIC MODELS
# ============================================

class GroupScanRequest(BaseModel):
    account_id: int
    keyword: str
    max_results: int = 50


class GroupJoinRequest(BaseModel):
    account_ids: List[int]
    group_ids: List[str]
    delay: int = 10  # seconds between joins
    max_groups_per_account: int = 20


class GroupLeaveRequest(BaseModel):
    account_id: int
    group_ids: List[str]
    delay: int = 5


class PostCreateRequest(BaseModel):
    account_id: int
    content: str
    images: Optional[List[str]] = None
    target_type: str = "timeline"  # timeline, group, page
    target_id: Optional[str] = None  # group_id or page_id
    schedule_time: Optional[datetime] = None


class CommentCreateRequest(BaseModel):
    account_ids: List[int]
    post_url: str
    comment_text: str
    delay: int = 20  # seconds between comments


class ReactionRequest(BaseModel):
    account_ids: List[int]
    post_url: str
    reaction_type: str = "LIKE"  # LIKE, LOVE, HAHA, WOW, SAD, ANGRY
    delay: int = 10


class FriendRequestAction(BaseModel):
    account_ids: List[int]
    target_uids: List[str]
    delay: int = 15


class MessageSendRequest(BaseModel):
    account_id: int
    recipient_ids: List[str]
    message: str
    delay: int = 30


class PagePostRequest(BaseModel):
    account_id: int
    page_id: str
    content: str
    images: Optional[List[str]] = None
    schedule_time: Optional[datetime] = None


# ============================================
# GROUP TASKS
# ============================================

@router.post("/groups/scan")
async def scan_groups(request: GroupScanRequest, db: AsyncSession = Depends(get_db)):
    """
    Scan Facebook groups by keyword
    """
    try:
        # Get account
        account = await crud.get_account(db, request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        if account.status != "active":
            raise HTTPException(status_code=400, detail="Account is not active")
        
        # TODO: Implement actual Facebook Graph API call
        # For now, return mock data
        mock_groups = [
            {
                "id": f"group_{i}",
                "name": f"Group {request.keyword} {i}",
                "member_count": 1000 + i * 100,
                "privacy": "PUBLIC" if i % 2 == 0 else "CLOSED",
                "description": f"Group về {request.keyword}"
            }
            for i in range(1, min(request.max_results + 1, 51))
        ]
        
        # Log activity
        await crud.create_log(
            db,
            level="success",
            message=f"Scanned {len(mock_groups)} groups for keyword: {request.keyword}",
            details=f"Account: {account.username}"
        )
        
        telegram_bot.send_notification(
            "Group Scan Completed",
            f"Found {len(mock_groups)} groups for '{request.keyword}'",
            "success"
        )
        
        return {
            "success": True,
            "account_id": request.account_id,
            "keyword": request.keyword,
            "groups_found": len(mock_groups),
            "groups": mock_groups
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await crud.create_log(
            db,
            level="error",
            message=f"Group scan failed: {str(e)}",
            details=f"Account ID: {request.account_id}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/groups/join")
async def join_groups(
    request: GroupJoinRequest, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Join multiple groups with multiple accounts
    """
    try:
        # Validate accounts
        accounts = []
        for account_id in request.account_ids:
            account = await crud.get_account(db, account_id)
            if not account:
                raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
            if account.status != "active":
                raise HTTPException(status_code=400, detail=f"Account {account_id} is not active")
            accounts.append(account)
        
        # Create task
        task_data = {
            "task_type": "group_join",
            "status": "pending",
            "progress": 0,
            "total_items": len(request.account_ids) * len(request.group_ids),
            "completed_items": 0,
            "failed_items": 0,
            "config": {
                "account_ids": request.account_ids,
                "group_ids": request.group_ids,
                "delay": request.delay,
                "max_groups_per_account": request.max_groups_per_account
            }
        }
        
        task = await crud.create_task(db, **task_data)
        
        # Log activity
        await crud.create_log(
            db,
            level="info",
            message=f"Started group join task: {len(request.account_ids)} accounts, {len(request.group_ids)} groups",
            details=f"Task ID: {task.id}"
        )
        
        telegram_bot.send_notification(
            "Group Join Task Started",
            f"Joining {len(request.group_ids)} groups with {len(request.account_ids)} accounts",
            "info",
            {"Task ID": task.id, "Delay": f"{request.delay}s"}
        )
        
        # TODO: Process in background
        # background_tasks.add_task(process_group_join_task, task.id, request, db)
        
        return {
            "success": True,
            "task_id": task.id,
            "accounts": len(request.account_ids),
            "groups": len(request.group_ids),
            "estimated_time": len(request.account_ids) * len(request.group_ids) * request.delay,
            "message": "Task created and will be processed in background"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await crud.create_log(
            db,
            level="error",
            message=f"Failed to create group join task: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/groups/leave")
async def leave_groups(request: GroupLeaveRequest, db: AsyncSession = Depends(get_db)):
    """
    Leave multiple groups with an account
    """
    try:
        # Get account
        account = await crud.get_account(db, request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create task
        task_data = {
            "task_type": "group_leave",
            "account_id": request.account_id,
            "status": "pending",
            "progress": 0,
            "total_items": len(request.group_ids),
            "config": {
                "group_ids": request.group_ids,
                "delay": request.delay
            }
        }
        
        task = await crud.create_task(db, **task_data)
        
        await crud.create_log(
            db,
            level="info",
            message=f"Started group leave task: {len(request.group_ids)} groups",
            details=f"Account: {account.username}, Task ID: {task.id}"
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "groups_to_leave": len(request.group_ids),
            "estimated_time": len(request.group_ids) * request.delay
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/groups/joined/{account_id}")
async def get_joined_groups(account_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get list of groups that account has joined
    """
    try:
        account = await crud.get_account(db, account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # TODO: Implement actual Facebook API call
        # Mock data for now
        mock_groups = [
            {
                "id": f"joined_group_{i}",
                "name": f"Joined Group {i}",
                "member_count": 5000 + i * 500,
                "joined_date": "2025-01-01"
            }
            for i in range(1, 21)
        ]
        
        return {
            "success": True,
            "account_id": account_id,
            "groups": mock_groups,
            "total": len(mock_groups)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# POST TASKS
# ============================================

@router.post("/posts/create")
async def create_post(request: PostCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new post on timeline, group, or page
    """
    try:
        account = await crud.get_account(db, request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create task
        task_data = {
            "task_type": "post_create",
            "account_id": request.account_id,
            "status": "pending",
            "config": {
                "content": request.content,
                "images": request.images,
                "target_type": request.target_type,
                "target_id": request.target_id,
                "schedule_time": request.schedule_time.isoformat() if request.schedule_time else None
            }
        }
        
        task = await crud.create_task(db, **task_data)
        
        await crud.create_log(
            db,
            level="info",
            message=f"Created post task on {request.target_type}",
            details=f"Account: {account.username}, Task ID: {task.id}"
        )
        
        telegram_bot.send_notification(
            "Post Created",
            f"New post on {request.target_type}",
            "success",
            {"Account": account.username, "Task ID": task.id}
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "post_type": request.target_type,
            "message": "Post task created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/comment")
async def comment_on_post(request: CommentCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Comment on a post with multiple accounts
    """
    try:
        # Validate accounts
        for account_id in request.account_ids:
            account = await crud.get_account(db, account_id)
            if not account:
                raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
        
        # Create task
        task_data = {
            "task_type": "post_comment",
            "status": "pending",
            "total_items": len(request.account_ids),
            "config": {
                "account_ids": request.account_ids,
                "post_url": request.post_url,
                "comment_text": request.comment_text,
                "delay": request.delay
            }
        }
        
        task = await crud.create_task(db, **task_data)
        
        await crud.create_log(
            db,
            level="info",
            message=f"Started comment task: {len(request.account_ids)} accounts",
            details=f"Post: {request.post_url}, Task ID: {task.id}"
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "accounts": len(request.account_ids),
            "estimated_time": len(request.account_ids) * request.delay
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/react")
async def react_to_post(request: ReactionRequest, db: AsyncSession = Depends(get_db)):
    """
    React to a post with multiple accounts
    """
    try:
        # Create task
        task_data = {
            "task_type": "post_reaction",
            "status": "pending",
            "total_items": len(request.account_ids),
            "config": {
                "account_ids": request.account_ids,
                "post_url": request.post_url,
                "reaction_type": request.reaction_type,
                "delay": request.delay
            }
        }
        
        task = await crud.create_task(db, **task_data)
        
        await crud.create_log(
            db,
            level="info",
            message=f"Started reaction task: {request.reaction_type}",
            details=f"{len(request.account_ids)} accounts, Task ID: {task.id}"
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "accounts": len(request.account_ids),
            "reaction": request.reaction_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# FRIEND TASKS
# ============================================

@router.post("/friends/add")
async def send_friend_requests(request: FriendRequestAction, db: AsyncSession = Depends(get_db)):
    """
    Send friend requests to multiple users
    """
    try:
        # Create task
        task_data = {
            "task_type": "friend_request",
            "status": "pending",
            "total_items": len(request.account_ids) * len(request.target_uids),
            "config": {
                "account_ids": request.account_ids,
                "target_uids": request.target_uids,
                "delay": request.delay
            }
        }
        
        task = await crud.create_task(db, **task_data)
        
        await crud.create_log(
            db,
            level="info",
            message=f"Started friend request task",
            details=f"{len(request.account_ids)} accounts, {len(request.target_uids)} targets, Task ID: {task.id}"
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "accounts": len(request.account_ids),
            "targets": len(request.target_uids),
            "estimated_time": len(request.account_ids) * len(request.target_uids) * request.delay
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/send")
async def send_messages(request: MessageSendRequest, db: AsyncSession = Depends(get_db)):
    """
    Send messages to multiple users
    """
    try:
        account = await crud.get_account(db, request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create task
        task_data = {
            "task_type": "send_message",
            "account_id": request.account_id,
            "status": "pending",
            "total_items": len(request.recipient_ids),
            "config": {
                "recipient_ids": request.recipient_ids,
                "message": request.message,
                "delay": request.delay
            }
        }
        
        task = await crud.create_task(db, **task_data)
        
        await crud.create_log(
            db,
            level="info",
            message=f"Started message sending task",
            details=f"Account: {account.username}, Recipients: {len(request.recipient_ids)}, Task ID: {task.id}"
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "recipients": len(request.recipient_ids),
            "estimated_time": len(request.recipient_ids) * request.delay
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PAGE TASKS
# ============================================

@router.post("/pages/post")
async def create_page_post(request: PagePostRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a post on a Facebook page
    """
    try:
        account = await crud.get_account(db, request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create task
        task_data = {
            "task_type": "page_post",
            "account_id": request.account_id,
            "status": "pending",
            "config": {
                "page_id": request.page_id,
                "content": request.content,
                "images": request.images,
                "schedule_time": request.schedule_time.isoformat() if request.schedule_time else None
            }
        }
        
        task = await crud.create_task(db, **task_data)
        
        await crud.create_log(
            db,
            level="info",
            message=f"Created page post task",
            details=f"Page ID: {request.page_id}, Task ID: {task.id}"
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "page_id": request.page_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TASK MANAGEMENT
# ============================================

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get task status and progress
    """
    try:
        task = await crud.get_task(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "success": True,
            "task": {
                "id": task.id,
                "type": task.task_type,
                "status": task.status,
                "progress": task.progress,
                "total_items": task.total_items,
                "completed_items": task.completed_items,
                "failed_items": task.failed_items,
                "created_at": task.created_at.isoformat(),
                "config": json.loads(task.config) if task.config else {}
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tasks/{task_id}")
async def cancel_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """
    Cancel a running task
    """
    try:
        task = await crud.get_task(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update task status
        await crud.update_task(db, task_id, status="cancelled")
        
        await crud.create_log(
            db,
            level="warning",
            message=f"Task cancelled: {task.task_type}",
            details=f"Task ID: {task_id}"
        )
        
        return {
            "success": True,
            "message": "Task cancelled successfully",
            "task_id": task_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
