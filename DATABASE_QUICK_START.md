# 🚀 Database Quick Start Guide

## 📍 Vị Trí Database

```
/home/bighitran1905/webapp/backend/data/bi_ads.db
```

**Loại:** SQLite (220KB)  
**Số bảng:** 12 tables  
**Dữ liệu hiện tại:** 35 accounts, 60 proxies, 33 logs

---

## 🔥 Cách Sử Dụng Nhanh (3 Phút)

### ⚡ Phương Pháp 1: Script Python (Khuyến nghị)

```bash
# Xem toàn bộ database
python3 quick_db_view.py

# Hoặc xem chi tiết với menu
python3 db_viewer.py
```

**Output mẫu:**
```
================================================================================
  BI ADS DATABASE - QUICK VIEW
================================================================================

📊 DATABASE INFO:
   Path: /home/bighitran1905/webapp/backend/data/bi_ads.db
   Size: 220.00 KB

📋 TABLES:
   - accounts: 35 rows
   - proxies: 60 rows
   - activity_logs: 33 rows
   ...

👥 ACCOUNTS (Top 10):
   ID    UID                  Name                      Status     Proxy
   ---------------------------------------------------------------------------
   1     61582525118131       mmm022                    active     ✓
   2     61583594998934       Shamim09                  active     ✓
   ...
```

### 🎯 Phương Pháp 2: DB Browser (GUI)

**Bước 1:** Download DB Browser
- Windows: https://sqlitebrowser.org/dl/
- macOS: `brew install --cask db-browser-for-sqlite`
- Linux: `sudo apt install sqlitebrowser`

**Bước 2:** Mở database
1. Launch DB Browser
2. File → Open Database
3. Select: `/home/bighitran1905/webapp/backend/data/bi_ads.db`
4. Browse Data tab để xem dữ liệu

### 💻 Phương Pháp 3: Backend API

```bash
# Start backend (nếu chưa chạy)
cd backend
python -m uvicorn main:app --reload

# Xem accounts qua API
curl http://localhost:8000/api/accounts

# Xem proxies
curl http://localhost:8000/api/proxies

# Xem statistics
curl http://localhost:8000/api/stats
```

---

## 💾 Backup & Restore

### Backup Database

```bash
# Tự động backup với timestamp và nén
./backup_database.sh
```

**Output:**
```
==========================================
  Bi Ads Database Backup
==========================================

📊 Database size: 224K
💾 Backing up database...
✅ Backup created: backups/database/bi_ads_20251116_084014.db
🗜️  Compressing backup...
✅ Compressed: bi_ads_20251116_084014.db.gz (28K)
```

**Backup được lưu tại:** `backups/database/`  
**Tự động giữ:** 30 bản backup gần nhất

### Restore Database

```bash
# Interactive restore với menu
./restore_database.sh
```

**Output:**
```
📋 Available backups:
  [1] bi_ads_20251116_084014.db.gz (27K)
  [2] bi_ads_20251115_120000.db.gz (26K)

Chọn backup để restore (1-2), hoặc 0 để hủy:
```

---

## 📝 SQL Queries Cơ Bản

### Trong Python

```python
import sqlite3

conn = sqlite3.connect('backend/data/bi_ads.db')
cursor = conn.cursor()

# Lấy tất cả accounts
cursor.execute("SELECT * FROM accounts")
accounts = cursor.fetchall()

# Lấy accounts với proxy
cursor.execute("""
    SELECT a.name, p.ip, p.port
    FROM accounts a
    JOIN proxies p ON a.proxy_id = p.id
""")
results = cursor.fetchall()

conn.close()
```

### Queries Hữu Ích

```sql
-- Xem accounts active
SELECT * FROM accounts WHERE status = 'active';

-- Đếm accounts theo status
SELECT status, COUNT(*) FROM accounts GROUP BY status;

-- Xem accounts với proxy info
SELECT a.name, a.uid, p.ip || ':' || p.port as proxy
FROM accounts a
LEFT JOIN proxies p ON a.proxy_id = p.id;

-- Xem logs gần nhất
SELECT * FROM activity_logs 
ORDER BY created_at DESC 
LIMIT 20;

-- Thống kê proxy usage
SELECT 
    p.ip || ':' || p.port as proxy,
    COUNT(a.id) as accounts_using
FROM proxies p
LEFT JOIN accounts a ON p.id = a.proxy_id
GROUP BY p.id;
```

---

## 📊 Cấu Trúc Database

### Bảng Chính

| Bảng | Mục đích | Số records |
|------|----------|------------|
| **accounts** | Tài khoản Facebook | 35 |
| **proxies** | Danh sách proxy | 60 |
| **tasks** | Tác vụ automation | 0 |
| **activity_logs** | Nhật ký hoạt động | 33 |
| **settings** | Cài đặt ứng dụng | 0 |

### Bảng Nâng Cao

| Bảng | Mục đích | Số records |
|------|----------|------------|
| **sub_accounts** | Tài khoản phụ | 9 |
| **facebook_ids** | UID thu thập | 50 |
| **ip_addresses** | Quản lý IP | 20 |
| **whitelist_accounts** | Tài khoản VIP | 30 |
| **posted_content** | Bài viết đã đăng | 40 |
| **messages** | Tin nhắn | 81 |
| **auto_reply_templates** | Template tự động | 0 |

---

## 🛠️ Troubleshooting

### ❌ Database is locked

```bash
# Kiểm tra process đang dùng
lsof backend/data/bi_ads.db

# Stop backend và thử lại
```

### ❌ Cannot find database

```bash
# Khởi tạo lại database
cd backend
python -c "
import asyncio
from core.database import init_db
asyncio.run(init_db())
"
```

### ❌ Database corrupted

```bash
# Restore từ backup
./restore_database.sh
```

---

## 📚 Chi Tiết Đầy Đủ

Xem tài liệu đầy đủ tại: **[HUONG_DAN_DATABASE.md](./HUONG_DAN_DATABASE.md)**

Bao gồm:
- ✅ Cấu trúc chi tiết tất cả bảng
- ✅ SQL queries nâng cao
- ✅ Python automation scripts
- ✅ Cron jobs cho auto backup
- ✅ Best practices
- ✅ Performance optimization

---

## ⚙️ Tự Động Backup (Optional)

### Cài đặt cron job

```bash
# Mở crontab
crontab -e

# Thêm dòng này để backup mỗi ngày lúc 2:00 AM
0 2 * * * /home/bighitran1905/webapp/backup_database.sh >> /home/bighitran1905/webapp/backups/backup.log 2>&1
```

---

## 🎯 Quick Commands Cheatsheet

```bash
# Xem database
python3 quick_db_view.py

# Backup
./backup_database.sh

# Restore
./restore_database.sh

# Menu đầy đủ
python3 db_viewer.py

# Chạy backend API
cd backend && python -m uvicorn main:app --reload

# Xem accounts qua API
curl http://localhost:8000/api/accounts | python3 -m json.tool
```

---

**Cần hỗ trợ?** Xem [HUONG_DAN_DATABASE.md](./HUONG_DAN_DATABASE.md) hoặc check backend logs.
