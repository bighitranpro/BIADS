"""
Bi Ads - Database Configuration
Author: Bi Ads Team
Version: 2.0.0
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.pool import StaticPool
from datetime import datetime
import os

# Database URL - Using SQLite for simplicity, can be changed to PostgreSQL
# Database is stored in data/ directory
from pathlib import Path
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DATA_DIR}/bi_ads.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=True  # Set to False in production
)

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Database Models
class Account(Base):
    """Tài khoản Facebook"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(50), unique=True, index=True, nullable=False)
    username = Column(String(255))
    name = Column(String(255))
    email = Column(String(255))
    password = Column(String(255))  # Encrypted
    cookies = Column(Text)  # JSON string
    access_token = Column(Text)
    two_fa_key = Column(String(100))
    proxy_id = Column(Integer, ForeignKey('proxies.id'), nullable=True)
    status = Column(String(50), default='active')  # active, inactive, locked, checkpoint
    method = Column(String(50), default='cookies')  # cookies, email, token
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_used = Column(DateTime, nullable=True)
    
    # Relationships
    proxy = relationship("Proxy", back_populates="accounts")
    tasks = relationship("Task", back_populates="account")
    logs = relationship("ActivityLog", back_populates="account")

class Proxy(Base):
    """Proxy Server"""
    __tablename__ = "proxies"
    
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(50), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(100), nullable=True)
    password = Column(String(255), nullable=True)  # Encrypted
    protocol = Column(String(20), default='http')  # http, https, socks5
    status = Column(String(50), default='active')  # active, inactive, error
    location = Column(String(100), nullable=True)
    speed = Column(Integer, nullable=True)  # ms
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    accounts = relationship("Account", back_populates="proxy")

class Task(Base):
    """Tác vụ automation"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), unique=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    task_type = Column(String(100), nullable=False)  # join_groups, add_friends, etc.
    task_name = Column(String(255))
    params = Column(Text)  # JSON string
    status = Column(String(50), default='pending')  # pending, processing, completed, failed, cancelled
    progress = Column(Integer, default=0)  # 0-100
    result = Column(Text, nullable=True)  # JSON string
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    account = relationship("Account", back_populates="tasks")

class ActivityLog(Base):
    """Nhật ký hoạt động"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    task_id = Column(String(100), nullable=True)
    action = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    level = Column(String(20), default='info')  # info, success, warning, error
    extra_data = Column(Text, nullable=True)  # JSON string (renamed from metadata to avoid SQLAlchemy conflict)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    account = relationship("Account", back_populates="logs")

class Settings(Base):
    """Cài đặt ứng dụng"""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# Advanced Features Models

class SubAccount(Base):
    """Tài khoản phụ - Tài khoản phụ dùng để tương tác với tài khoản chính"""
    __tablename__ = "sub_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    main_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    uid = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255))
    username = Column(String(255))
    cookies = Column(Text)  # JSON string
    access_token = Column(Text)
    status = Column(String(50), default='active')  # active, inactive, banned
    auto_like = Column(Boolean, default=True)
    auto_comment = Column(Boolean, default=False)
    auto_share = Column(Boolean, default=False)
    interaction_count = Column(Integer, default=0)
    last_interaction = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    main_account = relationship("Account", foreign_keys=[main_account_id])

class FacebookID(Base):
    """Quản lý Facebook ID/UID"""
    __tablename__ = "facebook_ids"
    
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255))
    username = Column(String(255))
    profile_url = Column(String(500))
    status = Column(String(50), default='valid')  # valid, invalid, used
    is_friend = Column(Boolean, default=False)
    source = Column(String(100))  # manual, import, scan_group, scan_post
    source_id = Column(String(100), nullable=True)  # Group ID or Post ID
    collected_by_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    collected_by = relationship("Account", foreign_keys=[collected_by_account_id])

class IPAddress(Base):
    """Quản lý IP thiết bị"""
    __tablename__ = "ip_addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(50), unique=True, index=True, nullable=False)
    location = Column(String(255))  # City, Country
    country_code = Column(String(10))
    status = Column(String(50), default='active')  # active, blocked, trusted
    is_proxy = Column(Boolean, default=False)
    used_by_accounts = Column(Text)  # JSON array of account IDs
    first_seen = Column(DateTime, default=datetime.now)
    last_seen = Column(DateTime, default=datetime.now)
    access_count = Column(Integer, default=0)
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
class WhitelistAccount(Base):
    """Tài khoản whitelist - Tài khoản được bảo vệ không bị tương tác tiêu cực"""
    __tablename__ = "whitelist_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255))
    username = Column(String(255))
    type = Column(String(50), default='friend')  # vip, customer, partner, admin, friend
    status = Column(String(50), default='active')  # active, inactive
    friendship_status = Column(String(50), default='friend')  # friend, not_friend, pending
    auto_accept_request = Column(Boolean, default=True)
    auto_like_posts = Column(Boolean, default=True)
    priority_messaging = Column(Boolean, default=False)
    never_unfriend = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    added_by_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    added_by = relationship("Account", foreign_keys=[added_by_account_id])

class PostedContent(Base):
    """Quản lý bài viết đã đăng"""
    __tablename__ = "posted_content"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String(100), unique=True, index=True, nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    content = Column(Text)
    post_url = Column(String(500))
    post_type = Column(String(50), default='text')  # text, image, video, link
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    status = Column(String(50), default='published')  # published, hidden, deleted
    posted_at = Column(DateTime, default=datetime.now)
    last_updated = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    account = relationship("Account", foreign_keys=[account_id])

class Message(Base):
    """Quản lý tin nhắn"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), index=True, nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    sender_uid = Column(String(50), nullable=False)
    sender_name = Column(String(255))
    receiver_uid = Column(String(50), nullable=False)
    receiver_name = Column(String(255))
    message_text = Column(Text)
    message_type = Column(String(50), default='text')  # text, image, sticker, link
    is_read = Column(Boolean, default=False)
    is_sent_by_me = Column(Boolean, default=False)
    auto_reply_enabled = Column(Boolean, default=False)
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    account = relationship("Account", foreign_keys=[account_id])

class AutoReplyTemplate(Base):
    """Template tin nhắn tự động trả lời"""
    __tablename__ = "auto_reply_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    name = Column(String(255), nullable=False)
    trigger_keywords = Column(Text)  # JSON array of keywords
    reply_message = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    use_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    account = relationship("Account", foreign_keys=[account_id])

# Dependency to get DB session
async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Initialize database
async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized successfully!")

# Drop all tables (for development only)
async def drop_db():
    """Drop all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("⚠️  All database tables dropped!")
