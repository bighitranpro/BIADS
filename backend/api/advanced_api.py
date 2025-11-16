"""
Bi Ads - Advanced Features API Endpoints
Author: Bi Ads Team
Version: 3.0.0
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from core.database import get_db
from core import crud

# Create router for advanced features
router = APIRouter(prefix="/api/advanced", tags=["Advanced Features"])

# ============================================
# PYDANTIC MODELS - SUB ACCOUNTS
# ============================================

class SubAccountCreate(BaseModel):
    main_account_id: int
    uid: str
    name: Optional[str] = None
    username: Optional[str] = None
    cookies: Optional[Dict] = None
    access_token: Optional[str] = None
    status: Optional[str] = 'active'
    auto_like: Optional[bool] = True
    auto_comment: Optional[bool] = False
    auto_share: Optional[bool] = False

class SubAccountResponse(BaseModel):
    id: int
    main_account_id: int
    uid: str
    name: Optional[str]
    username: Optional[str]
    status: str
    auto_like: bool
    auto_comment: bool
    auto_share: bool
    interaction_count: int
    last_interaction: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# PYDANTIC MODELS - FACEBOOK IDS
# ============================================

class FacebookIDCreate(BaseModel):
    uid: str
    name: Optional[str] = None
    username: Optional[str] = None
    profile_url: Optional[str] = None
    status: Optional[str] = 'valid'
    is_friend: Optional[bool] = False
    source: Optional[str] = 'manual'
    source_id: Optional[str] = None
    collected_by_account_id: Optional[int] = None
    notes: Optional[str] = None

class FacebookIDResponse(BaseModel):
    id: int
    uid: str
    name: Optional[str]
    username: Optional[str]
    profile_url: Optional[str]
    status: str
    is_friend: bool
    source: str
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# PYDANTIC MODELS - IP ADDRESSES
# ============================================

class IPAddressCreate(BaseModel):
    ip_address: str
    location: Optional[str] = None
    country_code: Optional[str] = None
    status: Optional[str] = 'active'
    is_proxy: Optional[bool] = False
    used_by_accounts: Optional[List[int]] = []
    is_blocked: Optional[bool] = False
    block_reason: Optional[str] = None
    notes: Optional[str] = None

class IPAddressResponse(BaseModel):
    id: int
    ip_address: str
    location: Optional[str]
    country_code: Optional[str]
    status: str
    is_proxy: bool
    is_blocked: bool
    access_count: int
    first_seen: datetime
    last_seen: datetime

    class Config:
        from_attributes = True

# ============================================
# PYDANTIC MODELS - WHITELIST ACCOUNTS
# ============================================

class WhitelistAccountCreate(BaseModel):
    uid: str
    name: Optional[str] = None
    username: Optional[str] = None
    type: Optional[str] = 'friend'
    status: Optional[str] = 'active'
    friendship_status: Optional[str] = 'friend'
    auto_accept_request: Optional[bool] = True
    auto_like_posts: Optional[bool] = True
    priority_messaging: Optional[bool] = False
    never_unfriend: Optional[bool] = True
    notes: Optional[str] = None
    added_by_account_id: Optional[int] = None

class WhitelistAccountResponse(BaseModel):
    id: int
    uid: str
    name: Optional[str]
    username: Optional[str]
    type: str
    status: str
    friendship_status: str
    auto_accept_request: bool
    auto_like_posts: bool
    priority_messaging: bool
    never_unfriend: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# PYDANTIC MODELS - POSTED CONTENT
# ============================================

class PostedContentCreate(BaseModel):
    post_id: str
    account_id: int
    content: Optional[str] = None
    post_url: Optional[str] = None
    post_type: Optional[str] = 'text'
    like_count: Optional[int] = 0
    comment_count: Optional[int] = 0
    share_count: Optional[int] = 0
    status: Optional[str] = 'published'

class PostedContentResponse(BaseModel):
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
    posted_at: datetime

    class Config:
        from_attributes = True

# ============================================
# PYDANTIC MODELS - MESSAGES
# ============================================

class MessageCreate(BaseModel):
    conversation_id: str
    account_id: int
    sender_uid: str
    sender_name: Optional[str] = None
    receiver_uid: str
    receiver_name: Optional[str] = None
    message_text: Optional[str] = None
    message_type: Optional[str] = 'text'
    is_read: Optional[bool] = False
    is_sent_by_me: Optional[bool] = False
    scheduled_at: Optional[datetime] = None

class MessageResponse(BaseModel):
    id: int
    conversation_id: str
    account_id: int
    sender_uid: str
    sender_name: Optional[str]
    receiver_uid: str
    receiver_name: Optional[str]
    message_text: Optional[str]
    message_type: str
    is_read: bool
    is_sent_by_me: bool
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# SUB ACCOUNTS ENDPOINTS
# ============================================

@router.post("/sub-accounts", response_model=SubAccountResponse)
async def create_sub_account(
    sub_account: SubAccountCreate,
    db: AsyncSession = Depends(get_db)
):
    """Tạo tài khoản phụ mới"""
    try:
        result = await crud.create_sub_account(db, sub_account.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sub-accounts", response_model=List[SubAccountResponse])
async def get_sub_accounts(
    main_account_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách tài khoản phụ"""
    result = await crud.get_sub_accounts(db, main_account_id, status, skip, limit)
    return result

@router.put("/sub-accounts/{sub_account_id}", response_model=SubAccountResponse)
async def update_sub_account(
    sub_account_id: int,
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Cập nhật tài khoản phụ"""
    result = await crud.update_sub_account(db, sub_account_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Sub account not found")
    return result

@router.delete("/sub-accounts/{sub_account_id}")
async def delete_sub_account(
    sub_account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Xóa tài khoản phụ"""
    success = await crud.delete_sub_account(db, sub_account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sub account not found")
    return {"message": "Sub account deleted successfully"}

@router.post("/sub-accounts/bulk")
async def bulk_create_sub_accounts(
    sub_accounts: List[SubAccountCreate],
    db: AsyncSession = Depends(get_db)
):
    """Import nhiều tài khoản phụ"""
    try:
        sub_accounts_data = [acc.dict() for acc in sub_accounts]
        count = await crud.bulk_create_sub_accounts(db, sub_accounts_data)
        return {"message": f"Imported {count} sub accounts successfully", "count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sub-accounts/stats")
async def get_sub_accounts_stats(
    main_account_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Lấy thống kê tài khoản phụ"""
    all_sub_accounts = await crud.get_sub_accounts(db, main_account_id, limit=10000)
    
    total = len(all_sub_accounts)
    active = sum(1 for acc in all_sub_accounts if acc.status == 'active')
    inactive = sum(1 for acc in all_sub_accounts if acc.status == 'inactive')
    banned = sum(1 for acc in all_sub_accounts if acc.status == 'banned')
    
    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "banned": banned
    }

# ============================================
# FACEBOOK IDS ENDPOINTS
# ============================================

@router.post("/facebook-ids", response_model=FacebookIDResponse)
async def create_facebook_id(
    fb_id: FacebookIDCreate,
    db: AsyncSession = Depends(get_db)
):
    """Tạo Facebook ID mới"""
    try:
        result = await crud.create_facebook_id(db, fb_id.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/facebook-ids", response_model=List[FacebookIDResponse])
async def get_facebook_ids(
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách Facebook IDs"""
    result = await crud.get_facebook_ids(db, status, source, skip, limit)
    return result

@router.post("/facebook-ids/bulk")
async def bulk_create_facebook_ids(
    fb_ids: List[FacebookIDCreate],
    db: AsyncSession = Depends(get_db)
):
    """Import nhiều Facebook IDs"""
    try:
        ids_data = [fb_id.dict() for fb_id in fb_ids]
        count = await crud.bulk_create_facebook_ids(db, ids_data)
        return {"message": f"Imported {count} Facebook IDs successfully", "count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/facebook-ids/{fb_id}")
async def delete_facebook_id(
    fb_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Xóa Facebook ID"""
    success = await crud.delete_facebook_id(db, fb_id)
    if not success:
        raise HTTPException(status_code=404, detail="Facebook ID not found")
    return {"message": "Facebook ID deleted successfully"}

@router.get("/facebook-ids/stats")
async def get_facebook_ids_stats(
    db: AsyncSession = Depends(get_db)
):
    """Lấy thống kê Facebook IDs"""
    all_ids = await crud.get_facebook_ids(db, limit=10000)
    
    total = len(all_ids)
    valid = sum(1 for id in all_ids if id.status == 'valid')
    invalid = sum(1 for id in all_ids if id.status == 'invalid')
    used = sum(1 for id in all_ids if id.status == 'used')
    
    return {
        "total": total,
        "valid": valid,
        "invalid": invalid,
        "used": used
    }

# ============================================
# IP ADDRESSES ENDPOINTS
# ============================================

@router.post("/ip-addresses", response_model=IPAddressResponse)
async def create_ip_address(
    ip_data: IPAddressCreate,
    db: AsyncSession = Depends(get_db)
):
    """Tạo IP address mới"""
    try:
        result = await crud.create_ip_address(db, ip_data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/ip-addresses", response_model=List[IPAddressResponse])
async def get_ip_addresses(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách IP addresses"""
    result = await crud.get_ip_addresses(db, status, skip, limit)
    return result

@router.put("/ip-addresses/{ip_id}", response_model=IPAddressResponse)
async def update_ip_address(
    ip_id: int,
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Cập nhật IP address"""
    result = await crud.update_ip_address(db, ip_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="IP address not found")
    return result

@router.get("/ip-addresses/stats")
async def get_ip_addresses_stats(
    db: AsyncSession = Depends(get_db)
):
    """Lấy thống kê IP addresses"""
    all_ips = await crud.get_ip_addresses(db, limit=10000)
    
    total = len(all_ips)
    active = sum(1 for ip in all_ips if ip.status == 'active')
    blocked = sum(1 for ip in all_ips if ip.status == 'blocked')
    trusted = sum(1 for ip in all_ips if ip.status == 'trusted')
    
    return {
        "total": total,
        "active": active,
        "blocked": blocked,
        "trusted": trusted
    }

# ============================================
# WHITELIST ACCOUNTS ENDPOINTS
# ============================================

@router.post("/whitelist", response_model=WhitelistAccountResponse)
async def create_whitelist_account(
    whitelist: WhitelistAccountCreate,
    db: AsyncSession = Depends(get_db)
):
    """Tạo whitelist account mới"""
    try:
        result = await crud.create_whitelist_account(db, whitelist.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/whitelist", response_model=List[WhitelistAccountResponse])
async def get_whitelist_accounts(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách whitelist accounts"""
    result = await crud.get_whitelist_accounts(db, type, status, skip, limit)
    return result

@router.post("/whitelist/bulk")
async def bulk_create_whitelist_accounts(
    whitelists: List[WhitelistAccountCreate],
    db: AsyncSession = Depends(get_db)
):
    """Import nhiều whitelist accounts"""
    try:
        whitelist_data = [w.dict() for w in whitelists]
        count = await crud.bulk_create_whitelist_accounts(db, whitelist_data)
        return {"message": f"Imported {count} whitelist accounts successfully", "count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/whitelist/{whitelist_id}")
async def delete_whitelist_account(
    whitelist_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Xóa whitelist account"""
    success = await crud.delete_whitelist_account(db, whitelist_id)
    if not success:
        raise HTTPException(status_code=404, detail="Whitelist account not found")
    return {"message": "Whitelist account deleted successfully"}

@router.get("/whitelist/stats")
async def get_whitelist_stats(
    db: AsyncSession = Depends(get_db)
):
    """Lấy thống kê whitelist accounts"""
    all_whitelist = await crud.get_whitelist_accounts(db, limit=10000)
    
    total = len(all_whitelist)
    vip = sum(1 for w in all_whitelist if w.type == 'vip')
    customer = sum(1 for w in all_whitelist if w.type == 'customer')
    partner = sum(1 for w in all_whitelist if w.type == 'partner')
    friend = sum(1 for w in all_whitelist if w.type == 'friend')
    
    return {
        "total": total,
        "vip": vip,
        "customer": customer,
        "partner": partner,
        "friend": friend
    }

# ============================================
# POSTED CONTENT ENDPOINTS
# ============================================

@router.post("/posts", response_model=PostedContentResponse)
async def create_posted_content(
    post: PostedContentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Tạo posted content mới"""
    try:
        result = await crud.create_posted_content(db, post.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/posts", response_model=List[PostedContentResponse])
async def get_posted_content(
    account_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách posted content"""
    result = await crud.get_posted_content(db, account_id, status, skip, limit)
    return result

@router.put("/posts/{post_id}", response_model=PostedContentResponse)
async def update_posted_content(
    post_id: str,
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Cập nhật posted content"""
    result = await crud.update_posted_content(db, post_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Posted content not found")
    return result

@router.get("/posts/stats")
async def get_posts_stats(
    account_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Lấy thống kê posted content"""
    all_posts = await crud.get_posted_content(db, account_id, limit=10000)
    
    total = len(all_posts)
    total_likes = sum(post.like_count for post in all_posts)
    total_comments = sum(post.comment_count for post in all_posts)
    total_shares = sum(post.share_count for post in all_posts)
    
    return {
        "total": total,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_shares": total_shares
    }

# ============================================
# MESSAGES ENDPOINTS
# ============================================

@router.post("/messages", response_model=MessageResponse)
async def create_message(
    message: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Tạo message mới"""
    try:
        result = await crud.create_message(db, message.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/messages", response_model=List[MessageResponse])
async def get_messages(
    account_id: Optional[int] = Query(None),
    conversation_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách messages"""
    result = await crud.get_messages(db, account_id, conversation_id, skip, limit)
    return result

@router.get("/conversations")
async def get_conversations(
    account_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách conversations"""
    result = await crud.get_conversations(db, account_id)
    return result

@router.get("/messages/stats")
async def get_messages_stats(
    account_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Lấy thống kê messages"""
    all_messages = await crud.get_messages(db, account_id, limit=10000)
    
    total = len(all_messages)
    unread = sum(1 for msg in all_messages if not msg.is_read)
    sent = sum(1 for msg in all_messages if msg.is_sent_by_me)
    received = total - sent
    
    # Count conversations
    conversations = await crud.get_conversations(db, account_id) if account_id else []
    
    return {
        "total": total,
        "unread": unread,
        "sent": sent,
        "received": received,
        "conversations": len(conversations)
    }
