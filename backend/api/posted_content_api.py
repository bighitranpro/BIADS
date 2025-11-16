"""
Posted Content API
REST endpoints for managing posted content with search and editing
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from core.database import get_db, PostedContent, Account
from services.activity_logger import ActivityLogger
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import re

router = APIRouter(prefix="/api/posted-content", tags=["Posted Content"])


# Pydantic Schemas
class PostedContentCreate(BaseModel):
    """Schema để tạo posted content mới"""
    post_id: str = Field(..., min_length=1, max_length=100, description="Post ID duy nhất")
    account_id: int = Field(..., description="Tài khoản đăng bài")
    content: Optional[str] = Field(None, description="Nội dung bài viết")
    post_url: Optional[str] = Field(None, max_length=500, description="URL bài viết")
    post_type: str = Field("text", description="Loại bài: text, image, video, link")
    like_count: int = Field(0, ge=0, description="Số lượt thích")
    comment_count: int = Field(0, ge=0, description="Số lượt comment")
    share_count: int = Field(0, ge=0, description="Số lượt share")
    status: str = Field("published", description="Trạng thái: published, hidden, deleted")


class PostedContentUpdate(BaseModel):
    """Schema để update posted content"""
    content: Optional[str] = None
    post_url: Optional[str] = None
    post_type: Optional[str] = None
    like_count: Optional[int] = Field(None, ge=0)
    comment_count: Optional[int] = Field(None, ge=0)
    share_count: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None


class PostedContentResponse(BaseModel):
    """Schema response cho posted content"""
    id: int
    post_id: str
    account_id: int
    content: Optional[str]
    post_url: Optional[str]
    post_type: str
    like_count: int
    comment_count: int
    share_count: int
    status: str
    posted_at: str
    last_updated: str
    created_at: str
    account_info: Optional[Dict[str, Any]]


class PostedContentStats(BaseModel):
    """Schema cho thống kê posted content"""
    total_count: int
    published_count: int
    hidden_count: int
    deleted_count: int
    total_likes: int
    total_comments: int
    total_shares: int
    post_types: Dict[str, int]
    recent_24h: int
    top_engagement_rate: float


class SearchResult(BaseModel):
    """Schema cho search result với highlighting"""
    id: int
    post_id: str
    content: Optional[str]
    content_highlighted: Optional[str]
    post_url: Optional[str]
    like_count: int
    comment_count: int
    share_count: int
    engagement_rate: float
    posted_at: str
    account_name: Optional[str]
    match_score: float


# Helper Functions
def highlight_text(text: Optional[str], search_query: str) -> Optional[str]:
    """Highlight search query in text"""
    if not text or not search_query:
        return text
    
    # Escape special regex characters in search query
    escaped_query = re.escape(search_query)
    
    # Case-insensitive replacement with highlight tags
    pattern = re.compile(f'({escaped_query})', re.IGNORECASE)
    highlighted = pattern.sub(r'<mark>\1</mark>', text)
    
    return highlighted


def calculate_engagement_rate(post: PostedContent) -> float:
    """Calculate engagement rate based on likes, comments, shares"""
    total_engagement = post.like_count + (post.comment_count * 2) + (post.share_count * 3)
    # Simple engagement rate (can be improved with follower count)
    return round(total_engagement / 100.0, 2)


# API Endpoints

@router.get("/", response_model=List[PostedContentResponse])
async def get_posted_content(
    account_id: Optional[int] = Query(None, description="Filter by account"),
    post_type: Optional[str] = Query(None, description="Filter by post type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách posted content với filters
    
    Query params:
    - account_id: Filter theo tài khoản
    - post_type: Filter theo loại bài (text, image, video, link)
    - status: Filter theo trạng thái (published, hidden, deleted)
    - start_date: Filter từ ngày (ISO format)
    - end_date: Filter đến ngày (ISO format)
    - limit: Số lượng tối đa (default 100, max 1000)
    - offset: Bỏ qua bao nhiêu records (pagination)
    """
    try:
        # Build query với filters
        query = select(PostedContent)
        
        conditions = []
        if account_id:
            conditions.append(PostedContent.account_id == account_id)
        if post_type:
            conditions.append(PostedContent.post_type == post_type)
        if status:
            conditions.append(PostedContent.status == status)
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            conditions.append(PostedContent.posted_at >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            conditions.append(PostedContent.posted_at <= end_dt)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply pagination
        query = query.offset(offset).limit(limit).order_by(PostedContent.posted_at.desc())
        
        result = await db.execute(query)
        posts = result.scalars().all()
        
        # Format response với account info
        response_data = []
        for post in posts:
            # Get account info
            acc_query = select(Account).where(Account.id == post.account_id)
            acc_result = await db.execute(acc_query)
            acc = acc_result.scalar_one_or_none()
            
            account_info = None
            if acc:
                account_info = {
                    "id": acc.id,
                    "uid": acc.uid,
                    "name": acc.name,
                    "username": acc.username
                }
            
            response_data.append({
                "id": post.id,
                "post_id": post.post_id,
                "account_id": post.account_id,
                "content": post.content,
                "post_url": post.post_url,
                "post_type": post.post_type,
                "like_count": post.like_count,
                "comment_count": post.comment_count,
                "share_count": post.share_count,
                "status": post.status,
                "posted_at": post.posted_at.isoformat(),
                "last_updated": post.last_updated.isoformat(),
                "created_at": post.created_at.isoformat(),
                "account_info": account_info
            })
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching posted content: {str(e)}")


@router.get("/stats", response_model=PostedContentStats)
async def get_posted_content_stats(
    account_id: Optional[int] = Query(None, description="Stats for specific account"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy thống kê posted content
    
    Query params:
    - account_id: Thống kê cho tài khoản cụ thể (optional)
    """
    try:
        # Build base query
        base_query = select(PostedContent)
        if account_id:
            base_query = base_query.where(PostedContent.account_id == account_id)
        
        # Total count
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(total_query)
        total_count = total_result.scalar() or 0
        
        # Published count
        published_query = select(func.count()).select_from(
            base_query.where(PostedContent.status == 'published').subquery()
        )
        published_result = await db.execute(published_query)
        published_count = published_result.scalar() or 0
        
        # Hidden count
        hidden_query = select(func.count()).select_from(
            base_query.where(PostedContent.status == 'hidden').subquery()
        )
        hidden_result = await db.execute(hidden_query)
        hidden_count = hidden_result.scalar() or 0
        
        # Deleted count
        deleted_query = select(func.count()).select_from(
            base_query.where(PostedContent.status == 'deleted').subquery()
        )
        deleted_result = await db.execute(deleted_query)
        deleted_count = deleted_result.scalar() or 0
        
        # Total engagement
        likes_query = select(func.sum(PostedContent.like_count)).select_from(base_query.subquery())
        likes_result = await db.execute(likes_query)
        total_likes = likes_result.scalar() or 0
        
        comments_query = select(func.sum(PostedContent.comment_count)).select_from(base_query.subquery())
        comments_result = await db.execute(comments_query)
        total_comments = comments_result.scalar() or 0
        
        shares_query = select(func.sum(PostedContent.share_count)).select_from(base_query.subquery())
        shares_result = await db.execute(shares_query)
        total_shares = shares_result.scalar() or 0
        
        # Post types breakdown
        types_query = select(PostedContent.post_type, func.count()).where(
            PostedContent.account_id == account_id if account_id else True
        ).group_by(PostedContent.post_type)
        types_result = await db.execute(types_query)
        post_types = dict(types_result.all())
        
        # Recent 24h
        yesterday = datetime.now() - timedelta(days=1)
        recent_query = select(func.count()).select_from(
            base_query.where(PostedContent.posted_at >= yesterday).subquery()
        )
        recent_result = await db.execute(recent_query)
        recent_24h = recent_result.scalar() or 0
        
        # Top engagement rate
        top_engagement_rate = 0.0
        if total_count > 0:
            total_engagement = int(total_likes) + (int(total_comments) * 2) + (int(total_shares) * 3)
            top_engagement_rate = round(total_engagement / float(total_count), 2)
        
        return {
            "total_count": total_count,
            "published_count": published_count,
            "hidden_count": hidden_count,
            "deleted_count": deleted_count,
            "total_likes": int(total_likes),
            "total_comments": int(total_comments),
            "total_shares": int(total_shares),
            "post_types": post_types,
            "recent_24h": recent_24h,
            "top_engagement_rate": top_engagement_rate
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@router.get("/search", response_model=List[SearchResult])
async def search_posted_content(
    query: str = Query(..., min_length=1, description="Search query"),
    account_id: Optional[int] = Query(None, description="Filter by account"),
    limit: int = Query(50, ge=1, le=500, description="Max number of results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Tìm kiếm posted content với highlighting
    
    Query params:
    - query: Từ khóa tìm kiếm (bắt buộc)
    - account_id: Filter theo tài khoản (optional)
    - limit: Số lượng kết quả tối đa (default 50, max 500)
    
    Features:
    - Search trong nội dung bài viết
    - Highlight từ khóa trong kết quả
    - Tính engagement rate
    - Sắp xếp theo relevance score
    """
    try:
        # Build search query
        search_query = select(PostedContent)
        
        conditions = [
            PostedContent.content.ilike(f'%{query}%')
        ]
        
        if account_id:
            conditions.append(PostedContent.account_id == account_id)
        
        search_query = search_query.where(and_(*conditions)).limit(limit)
        
        result = await db.execute(search_query)
        posts = result.scalars().all()
        
        # Format results with highlighting
        search_results = []
        for post in posts:
            # Get account info
            acc_query = select(Account).where(Account.id == post.account_id)
            acc_result = await db.execute(acc_query)
            acc = acc_result.scalar_one_or_none()
            
            # Calculate match score (simple: count occurrences)
            match_count = post.content.lower().count(query.lower()) if post.content else 0
            match_score = min(match_count / 10.0, 1.0)  # Normalize to 0-1
            
            # Calculate engagement rate
            engagement_rate = calculate_engagement_rate(post)
            
            # Highlight text
            highlighted_content = highlight_text(post.content, query)
            
            search_results.append({
                "id": post.id,
                "post_id": post.post_id,
                "content": post.content,
                "content_highlighted": highlighted_content,
                "post_url": post.post_url,
                "like_count": post.like_count,
                "comment_count": post.comment_count,
                "share_count": post.share_count,
                "engagement_rate": engagement_rate,
                "posted_at": post.posted_at.isoformat(),
                "account_name": acc.name if acc else None,
                "match_score": match_score
            })
        
        # Sort by match score and engagement
        search_results.sort(key=lambda x: (x['match_score'], x['engagement_rate']), reverse=True)
        
        return search_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching content: {str(e)}")


@router.get("/{content_id}", response_model=PostedContentResponse)
async def get_posted_content_by_id(
    content_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Lấy thông tin chi tiết một posted content"""
    try:
        query = select(PostedContent).where(PostedContent.id == content_id)
        result = await db.execute(query)
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(status_code=404, detail="Posted content not found")
        
        # Get account info
        acc_query = select(Account).where(Account.id == post.account_id)
        acc_result = await db.execute(acc_query)
        acc = acc_result.scalar_one_or_none()
        
        account_info = None
        if acc:
            account_info = {
                "id": acc.id,
                "uid": acc.uid,
                "name": acc.name,
                "username": acc.username
            }
        
        return {
            "id": post.id,
            "post_id": post.post_id,
            "account_id": post.account_id,
            "content": post.content,
            "post_url": post.post_url,
            "post_type": post.post_type,
            "like_count": post.like_count,
            "comment_count": post.comment_count,
            "share_count": post.share_count,
            "status": post.status,
            "posted_at": post.posted_at.isoformat(),
            "last_updated": post.last_updated.isoformat(),
            "created_at": post.created_at.isoformat(),
            "account_info": account_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching posted content: {str(e)}")


@router.post("/", response_model=Dict[str, Any])
async def create_posted_content(
    content: PostedContentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo posted content mới
    
    Body:
    - post_id: Post ID duy nhất (required)
    - account_id: Tài khoản đăng bài (required)
    - content: Nội dung bài viết (optional)
    - post_url: URL bài viết (optional)
    - post_type: Loại bài (default: text)
    - like_count, comment_count, share_count: Engagement metrics
    - status: Trạng thái (default: published)
    """
    try:
        # Check if account exists
        acc_query = select(Account).where(Account.id == content.account_id)
        acc_result = await db.execute(acc_query)
        acc = acc_result.scalar_one_or_none()
        
        if not acc:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Check if post_id already exists
        existing_query = select(PostedContent).where(PostedContent.post_id == content.post_id)
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail="Post ID already exists")
        
        # Create new posted content
        new_post = PostedContent(
            post_id=content.post_id,
            account_id=content.account_id,
            content=content.content,
            post_url=content.post_url,
            post_type=content.post_type,
            like_count=content.like_count,
            comment_count=content.comment_count,
            share_count=content.share_count,
            status=content.status,
            posted_at=datetime.now(),
            last_updated=datetime.now(),
            created_at=datetime.now()
        )
        
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            action="posted_content_create",
            message=f"Đã thêm bài viết {content.post_id}",
            level="success",
            account_id=content.account_id,
            extra_data={
                "post_id": content.post_id,
                "post_type": content.post_type
            }
        )
        
        return {
            "success": True,
            "message": "Posted content created successfully",
            "content_id": new_post.id,
            "post_id": new_post.post_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating posted content: {str(e)}")


@router.put("/{content_id}", response_model=Dict[str, Any])
async def update_posted_content(
    content_id: int,
    update_data: PostedContentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Cập nhật posted content (inline editing support)
    
    Body (tất cả optional):
    - content: Nội dung bài viết
    - post_url: URL bài viết
    - post_type: Loại bài
    - like_count, comment_count, share_count: Engagement metrics
    - status: Trạng thái
    """
    try:
        # Get existing posted content
        query = select(PostedContent).where(PostedContent.id == content_id)
        result = await db.execute(query)
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(status_code=404, detail="Posted content not found")
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(post, field, value)
        
        post.last_updated = datetime.now()
        
        await db.commit()
        await db.refresh(post)
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            action="posted_content_update",
            message=f"Đã cập nhật bài viết {post.post_id}",
            level="info",
            account_id=post.account_id,
            extra_data={
                "content_id": post.id,
                "updated_fields": list(update_dict.keys())
            }
        )
        
        return {
            "success": True,
            "message": "Posted content updated successfully",
            "content_id": post.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating posted content: {str(e)}")


@router.delete("/{content_id}", response_model=Dict[str, Any])
async def delete_posted_content(
    content_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Xóa posted content"""
    try:
        # Get posted content
        query = select(PostedContent).where(PostedContent.id == content_id)
        result = await db.execute(query)
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(status_code=404, detail="Posted content not found")
        
        post_id = post.post_id
        account_id = post.account_id
        
        # Delete posted content
        await db.delete(post)
        await db.commit()
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            action="posted_content_delete",
            message=f"Đã xóa bài viết {post_id}",
            level="warning",
            account_id=account_id,
            extra_data={
                "content_id": content_id,
                "post_id": post_id
            }
        )
        
        return {
            "success": True,
            "message": "Posted content deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting posted content: {str(e)}")
