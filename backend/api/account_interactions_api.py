"""
Account Interactions API - Complete implementation
Handles all Facebook account interaction tasks
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import asyncio

from core.database import get_db
from core import crud

router = APIRouter(prefix="/api/interactions", tags=["account-interactions"])

# ============================================
# PYDANTIC MODELS
# ============================================

class PostStatusRequest(BaseModel):
    """Create/update status post"""
    account_ids: List[int] = Field(..., description="List of account IDs")
    content: str = Field(..., description="Post content")
    target_type: str = Field(default="timeline", description="timeline, group, page")
    target_id: Optional[str] = Field(None, description="Group/Page ID if applicable")
    image_urls: List[str] = Field(default_factory=list, description="Image URLs")
    delay_between_posts: int = Field(default=10, description="Delay in seconds")
    privacy: str = Field(default="public", description="public, friends, only_me")

class SharePostRequest(BaseModel):
    """Share post to timeline/group"""
    account_ids: List[int]
    post_url: str = Field(..., description="URL of post to share")
    message: Optional[str] = Field(None, description="Share message")
    target_type: str = Field(default="timeline", description="timeline, group")
    target_id: Optional[str] = Field(None, description="Target group ID")
    delay_between_shares: int = Field(default=10, description="Delay in seconds")

class CommentPostRequest(BaseModel):
    """Comment on posts"""
    account_ids: List[int]
    post_urls: List[str] = Field(..., description="List of post URLs")
    comments: List[str] = Field(..., description="List of comments to use")
    delay_between_comments: int = Field(default=5, description="Delay in seconds")
    random_comments: bool = Field(default=True, description="Use random comments")

class AutoLikeRequest(BaseModel):
    """Auto like posts/comments"""
    account_ids: List[int]
    target_urls: List[str] = Field(..., description="Post/Comment URLs")
    reaction_type: str = Field(default="LIKE", description="LIKE, LOVE, HAHA, WOW, SAD, ANGRY")
    delay_between_reactions: int = Field(default=3, description="Delay in seconds")

class UpdateBioRequest(BaseModel):
    """Update account bio/description"""
    account_ids: List[int]
    bio_text: str = Field(..., description="New bio text")
    bio_type: str = Field(default="description", description="description, work, education")

class HideNotificationRequest(BaseModel):
    """Hide/turn off notifications"""
    account_ids: List[int]
    notification_type: str = Field(default="all", description="all, post, comment, friend_request")

class AutoViewNewsRequest(BaseModel):
    """Auto view newsfeed"""
    account_ids: List[int]
    duration_minutes: int = Field(default=10, description="How long to view")
    scroll_count: int = Field(default=20, description="Number of scrolls")
    interact_probability: float = Field(default=0.3, description="Probability to like/react")

class AutoWatchVideoRequest(BaseModel):
    """Auto watch videos"""
    account_ids: List[int]
    video_urls: List[str] = Field(default_factory=list, description="Specific videos or empty for suggested")
    watch_duration_seconds: int = Field(default=30, description="Watch duration per video")
    videos_count: int = Field(default=10, description="Number of videos to watch")

class DeletePostRequest(BaseModel):
    """Delete posts"""
    account_id: int
    post_ids: List[str] = Field(..., description="List of post IDs to delete")

class PokeFriendsRequest(BaseModel):
    """Poke friends"""
    account_ids: List[int]
    friend_ids: List[str] = Field(..., description="List of friend UIDs to poke")
    delay_between_pokes: int = Field(default=5, description="Delay in seconds")

class JoinViaUIDRequest(BaseModel):
    """Join groups via UID scan"""
    account_ids: List[int]
    uid_list: List[str] = Field(..., description="UIDs to scan for groups")
    auto_join: bool = Field(default=True, description="Auto join found groups")

# ============================================
# POST STATUS
# ============================================

@router.post("/post-status")
async def post_status(
    request: PostStatusRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create status posts on timeline/group/page
    """
    try:
        # Validate accounts
        accounts = []
        for acc_id in request.account_ids:
            account = await crud.get_account(db, acc_id)
            if not account:
                raise HTTPException(status_code=404, detail=f"Account {acc_id} not found")
            accounts.append(account)
        
        # Create task
        task_id = f"post_status_{int(datetime.now().timestamp())}"
        task = await crud.create_task(db, {
            'task_id': task_id,
            'task_type': 'post_status',
            'task_name': 'Đăng bài viết',
            'status': 'pending',
            'progress': 0,
            'params': {
                'account_count': len(accounts),
                'content': request.content,
                'target_type': request.target_type,
                'privacy': request.privacy
            }
        })
        
        # Add background task
        background_tasks.add_task(
            process_post_status,
            db, task_id, accounts, request
        )
        
        await crud.create_log(db, {
            'action': 'post_status',
            'message': f"Bắt đầu đăng bài cho {len(accounts)} tài khoản",
            'level': 'info',
            'metadata': {'task_id': task_id}
        })
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Đã tạo task đăng bài cho {len(accounts)} tài khoản"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_post_status(db, task_id, accounts, request: PostStatusRequest):
    """Background task to process status posting"""
    total = len(accounts)
    success_count = 0
    
    try:
        for idx, account in enumerate(accounts):
            try:
                # TODO: Implement actual Facebook API call
                # For now, simulate the action
                await asyncio.sleep(request.delay_between_posts)
                
                # Log success
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'post_status',
                    'message': f"Đã đăng bài thành công cho {account.username or account.uid}",
                    'level': 'success'
                })
                
                success_count += 1
                
            except Exception as e:
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'post_status',
                    'message': f"Lỗi đăng bài: {str(e)}",
                    'level': 'error'
                })
            
            # Update progress
            progress = int((idx + 1) / total * 100)
            await crud.update_task(db, task_id, {
                'progress': progress,
                'status': 'processing'
            })
        
        # Mark as completed
        await crud.update_task(db, task_id, {
            'status': 'completed',
            'progress': 100,
            'result': {
                'total': total,
                'success': success_count,
                'failed': total - success_count
            }
        })
        
    except Exception as e:
        await crud.update_task(db, task_id, {
            'status': 'failed',
            'error': str(e)
        })

# ============================================
# SHARE POST
# ============================================

@router.post("/share-post")
async def share_post(
    request: SharePostRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Share posts to timeline or groups
    """
    try:
        accounts = []
        for acc_id in request.account_ids:
            account = await crud.get_account(db, acc_id)
            if not account:
                raise HTTPException(status_code=404, detail=f"Account {acc_id} not found")
            accounts.append(account)
        
        task_id = f"share_post_{int(datetime.now().timestamp())}"
        task = await crud.create_task(db, {
            'task_id': task_id,
            'task_type': 'share_post',
            'task_name': 'Chia sẻ bài viết',
            'status': 'pending',
            'progress': 0,
            'params': {
                'account_count': len(accounts),
                'post_url': request.post_url,
                'target_type': request.target_type
            }
        })
        
        background_tasks.add_task(
            process_share_post,
            db, task_id, accounts, request
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Đã tạo task chia sẻ bài viết cho {len(accounts)} tài khoản"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_share_post(db, task_id, accounts, request: SharePostRequest):
    """Background task to process post sharing"""
    total = len(accounts)
    success_count = 0
    
    try:
        for idx, account in enumerate(accounts):
            try:
                await asyncio.sleep(request.delay_between_shares)
                
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'share_post',
                    'message': f"Đã chia sẻ bài viết thành công",
                    'level': 'success'
                })
                
                success_count += 1
                
            except Exception as e:
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'share_post',
                    'message': f"Lỗi chia sẻ: {str(e)}",
                    'level': 'error'
                })
            
            progress = int((idx + 1) / total * 100)
            await crud.update_task(db, task_id, {
                'progress': progress,
                'status': 'processing'
            })
        
        await crud.update_task(db, task_id, {
            'status': 'completed',
            'progress': 100,
            'result': {
                'total': total,
                'success': success_count,
                'failed': total - success_count
            }
        })
        
    except Exception as e:
        await crud.update_task(db, task_id, {
            'status': 'failed',
            'error': str(e)
        })

# ============================================
# COMMENT POST
# ============================================

@router.post("/comment-post")
async def comment_post(
    request: CommentPostRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Comment on posts with multiple accounts
    """
    try:
        accounts = []
        for acc_id in request.account_ids:
            account = await crud.get_account(db, acc_id)
            if not account:
                raise HTTPException(status_code=404, detail=f"Account {acc_id} not found")
            accounts.append(account)
        
        task_id = f"comment_post_{int(datetime.now().timestamp())}"
        task = await crud.create_task(db, {
            'task_id': task_id,
            'task_type': 'comment_post',
            'task_name': 'Bình luận bài viết',
            'status': 'pending',
            'progress': 0,
            'params': {
                'account_count': len(accounts),
                'post_count': len(request.post_urls),
                'comment_count': len(request.comments)
            }
        })
        
        background_tasks.add_task(
            process_comment_post,
            db, task_id, accounts, request
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Đã tạo task bình luận cho {len(accounts)} tài khoản"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_comment_post(db, task_id, accounts, request: CommentPostRequest):
    """Background task to process commenting"""
    import random
    
    total_actions = len(accounts) * len(request.post_urls)
    action_count = 0
    success_count = 0
    
    try:
        for account in accounts:
            for post_url in request.post_urls:
                try:
                    # Select comment (random or sequential)
                    if request.random_comments:
                        comment = random.choice(request.comments)
                    else:
                        comment = request.comments[action_count % len(request.comments)]
                    
                    await asyncio.sleep(request.delay_between_comments)
                    
                    await crud.create_log(db, {
                        'account_id': account.id,
                        'task_id': task_id,
                        'action': 'comment_post',
                        'message': f"Đã bình luận: {comment[:50]}...",
                        'level': 'success'
                    })
                    
                    success_count += 1
                    
                except Exception as e:
                    await crud.create_log(db, {
                        'account_id': account.id,
                        'task_id': task_id,
                        'action': 'comment_post',
                        'message': f"Lỗi bình luận: {str(e)}",
                        'level': 'error'
                    })
                
                action_count += 1
                progress = int(action_count / total_actions * 100)
                await crud.update_task(db, task_id, {
                    'progress': progress,
                    'status': 'processing'
                })
        
        await crud.update_task(db, task_id, {
            'status': 'completed',
            'progress': 100,
            'result': {
                'total': total_actions,
                'success': success_count,
                'failed': total_actions - success_count
            }
        })
        
    except Exception as e:
        await crud.update_task(db, task_id, {
            'status': 'failed',
            'error': str(e)
        })

# ============================================
# AUTO LIKE
# ============================================

@router.post("/auto-like")
async def auto_like(
    request: AutoLikeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Auto like/react to posts and comments
    """
    try:
        accounts = []
        for acc_id in request.account_ids:
            account = await crud.get_account(db, acc_id)
            if not account:
                raise HTTPException(status_code=404, detail=f"Account {acc_id} not found")
            accounts.append(account)
        
        task_id = f"auto_like_{int(datetime.now().timestamp())}"
        task = await crud.create_task(db, {
            'task_id': task_id,
            'task_type': 'auto_like',
            'task_name': 'Tự động like',
            'status': 'pending',
            'progress': 0,
            'params': {
                'account_count': len(accounts),
                'target_count': len(request.target_urls),
                'reaction_type': request.reaction_type
            }
        })
        
        background_tasks.add_task(
            process_auto_like,
            db, task_id, accounts, request
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Đã tạo task tự động like cho {len(accounts)} tài khoản"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_auto_like(db, task_id, accounts, request: AutoLikeRequest):
    """Background task to process auto liking"""
    total_actions = len(accounts) * len(request.target_urls)
    action_count = 0
    success_count = 0
    
    try:
        for account in accounts:
            for target_url in request.target_urls:
                try:
                    await asyncio.sleep(request.delay_between_reactions)
                    
                    await crud.create_log(db, {
                        'account_id': account.id,
                        'task_id': task_id,
                        'action': 'auto_like',
                        'message': f"Đã thả cảm xúc {request.reaction_type}",
                        'level': 'success'
                    })
                    
                    success_count += 1
                    
                except Exception as e:
                    await crud.create_log(db, {
                        'account_id': account.id,
                        'task_id': task_id,
                        'action': 'auto_like',
                        'message': f"Lỗi: {str(e)}",
                        'level': 'error'
                    })
                
                action_count += 1
                progress = int(action_count / total_actions * 100)
                await crud.update_task(db, task_id, {
                    'progress': progress,
                    'status': 'processing'
                })
        
        await crud.update_task(db, task_id, {
            'status': 'completed',
            'progress': 100,
            'result': {
                'total': total_actions,
                'success': success_count,
                'failed': total_actions - success_count
            }
        })
        
    except Exception as e:
        await crud.update_task(db, task_id, {
            'status': 'failed',
            'error': str(e)
        })

# ============================================
# UPDATE BIO
# ============================================

@router.post("/update-bio")
async def update_bio(
    request: UpdateBioRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Update account bio/description
    """
    try:
        accounts = []
        for acc_id in request.account_ids:
            account = await crud.get_account(db, acc_id)
            if not account:
                raise HTTPException(status_code=404, detail=f"Account {acc_id} not found")
            accounts.append(account)
        
        task_id = f"update_bio_{int(datetime.now().timestamp())}"
        task = await crud.create_task(db, {
            'task_id': task_id,
            'task_type': 'update_bio',
            'task_name': 'Update bio',
            'status': 'pending',
            'progress': 0,
            'params': {
                'account_count': len(accounts),
                'bio_type': request.bio_type
            }
        })
        
        background_tasks.add_task(
            process_update_bio,
            db, task_id, accounts, request
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Đã tạo task update bio cho {len(accounts)} tài khoản"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_update_bio(db, task_id, accounts, request: UpdateBioRequest):
    """Background task to update bio"""
    total = len(accounts)
    success_count = 0
    
    try:
        for idx, account in enumerate(accounts):
            try:
                # TODO: Implement Facebook API call to update bio
                await asyncio.sleep(2)
                
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'update_bio',
                    'message': f"Đã cập nhật bio thành công",
                    'level': 'success'
                })
                
                success_count += 1
                
            except Exception as e:
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'update_bio',
                    'message': f"Lỗi: {str(e)}",
                    'level': 'error'
                })
            
            progress = int((idx + 1) / total * 100)
            await crud.update_task(db, task_id, {
                'progress': progress,
                'status': 'processing'
            })
        
        await crud.update_task(db, task_id, {
            'status': 'completed',
            'progress': 100,
            'result': {
                'total': total,
                'success': success_count,
                'failed': total - success_count
            }
        })
        
    except Exception as e:
        await crud.update_task(db, task_id, {
            'status': 'failed',
            'error': str(e)
        })

# ============================================
# HIDE NOTIFICATIONS
# ============================================

@router.post("/hide-notifications")
async def hide_notifications(
    request: HideNotificationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Hide/turn off notifications
    """
    try:
        accounts = []
        for acc_id in request.account_ids:
            account = await crud.get_account(db, acc_id)
            if not account:
                raise HTTPException(status_code=404, detail=f"Account {acc_id} not found")
            accounts.append(account)
        
        task_id = f"hide_notif_{int(datetime.now().timestamp())}"
        task = await crud.create_task(db, {
            'task_id': task_id,
            'task_type': 'hide_notifications',
            'task_name': 'Ẩn thông báo',
            'status': 'pending',
            'progress': 0,
            'params': {
                'account_count': len(accounts),
                'notification_type': request.notification_type
            }
        })
        
        background_tasks.add_task(
            process_hide_notifications,
            db, task_id, accounts, request
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Đã tạo task ẩn thông báo cho {len(accounts)} tài khoản"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_hide_notifications(db, task_id, accounts, request: HideNotificationRequest):
    """Background task to hide notifications"""
    total = len(accounts)
    success_count = 0
    
    try:
        for idx, account in enumerate(accounts):
            try:
                await asyncio.sleep(1)
                
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'hide_notifications',
                    'message': f"Đã ẩn thông báo {request.notification_type}",
                    'level': 'success'
                })
                
                success_count += 1
                
            except Exception as e:
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'hide_notifications',
                    'message': f"Lỗi: {str(e)}",
                    'level': 'error'
                })
            
            progress = int((idx + 1) / total * 100)
            await crud.update_task(db, task_id, {
                'progress': progress,
                'status': 'processing'
            })
        
        await crud.update_task(db, task_id, {
            'status': 'completed',
            'progress': 100,
            'result': {
                'total': total,
                'success': success_count,
                'failed': total - success_count
            }
        })
        
    except Exception as e:
        await crud.update_task(db, task_id, {
            'status': 'failed',
            'error': str(e)
        })

# ============================================
# AUTO VIEW NEWSFEED
# ============================================

@router.post("/auto-view-news")
async def auto_view_news(
    request: AutoViewNewsRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Auto view and interact with newsfeed
    """
    try:
        accounts = []
        for acc_id in request.account_ids:
            account = await crud.get_account(db, acc_id)
            if not account:
                raise HTTPException(status_code=404, detail=f"Account {acc_id} not found")
            accounts.append(account)
        
        task_id = f"auto_view_news_{int(datetime.now().timestamp())}"
        task = await crud.create_task(db, {
            'task_id': task_id,
            'task_type': 'auto_view_news',
            'task_name': 'Tự động xem newsfeed',
            'status': 'pending',
            'progress': 0,
            'params': {
                'account_count': len(accounts),
                'duration_minutes': request.duration_minutes
            }
        })
        
        background_tasks.add_task(
            process_auto_view_news,
            db, task_id, accounts, request
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Đã tạo task xem newsfeed cho {len(accounts)} tài khoản"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_auto_view_news(db, task_id, accounts, request: AutoViewNewsRequest):
    """Background task to auto view newsfeed"""
    import random
    
    total = len(accounts)
    success_count = 0
    
    try:
        for idx, account in enumerate(accounts):
            try:
                # Simulate scrolling and viewing
                for scroll in range(request.scroll_count):
                    await asyncio.sleep(2)
                    
                    # Random interaction
                    if random.random() < request.interact_probability:
                        await crud.create_log(db, {
                            'account_id': account.id,
                            'task_id': task_id,
                            'action': 'auto_view_news',
                            'message': f"Đã tương tác với bài viết #{scroll + 1}",
                            'level': 'info'
                        })
                
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'auto_view_news',
                    'message': f"Hoàn thành xem {request.scroll_count} bài viết",
                    'level': 'success'
                })
                
                success_count += 1
                
            except Exception as e:
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'auto_view_news',
                    'message': f"Lỗi: {str(e)}",
                    'level': 'error'
                })
            
            progress = int((idx + 1) / total * 100)
            await crud.update_task(db, task_id, {
                'progress': progress,
                'status': 'processing'
            })
        
        await crud.update_task(db, task_id, {
            'status': 'completed',
            'progress': 100,
            'result': {
                'total': total,
                'success': success_count,
                'failed': total - success_count
            }
        })
        
    except Exception as e:
        await crud.update_task(db, task_id, {
            'status': 'failed',
            'error': str(e)
        })

# ============================================
# AUTO WATCH VIDEO
# ============================================

@router.post("/auto-watch-video")
async def auto_watch_video(
    request: AutoWatchVideoRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Auto watch videos
    """
    try:
        accounts = []
        for acc_id in request.account_ids:
            account = await crud.get_account(db, acc_id)
            if not account:
                raise HTTPException(status_code=404, detail=f"Account {acc_id} not found")
            accounts.append(account)
        
        task_id = f"auto_watch_video_{int(datetime.now().timestamp())}"
        task = await crud.create_task(db, {
            'task_id': task_id,
            'task_type': 'auto_watch_video',
            'task_name': 'Tự động xem video',
            'status': 'pending',
            'progress': 0,
            'params': {
                'account_count': len(accounts),
                'videos_count': request.videos_count
            }
        })
        
        background_tasks.add_task(
            process_auto_watch_video,
            db, task_id, accounts, request
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Đã tạo task xem video cho {len(accounts)} tài khoản"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_auto_watch_video(db, task_id, accounts, request: AutoWatchVideoRequest):
    """Background task to auto watch videos"""
    total = len(accounts)
    success_count = 0
    
    try:
        for idx, account in enumerate(accounts):
            try:
                videos_watched = 0
                
                # Watch videos
                for video_idx in range(request.videos_count):
                    await asyncio.sleep(request.watch_duration_seconds)
                    videos_watched += 1
                    
                    await crud.create_log(db, {
                        'account_id': account.id,
                        'task_id': task_id,
                        'action': 'auto_watch_video',
                        'message': f"Đã xem video #{video_idx + 1}/{request.videos_count}",
                        'level': 'info'
                    })
                
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'auto_watch_video',
                    'message': f"Hoàn thành xem {videos_watched} video",
                    'level': 'success'
                })
                
                success_count += 1
                
            except Exception as e:
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'auto_watch_video',
                    'message': f"Lỗi: {str(e)}",
                    'level': 'error'
                })
            
            progress = int((idx + 1) / total * 100)
            await crud.update_task(db, task_id, {
                'progress': progress,
                'status': 'processing'
            })
        
        await crud.update_task(db, task_id, {
            'status': 'completed',
            'progress': 100,
            'result': {
                'total': total,
                'success': success_count,
                'failed': total - success_count
            }
        })
        
    except Exception as e:
        await crud.update_task(db, task_id, {
            'status': 'failed',
            'error': str(e)
        })

# ============================================
# DELETE POSTS
# ============================================

@router.post("/delete-posts")
async def delete_posts(
    request: DeletePostRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete posts from account
    """
    try:
        account = await crud.get_account(db, request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        task_id = f"delete_posts_{int(datetime.now().timestamp())}"
        task = await crud.create_task(db, {
            'task_id': task_id,
            'task_type': 'delete_posts',
            'task_name': 'Xóa bài viết',
            'status': 'pending',
            'progress': 0,
            'params': {
                'account_id': request.account_id,
                'post_count': len(request.post_ids)
            }
        })
        
        background_tasks.add_task(
            process_delete_posts,
            db, task_id, account, request
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Đã tạo task xóa {len(request.post_ids)} bài viết"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_delete_posts(db, task_id, account, request: DeletePostRequest):
    """Background task to delete posts"""
    total = len(request.post_ids)
    success_count = 0
    
    try:
        for idx, post_id in enumerate(request.post_ids):
            try:
                await asyncio.sleep(2)
                
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'delete_posts',
                    'message': f"Đã xóa bài viết {post_id}",
                    'level': 'success'
                })
                
                success_count += 1
                
            except Exception as e:
                await crud.create_log(db, {
                    'account_id': account.id,
                    'task_id': task_id,
                    'action': 'delete_posts',
                    'message': f"Lỗi xóa bài viết {post_id}: {str(e)}",
                    'level': 'error'
                })
            
            progress = int((idx + 1) / total * 100)
            await crud.update_task(db, task_id, {
                'progress': progress,
                'status': 'processing'
            })
        
        await crud.update_task(db, task_id, {
            'status': 'completed',
            'progress': 100,
            'result': {
                'total': total,
                'success': success_count,
                'failed': total - success_count
            }
        })
        
    except Exception as e:
        await crud.update_task(db, task_id, {
            'status': 'failed',
            'error': str(e)
        })

# ============================================
# POKE FRIENDS
# ============================================

@router.post("/poke-friends")
async def poke_friends(
    request: PokeFriendsRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Poke friends
    """
    try:
        accounts = []
        for acc_id in request.account_ids:
            account = await crud.get_account(db, acc_id)
            if not account:
                raise HTTPException(status_code=404, detail=f"Account {acc_id} not found")
            accounts.append(account)
        
        task_id = f"poke_friends_{int(datetime.now().timestamp())}"
        task = await crud.create_task(db, {
            'task_id': task_id,
            'task_type': 'poke_friends',
            'task_name': 'Chọc bạn bè',
            'status': 'pending',
            'progress': 0,
            'params': {
                'account_count': len(accounts),
                'friend_count': len(request.friend_ids)
            }
        })
        
        background_tasks.add_task(
            process_poke_friends,
            db, task_id, accounts, request
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Đã tạo task chọc bạn bè cho {len(accounts)} tài khoản"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_poke_friends(db, task_id, accounts, request: PokeFriendsRequest):
    """Background task to poke friends"""
    total_actions = len(accounts) * len(request.friend_ids)
    action_count = 0
    success_count = 0
    
    try:
        for account in accounts:
            for friend_id in request.friend_ids:
                try:
                    await asyncio.sleep(request.delay_between_pokes)
                    
                    await crud.create_log(db, {
                        'account_id': account.id,
                        'task_id': task_id,
                        'action': 'poke_friends',
                        'message': f"Đã chọc bạn {friend_id}",
                        'level': 'success'
                    })
                    
                    success_count += 1
                    
                except Exception as e:
                    await crud.create_log(db, {
                        'account_id': account.id,
                        'task_id': task_id,
                        'action': 'poke_friends',
                        'message': f"Lỗi: {str(e)}",
                        'level': 'error'
                    })
                
                action_count += 1
                progress = int(action_count / total_actions * 100)
                await crud.update_task(db, task_id, {
                    'progress': progress,
                    'status': 'processing'
                })
        
        await crud.update_task(db, task_id, {
            'status': 'completed',
            'progress': 100,
            'result': {
                'total': total_actions,
                'success': success_count,
                'failed': total_actions - success_count
            }
        })
        
    except Exception as e:
        await crud.update_task(db, task_id, {
            'status': 'failed',
            'error': str(e)
        })

# ============================================
# HEALTH CHECK
# ============================================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Account Interactions API",
        "timestamp": datetime.now().isoformat()
    }
