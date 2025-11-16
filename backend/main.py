"""
Bi Ads - Multi Tool PRO v2.0 - Backend API
Author: Bi Ads Team
Version: 2.0.0
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database and CRUD
from core.database import get_db, init_db, Account as DBAccount, Proxy as DBProxy
from core import crud
from services.file_parser import (
    parse_via_txt, 
    parse_proxy_txt, 
    validate_account_data, 
    validate_proxy_data,
    get_import_stats
)

# Import webhook and telegram integrations
from services.facebook_webhook import FacebookWebhook, WebhookEventHandler
from services.telegram_bot import TelegramBot

# Initialize global instances
facebook_webhook = FacebookWebhook(
    app_secret=os.getenv('FACEBOOK_APP_SECRET', 'your-app-secret'),
    verify_token=os.getenv('FACEBOOK_VERIFY_TOKEN', 'bi-ads-verify-token')
)

telegram_bot = TelegramBot(
    bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
    chat_id=os.getenv('TELEGRAM_CHAT_ID')
)

webhook_handler = WebhookEventHandler()

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    print("🚀 Initializing database...")
    await init_db()
    print("✅ Database ready!")
    
    # Send startup notification
    telegram_bot.send_notification(
        "Hệ thống khởi động",
        "Bi Ads Multi Tool PRO đã sẵn sàng hoạt động",
        'success',
        {
            'Version': '3.0.0',
            'Database': 'SQLite',
            'Webhook': 'Active'
        }
    )
    
    yield
    
    # Send shutdown notification
    telegram_bot.send_notification(
        "Hệ thống đang tắt",
        "Bi Ads Multi Tool PRO đang ngừng hoạt động",
        'warning'
    )
    print("👋 Shutting down...")

app = FastAPI(
    title="Bi Ads Multi Tool PRO API",
    version="2.0.0",
    description="Backend API for Bi Ads Facebook Automation Tool",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include all API routers
from api.advanced_api import router as advanced_router
from api.settings_api import router as settings_router
from api.facebook_tasks_api import router as facebook_tasks_router
from api.task_manager_api import router as task_manager_router
from api.account_interactions_api import router as interactions_router
from api.account_checker_api import router as account_checker_router
from api.activity_api import router as activity_router
from api.task_status_api import router as task_status_router
from api.proxy_bulk_api import router as proxy_bulk_router
from api.sub_accounts_api import router as sub_accounts_router
from api.facebook_ids_api import router as facebook_ids_router
from api.posted_content_api import router as posted_content_router

app.include_router(advanced_router)
app.include_router(settings_router)
app.include_router(facebook_tasks_router)
app.include_router(interactions_router)
app.include_router(task_manager_router)
app.include_router(account_checker_router)
app.include_router(activity_router)
app.include_router(task_status_router)
app.include_router(proxy_bulk_router)
app.include_router(sub_accounts_router)
app.include_router(facebook_ids_router)
app.include_router(posted_content_router)

# ============================================
# PYDANTIC MODELS
# ============================================

class AccountCreate(BaseModel):
    uid: str
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    cookies: Optional[List[Dict]] = None
    access_token: Optional[str] = None
    two_fa_key: Optional[str] = None
    proxy_id: Optional[int] = None
    method: str = "cookies"
    status: str = "active"

class AccountResponse(BaseModel):
    id: int
    uid: str
    username: Optional[str]
    name: Optional[str]
    email: Optional[str]
    status: str
    method: str
    proxy_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProxyCreate(BaseModel):
    ip: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"
    status: str = "active"

class ProxyResponse(BaseModel):
    id: int
    ip: str
    port: int
    protocol: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskRequest(BaseModel):
    task_type: str
    account_id: int
    params: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    success: bool
    task_id: str
    message: str
    status: str = "processing"

# ============================================
# BASIC ROUTES
# ============================================

@app.get("/")
async def root():
    return {
        "app": "Bi Ads Multi Tool PRO",
        "version": "3.0.0",
        "status": "running",
        "author": "Bi Ads Team",
        "database": "Connected",
        "webhook": "Active",
        "telegram": "Configured" if telegram_bot.bot_token else "Not configured"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "database": "online",
        "webhook": "active",
        "telegram_configured": bool(telegram_bot.bot_token)
    }

# ============================================
# FACEBOOK WEBHOOK ENDPOINTS
# ============================================

@app.get("/webhook")
async def verify_webhook(
    request: Request,
    mode: str = Query(alias="hub.mode"),
    token: str = Query(alias="hub.verify_token"),
    challenge: str = Query(alias="hub.challenge")
):
    """
    Verify webhook subscription from Facebook
    This endpoint is called by Facebook during webhook setup
    """
    print(f"📡 Webhook verification request: mode={mode}, token={token[:10]}...")
    
    result = facebook_webhook.verify_webhook(mode, token, challenge)
    
    if result:
        print(f"✅ Webhook verified successfully")
        # Send notification
        telegram_bot.send_notification(
            "Webhook đã được kích hoạt",
            "Facebook webhook đã được xác thực thành công",
            'success'
        )
        return PlainTextResponse(result)
    else:
        print(f"❌ Webhook verification failed")
        telegram_bot.send_error_alert(
            "Webhook verification failed",
            {'mode': mode, 'token': token[:10]}
        )
        raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def receive_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Receive webhook events from Facebook
    """
    # Get raw body for signature verification
    body = await request.body()
    
    # Get signature from header
    signature = request.headers.get('x-hub-signature-256', '')
    
    # Verify signature
    if not facebook_webhook.verify_signature(body, signature):
        print(f"❌ Invalid webhook signature")
        telegram_bot.send_error_alert(
            "Invalid webhook signature",
            {'signature': signature[:20]}
        )
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse JSON data
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    
    print(f"📥 Received webhook event: {data.get('object')}")
    
    # Process webhook event
    result = facebook_webhook.process_webhook_event(data)
    
    if not result.get('success'):
        return JSONResponse({"status": "error", "message": result.get('error')})
    
    # Handle each event
    for event in result.get('events', []):
        event_category = event.get('event_category')
        
        try:
            # Handle different event types
            if event_category == 'post':
                await webhook_handler.handle_post_event(event)
            elif event_category == 'comment':
                await webhook_handler.handle_comment_event(event)
            elif event_category == 'reaction':
                await webhook_handler.handle_reaction_event(event)
            elif event_category == 'mention':
                await webhook_handler.handle_mention_event(event)
            
            # Save event to database
            await crud.create_log(db, {
                'action': 'webhook_event',
                'message': f"Facebook {event_category} event received",
                'level': 'info',
                'metadata': event
            })
            
            # Send Telegram notification
            telegram_bot.send_webhook_notification(
                event_category,
                event.get('data', {})
            )
            
        except Exception as e:
            print(f"❌ Error handling event: {e}")
            telegram_bot.send_error_alert(
                f"Error processing {event_category} event",
                {'error': str(e), 'event': event}
            )
    
    return JSONResponse({
        "status": "success",
        "events_processed": len(result.get('events', []))
    })

# ============================================
# ACCOUNT MANAGEMENT
# ============================================

@app.post("/api/accounts", response_model=AccountResponse)
async def create_account(account: AccountCreate, db: AsyncSession = Depends(get_db)):
    """Tạo tài khoản mới"""
    try:
        # Check if account already exists
        existing = await crud.get_account_by_uid(db, account.uid)
        if existing:
            raise HTTPException(status_code=400, detail="Tài khoản đã tồn tại")
        
        db_account = await crud.create_account(db, account.dict())
        return db_account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo tài khoản: {str(e)}")

@app.get("/api/accounts", response_model=List[AccountResponse])
async def get_accounts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách tài khoản"""
    accounts = await crud.get_accounts(db, skip=skip, limit=limit, status=status)
    return accounts

@app.get("/api/accounts/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """Lấy thông tin tài khoản"""
    account = await crud.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    return account

@app.put("/api/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Cập nhật thông tin tài khoản"""
    account = await crud.update_account(db, account_id, account_data)
    if not account:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    return account

@app.delete("/api/accounts/{account_id}")
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """Xóa tài khoản"""
    success = await crud.delete_account(db, account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    return {"success": True, "message": "Đã xóa tài khoản"}

@app.post("/api/accounts/import-via")
async def import_via_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Import tài khoản từ file via.txt"""
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Parse file
        accounts_data = parse_via_txt(content_str)
        
        if not accounts_data:
            raise HTTPException(status_code=400, detail="Không tìm thấy dữ liệu hợp lệ trong file")
        
        # Validate and filter valid accounts
        valid_accounts = [acc for acc in accounts_data if validate_account_data(acc)]
        
        if not valid_accounts:
            raise HTTPException(status_code=400, detail="Không có tài khoản hợp lệ để import")
        
        # Bulk create accounts (now returns dict with imported/skipped counts)
        result = await crud.bulk_create_accounts(db, valid_accounts)
        
        # Get statistics
        stats = get_import_stats(valid_accounts, [])
        
        # Create log
        await crud.create_log(db, {
            'action': 'import_accounts',
            'message': f"Import thành công {result['imported']} tài khoản, bỏ qua {result['skipped']} trùng lặp",
            'level': 'success',
            'metadata': stats
        })
        
        # Send Telegram notification
        telegram_bot.send_notification(
            "Import tài khoản thành công",
            f"Đã import {result['imported']} tài khoản (bỏ qua {result['skipped']} trùng lặp)",
            'success',
            stats['accounts']
        )
        
        return {
            "success": True,
            "message": f"Import thành công {result['imported']} tài khoản, bỏ qua {result['skipped']} trùng lặp",
            "total_imported": result['imported'],
            "total_parsed": len(accounts_data),
            "skipped": result['skipped'],
            "skipped_uids": result['skipped_uids'],
            "statistics": stats['accounts']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi import file: {str(e)}")

@app.post("/api/accounts/{account_id}/check-status")
async def check_account_status(account_id: int, db: AsyncSession = Depends(get_db)):
    """Kiểm tra trạng thái tài khoản (live/die)"""
    try:
        result = await crud.check_account_status(db, account_id)
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        # Create log
        await crud.create_log(db, {
            'action': 'check_account_status',
            'message': f"Kiểm tra tài khoản {result['uid']}: {result['status']}",
            'level': 'info',
            'metadata': result
        })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi kiểm tra tài khoản: {str(e)}")

@app.post("/api/accounts/check-status-bulk")
async def check_accounts_status_bulk(
    account_ids: Optional[List[int]] = None,
    db: AsyncSession = Depends(get_db)
):
    """Kiểm tra trạng thái nhiều tài khoản"""
    try:
        results = await crud.bulk_check_accounts_status(db, account_ids)
        
        # Count live/die
        live_count = sum(1 for r in results if r.get('is_live'))
        die_count = len(results) - live_count
        
        # Create log
        await crud.create_log(db, {
            'action': 'bulk_check_accounts',
            'message': f"Kiểm tra {len(results)} tài khoản: {live_count} live, {die_count} die",
            'level': 'info',
            'metadata': {'live': live_count, 'die': die_count}
        })
        
        # Send notification
        telegram_bot.send_notification(
            "Kiểm tra tài khoản hàng loạt",
            f"Đã kiểm tra {len(results)} tài khoản",
            'info',
            {'Live': live_count, 'Die': die_count}
        )
        
        return {
            "success": True,
            "total_checked": len(results),
            "live_count": live_count,
            "die_count": die_count,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi kiểm tra tài khoản: {str(e)}")

@app.put("/api/accounts/{account_id}/assign-proxy")
async def assign_proxy(
    account_id: int,
    proxy_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Gán proxy cho tài khoản (proxy_id=None để gỡ proxy)"""
    try:
        account = await crud.assign_proxy_to_account(db, account_id, proxy_id)
        if not account:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
        
        # Create log
        action = "assign_proxy" if proxy_id else "remove_proxy"
        message = f"Gán proxy {proxy_id} cho tài khoản {account.uid}" if proxy_id else f"Gỡ proxy khỏi tài khoản {account.uid}"
        
        await crud.create_log(db, {
            'action': action,
            'message': message,
            'level': 'info',
            'metadata': {'account_id': account_id, 'proxy_id': proxy_id}
        })
        
        return {
            "success": True,
            "message": message,
            "account": AccountResponse.from_orm(account)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi gán proxy: {str(e)}")

# ============================================
# PROXY MANAGEMENT
# ============================================

@app.post("/api/proxies", response_model=ProxyResponse)
async def create_proxy(proxy: ProxyCreate, db: AsyncSession = Depends(get_db)):
    """Tạo proxy mới"""
    try:
        db_proxy = await crud.create_proxy(db, proxy.dict())
        return db_proxy
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo proxy: {str(e)}")

@app.get("/api/proxies", response_model=List[ProxyResponse])
async def get_proxies(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Lấy danh sách proxy"""
    proxies = await crud.get_proxies(db, skip=skip, limit=limit)
    return proxies

@app.delete("/api/proxies/{proxy_id}")
async def delete_proxy(proxy_id: int, db: AsyncSession = Depends(get_db)):
    """Xóa proxy"""
    success = await crud.delete_proxy(db, proxy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy proxy")
    return {"success": True, "message": "Đã xóa proxy"}

@app.post("/api/proxies/import-txt")
async def import_proxy_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Import proxy từ file proxy.txt"""
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Parse file
        proxies_data = parse_proxy_txt(content_str)
        
        if not proxies_data:
            raise HTTPException(status_code=400, detail="Không tìm thấy dữ liệu hợp lệ trong file")
        
        # Validate and filter valid proxies
        valid_proxies = [proxy for proxy in proxies_data if validate_proxy_data(proxy)]
        
        if not valid_proxies:
            raise HTTPException(status_code=400, detail="Không có proxy hợp lệ để import")
        
        # Bulk create proxies
        created_count = await crud.bulk_create_proxies(db, valid_proxies)
        
        # Get statistics
        stats = get_import_stats([], valid_proxies)
        
        # Create log
        await crud.create_log(db, {
            'action': 'import_proxies',
            'message': f"Import thành công {created_count} proxy từ file proxy.txt",
            'level': 'success',
            'metadata': stats
        })
        
        return {
            "success": True,
            "message": f"Import thành công {created_count} proxy",
            "total_imported": created_count,
            "total_parsed": len(proxies_data),
            "statistics": stats['proxies']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi import file: {str(e)}")

@app.post("/api/proxies/assign/{account_id}/{proxy_id}")
async def assign_proxy(account_id: int, proxy_id: int, db: AsyncSession = Depends(get_db)):
    """Gán proxy cho tài khoản"""
    try:
        # Check if account and proxy exist
        account = await crud.get_account(db, account_id)
        proxy = await crud.get_proxy(db, proxy_id)
        
        if not account:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
        if not proxy:
            raise HTTPException(status_code=404, detail="Không tìm thấy proxy")
        
        # Update account with proxy
        await crud.update_account(db, account_id, {'proxy_id': proxy_id})
        
        # Create log
        await crud.create_log(db, {
            'account_id': account_id,
            'action': 'assign_proxy',
            'message': f"Gán proxy {proxy.ip}:{proxy.port} cho tài khoản {account.username}",
            'level': 'info'
        })
        
        return {
            "success": True,
            "message": "Đã gán proxy cho tài khoản"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi gán proxy: {str(e)}")

@app.post("/api/proxies/auto-assign")
async def auto_assign_proxies(db: AsyncSession = Depends(get_db)):
    """Tự động gán proxy cho các tài khoản chưa có proxy"""
    try:
        # Get accounts without proxy
        accounts = await crud.get_accounts(db, limit=1000)
        accounts_without_proxy = [acc for acc in accounts if not acc.proxy_id]
        
        # Get available proxies
        proxies = await crud.get_proxies(db, limit=1000)
        active_proxies = [p for p in proxies if p.status == 'active']
        
        if not active_proxies:
            raise HTTPException(status_code=400, detail="Không có proxy khả dụng")
        
        # Assign proxies in round-robin
        assigned_count = 0
        for i, account in enumerate(accounts_without_proxy):
            proxy = active_proxies[i % len(active_proxies)]
            await crud.update_account(db, account.id, {'proxy_id': proxy.id})
            assigned_count += 1
        
        # Create log
        await crud.create_log(db, {
            'action': 'auto_assign_proxies',
            'message': f"Tự động gán proxy cho {assigned_count} tài khoản",
            'level': 'success'
        })
        
        return {
            "success": True,
            "message": f"Đã gán proxy cho {assigned_count} tài khoản",
            "assigned_count": assigned_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi gán proxy tự động: {str(e)}")

# ============================================
# TASK MANAGEMENT
# ============================================

@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task_req: TaskRequest, db: AsyncSession = Depends(get_db)):
    """Tạo tác vụ mới"""
    try:
        # Check if account exists
        account = await crud.get_account(db, task_req.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
        
        # Create task
        task_id = f"{task_req.task_type}_{int(datetime.now().timestamp())}"
        task = await crud.create_task(db, {
            'task_id': task_id,
            'account_id': task_req.account_id,
            'task_type': task_req.task_type,
            'task_name': task_req.task_type.replace('_', ' ').title(),
            'params': task_req.params or {}
        })
        
        # Create log
        await crud.create_log(db, {
            'account_id': task_req.account_id,
            'task_id': task_id,
            'action': 'create_task',
            'message': f"Tạo tác vụ {task_req.task_type}",
            'level': 'info'
        })
        
        # Send Telegram notification
        telegram_bot.send_task_notification(
            task_req.task_type,
            account.username or account.uid,
            'processing',
            {'task_id': task_id}
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Đã tạo tác vụ {task_req.task_type}",
            "status": "pending"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo tác vụ: {str(e)}")

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str, db: AsyncSession = Depends(get_db)):
    """Lấy trạng thái tác vụ"""
    task = await crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Không tìm thấy tác vụ")
    
    return {
        "task_id": task.task_id,
        "status": task.status,
        "progress": task.progress,
        "message": f"Tác vụ đang {task.status}"
    }

@app.get("/api/tasks")
async def get_tasks(
    account_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách tác vụ"""
    tasks = await crud.get_tasks(db, account_id=account_id, status=status, skip=skip, limit=limit)
    return tasks

# ============================================
# ACTIVITY LOGS
# ============================================

@app.get("/api/logs")
async def get_logs(
    account_id: Optional[int] = None,
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Lấy nhật ký hoạt động"""
    logs = await crud.get_logs(db, account_id=account_id, level=level, skip=skip, limit=limit)
    return logs

# ============================================
# FACEBOOK AUTOMATION ENDPOINTS
# ============================================

@app.post("/api/groups/join")
async def join_groups(data: Dict, db: AsyncSession = Depends(get_db)):
    """Tham gia nhóm"""
    task_req = TaskRequest(
        task_type="join_groups",
        account_id=data['account_id'],
        params={'group_list': data.get('group_list', []), 'delay': data.get('delay', 10)}
    )
    return await create_task(task_req, db)

@app.post("/api/groups/leave")
async def leave_groups(data: Dict, db: AsyncSession = Depends(get_db)):
    """Rời nhóm"""
    task_req = TaskRequest(
        task_type="leave_groups",
        account_id=data['account_id'],
        params={'group_list': data.get('group_list', [])}
    )
    return await create_task(task_req, db)

@app.post("/api/friends/add")
async def add_friends(data: Dict, db: AsyncSession = Depends(get_db)):
    """Kết bạn"""
    task_req = TaskRequest(
        task_type="add_friends",
        account_id=data['account_id'],
        params={'uid_list': data.get('uid_list', [])}
    )
    return await create_task(task_req, db)

@app.post("/api/posts/create")
async def create_post(data: Dict, db: AsyncSession = Depends(get_db)):
    """Đăng bài viết"""
    task_req = TaskRequest(
        task_type="create_post",
        account_id=data['account_id'],
        params={'content': data.get('content', ''), 'images': data.get('images', [])}
    )
    return await create_task(task_req, db)

# ============================================
# STATISTICS
# ============================================

@app.get("/api/stats")
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """Lấy thống kê tổng quan"""
    accounts = await crud.get_accounts(db, limit=10000)
    proxies = await crud.get_proxies(db, limit=10000)
    tasks = await crud.get_tasks(db, limit=10000)
    
    return {
        "accounts": {
            "total": len(accounts),
            "active": len([a for a in accounts if a.status == 'active']),
            "inactive": len([a for a in accounts if a.status == 'inactive']),
            "with_proxy": len([a for a in accounts if a.proxy_id])
        },
        "proxies": {
            "total": len(proxies),
            "active": len([p for p in proxies if p.status == 'active'])
        },
        "tasks": {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.status == 'pending']),
            "processing": len([t for t in tasks if t.status == 'processing']),
            "completed": len([t for t in tasks if t.status == 'completed']),
            "failed": len([t for t in tasks if t.status == 'failed'])
        }
    }

# ============================================
# SETTINGS MANAGEMENT
# ============================================

@app.get("/api/settings")
async def get_settings(db: AsyncSession = Depends(get_db)):
    """Get application settings"""
    # Get settings from database or return defaults
    settings = await crud.get_settings(db) if hasattr(crud, 'get_settings') else {}
    
    # Return default settings if not in database
    default_settings = {
        "databaseType": "sqlite",
        "autoBackup": True,
        "facebookAppId": os.getenv('FACEBOOK_APP_ID', ''),
        "webhookVerifyToken": os.getenv('FACEBOOK_VERIFY_TOKEN', ''),
        "telegramBotToken": os.getenv('TELEGRAM_BOT_TOKEN', ''),
        "telegramChatId": os.getenv('TELEGRAM_CHAT_ID', ''),
        "notifyTaskComplete": True,
        "notifyTaskFailed": True,
        "notifyError": True,
        "notifyWebhook": False,
        "headlessMode": False,
        "maxConcurrent": 5,
        "taskTimeout": 300,
        "proxyRotation": "round-robin",
        "proxyTimeout": 30,
        "autoAssignProxy": True,
        "delayMin": 5,
        "delayMax": 15,
        "maxActionsPerHour": 100,
        "debugMode": False,
        "retryFailedTasks": True,
        "maxRetries": 3,
        "logLevel": "INFO"
    }
    
    return {**default_settings, **settings}

@app.post("/api/settings")
async def save_settings(settings: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """Save application settings"""
    try:
        # Save to database if crud method exists
        if hasattr(crud, 'save_settings'):
            await crud.save_settings(db, settings)
        
        # Create log
        await crud.create_log(db, {
            'action': 'save_settings',
            'message': 'Cập nhật cài đặt hệ thống',
            'level': 'info',
            'metadata': settings
        })
        
        return {"success": True, "message": "Đã lưu cài đặt"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lưu cài đặt: {str(e)}")

# ============================================
# TELEGRAM TEST ENDPOINT
# ============================================

@app.post("/api/telegram/test")
async def test_telegram(data: Dict[str, str]):
    """Test Telegram notification"""
    try:
        bot_token = data.get('bot_token')
        chat_id = data.get('chat_id')
        
        if not bot_token or not chat_id:
            raise HTTPException(status_code=400, detail="Missing bot_token or chat_id")
        
        # Create temporary bot instance
        from telegram_bot import TelegramBot
        test_bot = TelegramBot(bot_token=bot_token, chat_id=chat_id)
        
        # Send test message
        success = test_bot.send_notification(
            "Test thông báo",
            "Đây là tin nhắn test từ Bi Ads Multi Tool PRO v3.0",
            'success',
            {
                'Version': '3.0.0',
                'Test': 'OK'
            }
        )
        
        if success:
            return {"success": True, "message": "Đã gửi tin nhắn test thành công"}
        else:
            raise HTTPException(status_code=500, detail="Không thể gửi tin nhắn")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")

if __name__ == "__main__":
    print("🚀 Bi Ads Multi Tool PRO - Backend API v2.0")
    print("📡 Starting server on http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")
    print("💾 Database: SQLite (bi_ads.db)")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
