# 📚 Hướng Dẫn Sử Dụng Database - Bi Ads Multi Tool PRO

## 📋 Mục Lục
1. [Giới thiệu Database](#giới-thiệu)
2. [Cấu trúc Database](#cấu-trúc-database)
3. [Cách sử dụng trên máy tính](#cách-sử-dụng-trên-máy-tính)
4. [Công cụ quản lý Database](#công-cụ-quản-lý)
5. [Thao tác SQL cơ bản](#thao-tác-sql)
6. [Backup và Restore](#backup-restore)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Giới Thiệu Database

### Thông Tin Cơ Bản
- **Database Engine:** SQLite (async với aiosqlite)
- **Location:** `/home/bighitran1905/webapp/backend/data/bi_ads.db`
- **Size hiện tại:** ~220KB
- **ORM:** SQLAlchemy với async support

### Tại Sao Dùng SQLite?
✅ **Không cần cài đặt server riêng**  
✅ **File-based - dễ backup**  
✅ **Nhẹ và nhanh cho desktop app**  
✅ **Cross-platform - chạy mọi OS**  
✅ **Tích hợp sẵn trong Python**

---

## 🗄️ Cấu Trúc Database

### 1. Bảng Chính (Core Tables)

#### `accounts` - Tài khoản Facebook
```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    uid VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(255),
    name VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255),
    cookies TEXT,
    access_token TEXT,
    two_fa_key VARCHAR(100),
    proxy_id INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    method VARCHAR(50) DEFAULT 'cookies',
    created_at DATETIME,
    updated_at DATETIME,
    last_used DATETIME,
    FOREIGN KEY(proxy_id) REFERENCES proxies(id)
);
```

**Các trạng thái:**
- `active` - Hoạt động bình thường
- `inactive` - Tạm ngưng
- `locked` - Bị khóa
- `checkpoint` - Checkpoint Facebook

#### `proxies` - Danh sách Proxy
```sql
CREATE TABLE proxies (
    id INTEGER PRIMARY KEY,
    ip VARCHAR(50) NOT NULL,
    port INTEGER NOT NULL,
    username VARCHAR(100),
    password VARCHAR(255),
    protocol VARCHAR(20) DEFAULT 'http',
    status VARCHAR(50) DEFAULT 'active',
    location VARCHAR(100),
    speed INTEGER,
    last_checked DATETIME,
    created_at DATETIME
);
```

**Protocols hỗ trợ:**
- `http` - HTTP proxy
- `https` - HTTPS proxy
- `socks5` - SOCKS5 proxy

#### `tasks` - Tác vụ automation
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE,
    account_id INTEGER NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    task_name VARCHAR(255),
    params TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    result TEXT,
    error_message TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME,
    FOREIGN KEY(account_id) REFERENCES accounts(id)
);
```

**Task types:**
- `join_groups` - Tham gia nhóm
- `add_friends` - Kết bạn
- `auto_post` - Đăng bài tự động
- `auto_comment` - Comment tự động
- `auto_like` - Like tự động

#### `activity_logs` - Nhật ký hoạt động
```sql
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY,
    account_id INTEGER,
    task_id VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    level VARCHAR(20) DEFAULT 'info',
    extra_data TEXT,
    created_at DATETIME,
    FOREIGN KEY(account_id) REFERENCES accounts(id)
);
```

**Log levels:**
- `info` - Thông tin
- `success` - Thành công
- `warning` - Cảnh báo
- `error` - Lỗi

#### `settings` - Cài đặt ứng dụng
```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME
);
```

### 2. Bảng Nâng Cao (Advanced Tables)

#### `sub_accounts` - Tài khoản phụ
Tài khoản phụ dùng để tương tác với tài khoản chính (auto like, comment, share)

#### `facebook_ids` - Quản lý UID
Lưu trữ Facebook UID thu thập từ groups, posts, friends

#### `ip_addresses` - Quản lý IP
Theo dõi IP truy cập và bảo mật

#### `whitelist_accounts` - Whitelist
Tài khoản VIP không bị tương tác tiêu cực

#### `posted_content` - Bài viết đã đăng
Quản lý nội dung đã post

#### `messages` - Tin nhắn
Quản lý inbox và auto reply

#### `auto_reply_templates` - Template tự động
Template tin nhắn tự động trả lời

---

## 💻 Cách Sử Dụng Trên Máy Tính

### Phương Pháp 1: Sử Dụng DB Browser for SQLite (KHUYẾN NGHỊ)

#### Bước 1: Download và cài đặt
**Windows:**
```bash
# Tải từ: https://sqlitebrowser.org/dl/
# Hoặc dùng winget:
winget install DB.Browser.SQLite
```

**macOS:**
```bash
brew install --cask db-browser-for-sqlite
```

**Linux:**
```bash
sudo apt install sqlitebrowser
# Hoặc
sudo snap install sqlitebrowser
```

#### Bước 2: Mở Database
1. Mở ứng dụng **DB Browser for SQLite**
2. Click **"Open Database"**
3. Navigate đến: `/home/bighitran1905/webapp/backend/data/bi_ads.db`
4. Click **"Open"**

#### Bước 3: Xem và chỉnh sửa dữ liệu
- Tab **"Browse Data"**: Xem và edit dữ liệu bảng
- Tab **"Execute SQL"**: Chạy câu lệnh SQL
- Tab **"Database Structure"**: Xem cấu trúc bảng

### Phương Pháp 2: Sử Dụng SQLite CLI

#### Cài đặt SQLite CLI
```bash
# Kiểm tra đã có chưa
sqlite3 --version

# Nếu chưa có:
# Ubuntu/Debian:
sudo apt install sqlite3

# macOS:
brew install sqlite

# Windows: Download từ https://www.sqlite.org/download.html
```

#### Kết nối Database
```bash
# Navigate to project directory
cd /home/bighitran1905/webapp/backend/data

# Mở database
sqlite3 bi_ads.db
```

#### Commands cơ bản
```sql
-- Xem danh sách bảng
.tables

-- Xem cấu trúc bảng
.schema accounts

-- Enable headers
.headers on

-- Pretty print
.mode column

-- Xem tất cả accounts
SELECT * FROM accounts;

-- Đếm số accounts
SELECT COUNT(*) FROM accounts;

-- Thoát
.quit
```

### Phương Pháp 3: Sử Dụng Python Script

#### Tạo file `db_viewer.py`
```python
import sqlite3
import pandas as pd
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "backend" / "data" / "bi_ads.db"

def connect_db():
    """Kết nối database"""
    return sqlite3.connect(DB_PATH)

def view_accounts():
    """Xem tất cả tài khoản"""
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM accounts", conn)
    conn.close()
    print(df)
    return df

def view_proxies():
    """Xem tất cả proxy"""
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM proxies", conn)
    conn.close()
    print(df)
    return df

def view_tasks():
    """Xem tất cả tasks"""
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM tasks ORDER BY created_at DESC", conn)
    conn.close()
    print(df)
    return df

def view_logs(limit=50):
    """Xem logs gần nhất"""
    conn = connect_db()
    query = f"SELECT * FROM activity_logs ORDER BY created_at DESC LIMIT {limit}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    print(df)
    return df

def custom_query(sql):
    """Chạy custom SQL query"""
    conn = connect_db()
    try:
        df = pd.read_sql_query(sql, conn)
        print(df)
        return df
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== BI ADS DATABASE VIEWER ===\n")
    
    print("1. Accounts:")
    view_accounts()
    
    print("\n2. Proxies:")
    view_proxies()
    
    print("\n3. Recent Tasks:")
    view_tasks()
    
    print("\n4. Recent Logs:")
    view_logs(20)
```

**Chạy script:**
```bash
cd /home/bighitran1905/webapp
python db_viewer.py
```

---

## 🛠️ Công Cụ Quản Lý Database

### 1. Tích hợp sẵn trong Backend API

Backend đã có sẵn API endpoints để quản lý database:

```bash
# Health check (bao gồm database status)
curl http://localhost:8000/health

# Lấy tất cả accounts
curl http://localhost:8000/api/accounts

# Lấy tất cả proxies
curl http://localhost:8000/api/proxies

# Lấy statistics
curl http://localhost:8000/api/stats
```

### 2. Python Async Functions

Sử dụng CRUD functions có sẵn trong `backend/crud.py`:

```python
from backend.crud import *
from backend.core.database import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as db:
        # Lấy tất cả accounts
        accounts = await get_accounts(db)
        
        # Tìm account theo ID
        account = await get_account(db, account_id=1)
        
        # Tạo account mới
        new_account = await create_account(db, account_data)
        
        # Update account
        updated = await update_account(db, account_id=1, updates)
        
        # Delete account
        deleted = await delete_account(db, account_id=1)
```

---

## 📝 Thao Tác SQL Cơ Bản

### 1. Xem Dữ Liệu (SELECT)

```sql
-- Xem tất cả accounts
SELECT * FROM accounts;

-- Xem accounts với proxy
SELECT a.id, a.name, a.uid, a.status, p.ip, p.port
FROM accounts a
LEFT JOIN proxies p ON a.proxy_id = p.id;

-- Xem accounts active
SELECT * FROM accounts WHERE status = 'active';

-- Đếm accounts theo status
SELECT status, COUNT(*) as count
FROM accounts
GROUP BY status;

-- Xem 10 logs gần nhất
SELECT * FROM activity_logs
ORDER BY created_at DESC
LIMIT 10;

-- Xem tasks đang chạy
SELECT * FROM tasks
WHERE status IN ('pending', 'processing')
ORDER BY created_at DESC;
```

### 2. Thêm Dữ Liệu (INSERT)

```sql
-- Thêm account mới
INSERT INTO accounts (uid, name, username, email, status, method)
VALUES ('100012345678901', 'Nguyen Van A', 'nguyenvana', 'nguyenvana@email.com', 'active', 'cookies');

-- Thêm proxy mới
INSERT INTO proxies (ip, port, username, password, protocol, status)
VALUES ('123.45.67.89', 8080, 'proxy_user', 'proxy_pass', 'http', 'active');

-- Thêm task mới
INSERT INTO tasks (task_id, account_id, task_type, task_name, status)
VALUES ('TASK-12345', 1, 'join_groups', 'Join 10 groups', 'pending');
```

### 3. Cập Nhật Dữ Liệu (UPDATE)

```sql
-- Cập nhật status account
UPDATE accounts
SET status = 'inactive', updated_at = CURRENT_TIMESTAMP
WHERE id = 1;

-- Gán proxy cho account
UPDATE accounts
SET proxy_id = 5, updated_at = CURRENT_TIMESTAMP
WHERE id = 1;

-- Cập nhật progress task
UPDATE tasks
SET progress = 50, status = 'processing'
WHERE task_id = 'TASK-12345';

-- Update last_used cho account
UPDATE accounts
SET last_used = CURRENT_TIMESTAMP
WHERE id = 1;
```

### 4. Xóa Dữ Liệu (DELETE)

```sql
-- Xóa account (cẩn thận!)
DELETE FROM accounts WHERE id = 999;

-- Xóa logs cũ hơn 30 ngày
DELETE FROM activity_logs
WHERE created_at < datetime('now', '-30 days');

-- Xóa tasks đã hoàn thành
DELETE FROM tasks
WHERE status = 'completed' AND completed_at < datetime('now', '-7 days');

-- Xóa proxy không hoạt động
DELETE FROM proxies
WHERE status = 'inactive';
```

### 5. Queries Nâng Cao

```sql
-- Thống kê accounts theo status
SELECT 
    status,
    COUNT(*) as total,
    COUNT(proxy_id) as with_proxy,
    COUNT(*) - COUNT(proxy_id) as without_proxy
FROM accounts
GROUP BY status;

-- Top 5 accounts có nhiều tasks nhất
SELECT 
    a.name,
    a.uid,
    COUNT(t.id) as total_tasks
FROM accounts a
LEFT JOIN tasks t ON a.id = t.account_id
GROUP BY a.id
ORDER BY total_tasks DESC
LIMIT 5;

-- Tasks success rate
SELECT 
    task_type,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
    ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM tasks
GROUP BY task_type;

-- Logs theo level trong 24h
SELECT 
    level,
    COUNT(*) as count
FROM activity_logs
WHERE created_at > datetime('now', '-1 day')
GROUP BY level;

-- Proxies và số accounts đang dùng
SELECT 
    p.id,
    p.ip || ':' || p.port as proxy_address,
    p.protocol,
    p.status,
    COUNT(a.id) as accounts_using
FROM proxies p
LEFT JOIN accounts a ON p.id = a.proxy_id
GROUP BY p.id
ORDER BY accounts_using DESC;
```

---

## 💾 Backup và Restore

### 1. Backup Database

#### Phương pháp 1: Copy file
```bash
# Backup đơn giản - copy file
cp backend/data/bi_ads.db backend/data/bi_ads_backup_$(date +%Y%m%d_%H%M%S).db

# Hoặc tạo thư mục backup riêng
mkdir -p backups
cp backend/data/bi_ads.db backups/bi_ads_$(date +%Y%m%d_%H%M%S).db
```

#### Phương pháp 2: SQLite dump
```bash
# Backup toàn bộ database thành SQL file
sqlite3 backend/data/bi_ads.db .dump > backups/bi_ads_backup.sql

# Nén lại để tiết kiệm dung lượng
sqlite3 backend/data/bi_ads.db .dump | gzip > backups/bi_ads_backup_$(date +%Y%m%d).sql.gz
```

#### Phương pháp 3: Tự động backup
Tạo file `backup_database.sh`:
```bash
#!/bin/bash

# Configuration
DB_PATH="backend/data/bi_ads.db"
BACKUP_DIR="backups"
MAX_BACKUPS=10

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup filename with timestamp
BACKUP_FILE="$BACKUP_DIR/bi_ads_$(date +%Y%m%d_%H%M%S).db"

# Create backup
cp "$DB_PATH" "$BACKUP_FILE"

# Compress
gzip "$BACKUP_FILE"

echo "✅ Backup created: ${BACKUP_FILE}.gz"

# Delete old backups (keep only MAX_BACKUPS)
ls -t "$BACKUP_DIR"/bi_ads_*.db.gz | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm

echo "✅ Cleanup completed. Keeping $MAX_BACKUPS most recent backups."
```

Chạy script:
```bash
chmod +x backup_database.sh
./backup_database.sh
```

### 2. Restore Database

#### Từ file backup
```bash
# Stop backend trước
# Restore từ backup file
cp backups/bi_ads_20251116.db backend/data/bi_ads.db

# Hoặc từ file nén
gunzip -c backups/bi_ads_20251116.db.gz > backend/data/bi_ads.db
```

#### Từ SQL dump
```bash
# Stop backend trước
# Xóa database cũ (optional)
rm backend/data/bi_ads.db

# Restore từ SQL dump
sqlite3 backend/data/bi_ads.db < backups/bi_ads_backup.sql

# Hoặc từ file nén
gunzip -c backups/bi_ads_backup.sql.gz | sqlite3 backend/data/bi_ads.db
```

### 3. Tự động backup định kỳ (Cron Job)

```bash
# Mở crontab
crontab -e

# Thêm dòng này để backup mỗi ngày lúc 2 giờ sáng
0 2 * * * /home/bighitran1905/webapp/backup_database.sh >> /home/bighitran1905/webapp/backups/backup.log 2>&1
```

---

## 🔧 Troubleshooting

### Lỗi 1: Database is locked

**Nguyên nhân:** Có process khác đang truy cập database

**Giải pháp:**
```bash
# Kiểm tra process đang dùng database
lsof backend/data/bi_ads.db

# Hoặc
fuser backend/data/bi_ads.db

# Stop backend và thử lại
# Nếu vẫn bị lock, restart máy hoặc kill process
```

### Lỗi 2: Database file is corrupted

**Giải pháp:**
```bash
# Check integrity
sqlite3 backend/data/bi_ads.db "PRAGMA integrity_check;"

# Nếu corrupted, restore từ backup
cp backups/bi_ads_latest.db backend/data/bi_ads.db

# Hoặc dump và recreate
sqlite3 backend/data/bi_ads.db ".recover" | sqlite3 backend/data/bi_ads_recovered.db
```

### Lỗi 3: Cannot find database file

**Giải pháp:**
```bash
# Kiểm tra đường dẫn
ls -la backend/data/bi_ads.db

# Nếu không tồn tại, khởi tạo lại
cd backend
python -c "
import asyncio
from core.database import init_db
asyncio.run(init_db())
"
```

### Lỗi 4: Performance chậm

**Giải pháp:**
```sql
-- Analyze database
ANALYZE;

-- Vacuum để optimize
VACUUM;

-- Rebuild indexes
REINDEX;
```

---

## 📊 Monitoring Database

### 1. Xem Database Size
```bash
# Total size
du -h backend/data/bi_ads.db

# Detailed info
sqlite3 backend/data/bi_ads.db "PRAGMA page_count; PRAGMA page_size;"
```

### 2. Check Performance
```sql
-- Query plan
EXPLAIN QUERY PLAN SELECT * FROM accounts WHERE status = 'active';

-- Index usage
SELECT * FROM sqlite_master WHERE type = 'index';

-- Table info
PRAGMA table_info(accounts);
```

### 3. Statistics
```sql
-- Row counts cho tất cả tables
SELECT 'accounts' as table_name, COUNT(*) as rows FROM accounts
UNION ALL
SELECT 'proxies', COUNT(*) FROM proxies
UNION ALL
SELECT 'tasks', COUNT(*) FROM tasks
UNION ALL
SELECT 'activity_logs', COUNT(*) FROM activity_logs;

-- Database size per table
SELECT 
    name,
    SUM("pgsize") as size
FROM "dbstat"
GROUP BY name
ORDER BY size DESC;
```

---

## 🎓 Best Practices

### 1. Bảo mật
- ✅ Backup database thường xuyên
- ✅ Không commit database file lên Git
- ✅ Mã hóa passwords và sensitive data
- ✅ Giới hạn quyền truy cập file

### 2. Performance
- ✅ Sử dụng indexes hợp lý
- ✅ Định kỳ VACUUM database
- ✅ Clean up old logs và completed tasks
- ✅ Batch operations khi possible

### 3. Maintenance
- ✅ Backup tự động hàng ngày
- ✅ Monitor database size
- ✅ Clean up logs > 30 ngày
- ✅ Check integrity định kỳ

---

## 🔗 Resources

- **SQLite Documentation:** https://www.sqlite.org/docs.html
- **DB Browser for SQLite:** https://sqlitebrowser.org/
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/
- **Python sqlite3:** https://docs.python.org/3/library/sqlite3.html

---

## 📞 Support

Nếu gặp vấn đề với database:
1. Check logs trong `backend/logs/`
2. Verify database integrity
3. Restore từ backup gần nhất
4. Liên hệ support team

---

**Last Updated:** 2025-11-16  
**Version:** 1.0.0  
**Author:** Bi Ads Development Team
