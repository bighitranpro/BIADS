"""
Bi Ads - CRUD Operations
Author: Bi Ads Team
Version: 2.0.0
"""

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from .database import (
    Account, Proxy, Task, ActivityLog, Settings,
    SubAccount, FacebookID, IPAddress, WhitelistAccount, PostedContent, Message, AutoReplyTemplate
)

# ============================================
# ACCOUNT CRUD
# ============================================

async def create_account(db: AsyncSession, account_data: Dict[str, Any]) -> Account:
    """Tạo tài khoản mới"""
    account = Account(
        uid=account_data['uid'],
        username=account_data.get('username'),
        name=account_data.get('name'),
        email=account_data.get('email'),
        password=account_data.get('password'),
        cookies=json.dumps(account_data.get('cookies')) if account_data.get('cookies') else None,
        access_token=account_data.get('access_token'),
        two_fa_key=account_data.get('two_fa_key'),
        proxy_id=account_data.get('proxy_id'),
        status=account_data.get('status', 'active'),
        method=account_data.get('method', 'cookies')
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account

async def get_account(db: AsyncSession, account_id: int) -> Optional[Account]:
    """Lấy thông tin tài khoản theo ID"""
    result = await db.execute(
        select(Account).where(Account.id == account_id).options(selectinload(Account.proxy))
    )
    return result.scalar_one_or_none()

async def get_account_by_uid(db: AsyncSession, uid: str) -> Optional[Account]:
    """Lấy thông tin tài khoản theo UID"""
    result = await db.execute(
        select(Account).where(Account.uid == uid).options(selectinload(Account.proxy))
    )
    return result.scalar_one_or_none()

async def get_accounts(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None
) -> List[Account]:
    """Lấy danh sách tài khoản"""
    query = select(Account).options(selectinload(Account.proxy))
    
    if status:
        query = query.where(Account.status == status)
    
    query = query.offset(skip).limit(limit).order_by(Account.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_account(db: AsyncSession, account_id: int, account_data: Dict[str, Any]) -> Optional[Account]:
    """Cập nhật thông tin tài khoản"""
    account = await get_account(db, account_id)
    if not account:
        return None
    
    for key, value in account_data.items():
        if key == 'cookies' and value:
            value = json.dumps(value)
        if hasattr(account, key):
            setattr(account, key, value)
    
    account.updated_at = datetime.now()
    await db.commit()
    await db.refresh(account)
    return account

async def delete_account(db: AsyncSession, account_id: int) -> bool:
    """Xóa tài khoản"""
    account = await get_account(db, account_id)
    if not account:
        return False
    
    await db.delete(account)
    await db.commit()
    return True

async def check_account_status(db: AsyncSession, account_id: int) -> Dict[str, Any]:
    """Kiểm tra trạng thái tài khoản (live/die)"""
    account = await get_account(db, account_id)
    if not account:
        return {'error': 'Account not found'}
    
    # TODO: Implement actual Facebook API check
    # For now, return mock data based on cookies/token availability
    is_live = False
    reason = ''
    
    if account.cookies:
        # Check if cookies are valid format
        try:
            import json as json_lib
            cookies = json_lib.loads(account.cookies)
            is_live = len(cookies) > 0
            reason = 'Có cookies' if is_live else 'Cookies không hợp lệ'
        except:
            reason = 'Cookies lỗi định dạng'
    elif account.access_token:
        is_live = len(account.access_token) > 50
        reason = 'Có access token' if is_live else 'Token không hợp lệ'
    else:
        reason = 'Không có thông tin xác thực'
    
    # Update account status
    new_status = 'active' if is_live else 'dead'
    account.status = new_status
    account.updated_at = datetime.now()
    await db.commit()
    
    return {
        'account_id': account_id,
        'uid': account.uid,
        'is_live': is_live,
        'status': new_status,
        'reason': reason,
        'checked_at': datetime.now().isoformat()
    }

async def bulk_check_accounts_status(db: AsyncSession, account_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
    """Kiểm tra trạng thái nhiều tài khoản"""
    if account_ids:
        # Check specific accounts
        results = []
        for acc_id in account_ids:
            result = await check_account_status(db, acc_id)
            results.append(result)
        return results
    else:
        # Check all accounts
        accounts = await get_accounts(db, limit=1000)
        results = []
        for account in accounts:
            result = await check_account_status(db, account.id)
            results.append(result)
        return results

async def assign_proxy_to_account(db: AsyncSession, account_id: int, proxy_id: Optional[int]) -> Optional[Account]:
    """Gán proxy cho tài khoản"""
    account = await get_account(db, account_id)
    if not account:
        return None
    
    account.proxy_id = proxy_id
    account.updated_at = datetime.now()
    await db.commit()
    await db.refresh(account)
    return account

async def bulk_create_accounts(db: AsyncSession, accounts_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Tạo nhiều tài khoản cùng lúc - bỏ qua UID trùng lặp"""
    accounts = []
    skipped = 0
    skipped_uids = []
    
    for data in accounts_data:
        uid = data['uid']
        
        # Check if UID already exists
        existing = await db.execute(select(Account).where(Account.uid == uid))
        if existing.scalar_one_or_none():
            skipped += 1
            skipped_uids.append(uid)
            continue
        
        account = Account(
            uid=uid,
            username=data.get('username'),
            name=data.get('name'),
            email=data.get('email'),
            cookies=json.dumps(data.get('cookies')) if data.get('cookies') else None,
            access_token=data.get('access_token'),
            two_fa_key=data.get('two_fa_key'),
            proxy_id=data.get('proxy_id'),
            status=data.get('status', 'active'),
            method=data.get('method', 'cookies')
        )
        accounts.append(account)
    
    if accounts:
        db.add_all(accounts)
        await db.commit()
    
    return {
        'imported': len(accounts),
        'skipped': skipped,
        'skipped_uids': skipped_uids[:10]  # Only return first 10 for display
    }

# ============================================
# PROXY CRUD
# ============================================

async def create_proxy(db: AsyncSession, proxy_data: Dict[str, Any]) -> Proxy:
    """Tạo proxy mới"""
    proxy = Proxy(
        ip=proxy_data['ip'],
        port=proxy_data['port'],
        username=proxy_data.get('username'),
        password=proxy_data.get('password'),
        protocol=proxy_data.get('protocol', 'http'),
        status=proxy_data.get('status', 'active'),
        location=proxy_data.get('location')
    )
    db.add(proxy)
    await db.commit()
    await db.refresh(proxy)
    return proxy

async def get_proxy(db: AsyncSession, proxy_id: int) -> Optional[Proxy]:
    """Lấy thông tin proxy"""
    result = await db.execute(select(Proxy).where(Proxy.id == proxy_id))
    return result.scalar_one_or_none()

async def get_proxies(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Proxy]:
    """Lấy danh sách proxy"""
    result = await db.execute(
        select(Proxy).offset(skip).limit(limit).order_by(Proxy.created_at.desc())
    )
    return result.scalars().all()

async def get_available_proxy(db: AsyncSession) -> Optional[Proxy]:
    """Lấy proxy khả dụng (ít tài khoản nhất)"""
    result = await db.execute(
        select(Proxy)
        .where(Proxy.status == 'active')
        .order_by(Proxy.id)
        .limit(1)
    )
    return result.scalar_one_or_none()

async def bulk_create_proxies(db: AsyncSession, proxies_data: List[Dict[str, Any]]) -> int:
    """Tạo nhiều proxy cùng lúc"""
    proxies = []
    for data in proxies_data:
        proxy = Proxy(
            ip=data['ip'],
            port=data['port'],
            username=data.get('username'),
            password=data.get('password'),
            protocol=data.get('protocol', 'http'),
            status=data.get('status', 'active')
        )
        proxies.append(proxy)
    
    db.add_all(proxies)
    await db.commit()
    return len(proxies)

async def delete_proxy(db: AsyncSession, proxy_id: int) -> bool:
    """Xóa proxy"""
    proxy = await get_proxy(db, proxy_id)
    if not proxy:
        return False
    
    await db.delete(proxy)
    await db.commit()
    return True

# ============================================
# TASK CRUD
# ============================================

async def create_task(db: AsyncSession, task_data: Dict[str, Any]) -> Task:
    """Tạo tác vụ mới"""
    task = Task(
        task_id=task_data['task_id'],
        account_id=task_data['account_id'],
        task_type=task_data['task_type'],
        task_name=task_data.get('task_name'),
        params=json.dumps(task_data.get('params', {})),
        status='pending'
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

async def get_task(db: AsyncSession, task_id: str) -> Optional[Task]:
    """Lấy thông tin tác vụ"""
    result = await db.execute(
        select(Task).where(Task.task_id == task_id).options(selectinload(Task.account))
    )
    return result.scalar_one_or_none()

async def get_tasks(
    db: AsyncSession,
    account_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """Lấy danh sách tác vụ"""
    query = select(Task).options(selectinload(Task.account))
    
    if account_id:
        query = query.where(Task.account_id == account_id)
    if status:
        query = query.where(Task.status == status)
    
    query = query.offset(skip).limit(limit).order_by(Task.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_task_status(
    db: AsyncSession,
    task_id: str,
    status: str,
    progress: Optional[int] = None,
    result: Optional[Dict] = None,
    error_message: Optional[str] = None
) -> Optional[Task]:
    """Cập nhật trạng thái tác vụ"""
    task = await get_task(db, task_id)
    if not task:
        return None
    
    task.status = status
    if progress is not None:
        task.progress = progress
    if result:
        task.result = json.dumps(result)
    if error_message:
        task.error_message = error_message
    
    if status == 'processing' and not task.started_at:
        task.started_at = datetime.now()
    if status in ['completed', 'failed', 'cancelled']:
        task.completed_at = datetime.now()
    
    await db.commit()
    await db.refresh(task)
    return task

# ============================================
# ACTIVITY LOG CRUD
# ============================================

async def create_log(db: AsyncSession, log_data: Dict[str, Any]) -> ActivityLog:
    """Tạo log hoạt động"""
    log = ActivityLog(
        account_id=log_data.get('account_id'),
        task_id=log_data.get('task_id'),
        action=log_data['action'],
        message=log_data['message'],
        level=log_data.get('level', 'info'),
        extra_data=json.dumps(log_data.get('metadata', {}))
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log

async def get_logs(
    db: AsyncSession,
    account_id: Optional[int] = None,
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[ActivityLog]:
    """Lấy danh sách log"""
    query = select(ActivityLog)
    
    if account_id:
        query = query.where(ActivityLog.account_id == account_id)
    if level:
        query = query.where(ActivityLog.level == level)
    
    query = query.offset(skip).limit(limit).order_by(ActivityLog.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

# ============================================
# SETTINGS CRUD
# ============================================

async def get_setting(db: AsyncSession, key: str) -> Optional[str]:
    """Lấy cài đặt"""
    result = await db.execute(select(Settings).where(Settings.key == key))
    setting = result.scalar_one_or_none()
    return setting.value if setting else None

async def set_setting(db: AsyncSession, key: str, value: str, description: Optional[str] = None) -> Settings:
    """Lưu cài đặt"""
    result = await db.execute(select(Settings).where(Settings.key == key))
    setting = result.scalar_one_or_none()
    
    if setting:
        setting.value = value
        setting.updated_at = datetime.now()
        if description:
            setting.description = description
    else:
        setting = Settings(key=key, value=value, description=description)
        db.add(setting)
    
    await db.commit()
    await db.refresh(setting)
    return setting

# ============================================
# SUB ACCOUNT CRUD
# ============================================

async def create_sub_account(db: AsyncSession, sub_account_data: Dict[str, Any]) -> SubAccount:
    """Tạo tài khoản phụ mới"""
    sub_account = SubAccount(
        main_account_id=sub_account_data['main_account_id'],
        uid=sub_account_data['uid'],
        name=sub_account_data.get('name'),
        username=sub_account_data.get('username'),
        cookies=json.dumps(sub_account_data.get('cookies')) if sub_account_data.get('cookies') else None,
        access_token=sub_account_data.get('access_token'),
        status=sub_account_data.get('status', 'active'),
        auto_like=sub_account_data.get('auto_like', True),
        auto_comment=sub_account_data.get('auto_comment', False),
        auto_share=sub_account_data.get('auto_share', False)
    )
    db.add(sub_account)
    await db.commit()
    await db.refresh(sub_account)
    return sub_account

async def get_sub_accounts(
    db: AsyncSession,
    main_account_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[SubAccount]:
    """Lấy danh sách tài khoản phụ"""
    query = select(SubAccount).options(selectinload(SubAccount.main_account))
    
    if main_account_id:
        query = query.where(SubAccount.main_account_id == main_account_id)
    if status:
        query = query.where(SubAccount.status == status)
    
    query = query.offset(skip).limit(limit).order_by(SubAccount.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_sub_account(db: AsyncSession, sub_account_id: int, data: Dict[str, Any]) -> Optional[SubAccount]:
    """Cập nhật tài khoản phụ"""
    result = await db.execute(select(SubAccount).where(SubAccount.id == sub_account_id))
    sub_account = result.scalar_one_or_none()
    
    if not sub_account:
        return None
    
    for key, value in data.items():
        if key == 'cookies' and value:
            value = json.dumps(value)
        if hasattr(sub_account, key):
            setattr(sub_account, key, value)
    
    sub_account.updated_at = datetime.now()
    await db.commit()
    await db.refresh(sub_account)
    return sub_account

async def delete_sub_account(db: AsyncSession, sub_account_id: int) -> bool:
    """Xóa tài khoản phụ"""
    result = await db.execute(select(SubAccount).where(SubAccount.id == sub_account_id))
    sub_account = result.scalar_one_or_none()
    
    if not sub_account:
        return False
    
    await db.delete(sub_account)
    await db.commit()
    return True

async def bulk_create_sub_accounts(db: AsyncSession, sub_accounts_data: List[Dict[str, Any]]) -> int:
    """Tạo nhiều tài khoản phụ cùng lúc"""
    sub_accounts = []
    for data in sub_accounts_data:
        sub_account = SubAccount(
            main_account_id=data['main_account_id'],
            uid=data['uid'],
            name=data.get('name'),
            username=data.get('username'),
            cookies=json.dumps(data.get('cookies')) if data.get('cookies') else None,
            access_token=data.get('access_token'),
            status=data.get('status', 'active'),
            auto_like=data.get('auto_like', True),
            auto_comment=data.get('auto_comment', False),
            auto_share=data.get('auto_share', False)
        )
        sub_accounts.append(sub_account)
    
    db.add_all(sub_accounts)
    await db.commit()
    return len(sub_accounts)

# ============================================
# FACEBOOK ID CRUD
# ============================================

async def create_facebook_id(db: AsyncSession, fb_id_data: Dict[str, Any]) -> FacebookID:
    """Tạo Facebook ID mới"""
    fb_id = FacebookID(
        uid=fb_id_data['uid'],
        name=fb_id_data.get('name'),
        username=fb_id_data.get('username'),
        profile_url=fb_id_data.get('profile_url'),
        status=fb_id_data.get('status', 'valid'),
        is_friend=fb_id_data.get('is_friend', False),
        source=fb_id_data.get('source', 'manual'),
        source_id=fb_id_data.get('source_id'),
        collected_by_account_id=fb_id_data.get('collected_by_account_id'),
        notes=fb_id_data.get('notes')
    )
    db.add(fb_id)
    await db.commit()
    await db.refresh(fb_id)
    return fb_id

async def get_facebook_ids(
    db: AsyncSession,
    status: Optional[str] = None,
    source: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[FacebookID]:
    """Lấy danh sách Facebook ID"""
    query = select(FacebookID)
    
    if status:
        query = query.where(FacebookID.status == status)
    if source:
        query = query.where(FacebookID.source == source)
    
    query = query.offset(skip).limit(limit).order_by(FacebookID.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def bulk_create_facebook_ids(db: AsyncSession, ids_data: List[Dict[str, Any]]) -> int:
    """Tạo nhiều Facebook ID cùng lúc"""
    fb_ids = []
    for data in ids_data:
        # Skip if UID already exists
        existing = await db.execute(select(FacebookID).where(FacebookID.uid == data['uid']))
        if existing.scalar_one_or_none():
            continue
            
        fb_id = FacebookID(
            uid=data['uid'],
            name=data.get('name'),
            username=data.get('username'),
            profile_url=data.get('profile_url'),
            status=data.get('status', 'valid'),
            is_friend=data.get('is_friend', False),
            source=data.get('source', 'import'),
            source_id=data.get('source_id'),
            collected_by_account_id=data.get('collected_by_account_id'),
            notes=data.get('notes')
        )
        fb_ids.append(fb_id)
    
    db.add_all(fb_ids)
    await db.commit()
    return len(fb_ids)

async def delete_facebook_id(db: AsyncSession, fb_id: int) -> bool:
    """Xóa Facebook ID"""
    result = await db.execute(select(FacebookID).where(FacebookID.id == fb_id))
    facebook_id = result.scalar_one_or_none()
    
    if not facebook_id:
        return False
    
    await db.delete(facebook_id)
    await db.commit()
    return True

# ============================================
# IP ADDRESS CRUD
# ============================================

async def create_ip_address(db: AsyncSession, ip_data: Dict[str, Any]) -> IPAddress:
    """Tạo IP address mới"""
    ip_address = IPAddress(
        ip_address=ip_data['ip_address'],
        location=ip_data.get('location'),
        country_code=ip_data.get('country_code'),
        status=ip_data.get('status', 'active'),
        is_proxy=ip_data.get('is_proxy', False),
        used_by_accounts=json.dumps(ip_data.get('used_by_accounts', [])),
        is_blocked=ip_data.get('is_blocked', False),
        block_reason=ip_data.get('block_reason'),
        notes=ip_data.get('notes')
    )
    db.add(ip_address)
    await db.commit()
    await db.refresh(ip_address)
    return ip_address

async def get_ip_addresses(
    db: AsyncSession,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[IPAddress]:
    """Lấy danh sách IP addresses"""
    query = select(IPAddress)
    
    if status:
        query = query.where(IPAddress.status == status)
    
    query = query.offset(skip).limit(limit).order_by(IPAddress.last_seen.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_ip_address(db: AsyncSession, ip_id: int, data: Dict[str, Any]) -> Optional[IPAddress]:
    """Cập nhật IP address"""
    result = await db.execute(select(IPAddress).where(IPAddress.id == ip_id))
    ip_address = result.scalar_one_or_none()
    
    if not ip_address:
        return None
    
    for key, value in data.items():
        if key == 'used_by_accounts' and value:
            value = json.dumps(value)
        if hasattr(ip_address, key):
            setattr(ip_address, key, value)
    
    ip_address.last_seen = datetime.now()
    await db.commit()
    await db.refresh(ip_address)
    return ip_address

# ============================================
# WHITELIST ACCOUNT CRUD
# ============================================

async def create_whitelist_account(db: AsyncSession, whitelist_data: Dict[str, Any]) -> WhitelistAccount:
    """Tạo whitelist account mới"""
    whitelist = WhitelistAccount(
        uid=whitelist_data['uid'],
        name=whitelist_data.get('name'),
        username=whitelist_data.get('username'),
        type=whitelist_data.get('type', 'friend'),
        status=whitelist_data.get('status', 'active'),
        friendship_status=whitelist_data.get('friendship_status', 'friend'),
        auto_accept_request=whitelist_data.get('auto_accept_request', True),
        auto_like_posts=whitelist_data.get('auto_like_posts', True),
        priority_messaging=whitelist_data.get('priority_messaging', False),
        never_unfriend=whitelist_data.get('never_unfriend', True),
        notes=whitelist_data.get('notes'),
        added_by_account_id=whitelist_data.get('added_by_account_id')
    )
    db.add(whitelist)
    await db.commit()
    await db.refresh(whitelist)
    return whitelist

async def get_whitelist_accounts(
    db: AsyncSession,
    type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[WhitelistAccount]:
    """Lấy danh sách whitelist accounts"""
    query = select(WhitelistAccount)
    
    if type:
        query = query.where(WhitelistAccount.type == type)
    if status:
        query = query.where(WhitelistAccount.status == status)
    
    query = query.offset(skip).limit(limit).order_by(WhitelistAccount.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def bulk_create_whitelist_accounts(db: AsyncSession, whitelist_data: List[Dict[str, Any]]) -> int:
    """Tạo nhiều whitelist accounts cùng lúc"""
    whitelists = []
    for data in whitelist_data:
        # Skip if UID already exists
        existing = await db.execute(select(WhitelistAccount).where(WhitelistAccount.uid == data['uid']))
        if existing.scalar_one_or_none():
            continue
            
        whitelist = WhitelistAccount(
            uid=data['uid'],
            name=data.get('name'),
            username=data.get('username'),
            type=data.get('type', 'friend'),
            status=data.get('status', 'active'),
            friendship_status=data.get('friendship_status', 'friend'),
            auto_accept_request=data.get('auto_accept_request', True),
            auto_like_posts=data.get('auto_like_posts', True),
            priority_messaging=data.get('priority_messaging', False),
            never_unfriend=data.get('never_unfriend', True),
            notes=data.get('notes'),
            added_by_account_id=data.get('added_by_account_id')
        )
        whitelists.append(whitelist)
    
    db.add_all(whitelists)
    await db.commit()
    return len(whitelists)

async def delete_whitelist_account(db: AsyncSession, whitelist_id: int) -> bool:
    """Xóa whitelist account"""
    result = await db.execute(select(WhitelistAccount).where(WhitelistAccount.id == whitelist_id))
    whitelist = result.scalar_one_or_none()
    
    if not whitelist:
        return False
    
    await db.delete(whitelist)
    await db.commit()
    return True

# ============================================
# POSTED CONTENT CRUD
# ============================================

async def create_posted_content(db: AsyncSession, post_data: Dict[str, Any]) -> PostedContent:
    """Tạo posted content mới"""
    post = PostedContent(
        post_id=post_data['post_id'],
        account_id=post_data['account_id'],
        content=post_data.get('content'),
        post_url=post_data.get('post_url'),
        post_type=post_data.get('post_type', 'text'),
        like_count=post_data.get('like_count', 0),
        comment_count=post_data.get('comment_count', 0),
        share_count=post_data.get('share_count', 0),
        status=post_data.get('status', 'published')
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post

async def get_posted_content(
    db: AsyncSession,
    account_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[PostedContent]:
    """Lấy danh sách posted content"""
    query = select(PostedContent).options(selectinload(PostedContent.account))
    
    if account_id:
        query = query.where(PostedContent.account_id == account_id)
    if status:
        query = query.where(PostedContent.status == status)
    
    query = query.offset(skip).limit(limit).order_by(PostedContent.posted_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_posted_content(db: AsyncSession, post_id: str, data: Dict[str, Any]) -> Optional[PostedContent]:
    """Cập nhật posted content"""
    result = await db.execute(select(PostedContent).where(PostedContent.post_id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        return None
    
    for key, value in data.items():
        if hasattr(post, key):
            setattr(post, key, value)
    
    post.last_updated = datetime.now()
    await db.commit()
    await db.refresh(post)
    return post

# ============================================
# MESSAGE CRUD
# ============================================

async def create_message(db: AsyncSession, message_data: Dict[str, Any]) -> Message:
    """Tạo message mới"""
    message = Message(
        conversation_id=message_data['conversation_id'],
        account_id=message_data['account_id'],
        sender_uid=message_data['sender_uid'],
        sender_name=message_data.get('sender_name'),
        receiver_uid=message_data['receiver_uid'],
        receiver_name=message_data.get('receiver_name'),
        message_text=message_data.get('message_text'),
        message_type=message_data.get('message_type', 'text'),
        is_read=message_data.get('is_read', False),
        is_sent_by_me=message_data.get('is_sent_by_me', False),
        auto_reply_enabled=message_data.get('auto_reply_enabled', False),
        scheduled_at=message_data.get('scheduled_at'),
        sent_at=message_data.get('sent_at')
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message

async def get_messages(
    db: AsyncSession,
    account_id: Optional[int] = None,
    conversation_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Message]:
    """Lấy danh sách messages"""
    query = select(Message).options(selectinload(Message.account))
    
    if account_id:
        query = query.where(Message.account_id == account_id)
    if conversation_id:
        query = query.where(Message.conversation_id == conversation_id)
    
    query = query.offset(skip).limit(limit).order_by(Message.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_conversations(db: AsyncSession, account_id: int) -> List[Dict[str, Any]]:
    """Lấy danh sách conversations"""
    result = await db.execute(
        select(Message.conversation_id, Message.receiver_name, Message.created_at)
        .where(Message.account_id == account_id)
        .order_by(Message.created_at.desc())
        .distinct(Message.conversation_id)
        .limit(50)
    )
    
    conversations = []
    for row in result:
        conversations.append({
            'conversation_id': row.conversation_id,
            'name': row.receiver_name,
            'last_message_time': row.created_at
        })
    
    return conversations

# ============================================
# AUTO REPLY TEMPLATE CRUD
# ============================================

async def create_auto_reply_template(db: AsyncSession, template_data: Dict[str, Any]) -> AutoReplyTemplate:
    """Tạo auto reply template mới"""
    template = AutoReplyTemplate(
        account_id=template_data['account_id'],
        name=template_data['name'],
        trigger_keywords=json.dumps(template_data.get('trigger_keywords', [])),
        reply_message=template_data['reply_message'],
        is_active=template_data.get('is_active', True),
        priority=template_data.get('priority', 0)
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template

async def get_auto_reply_templates(
    db: AsyncSession,
    account_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AutoReplyTemplate]:
    """Lấy danh sách auto reply templates"""
    query = select(AutoReplyTemplate)
    
    if account_id:
        query = query.where(AutoReplyTemplate.account_id == account_id)
    if is_active is not None:
        query = query.where(AutoReplyTemplate.is_active == is_active)
    
    query = query.offset(skip).limit(limit).order_by(AutoReplyTemplate.priority.desc())
    
    result = await db.execute(query)
    return result.scalars().all()
