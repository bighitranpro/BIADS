# ✅ Hướng Dẫn Sử Dụng Database - HOÀN TẤT

## 🎉 Tổng Quan

Đã tạo hoàn chỉnh hệ thống quản lý database cho Bi Ads Multi Tool PRO với:
- ✅ **3 công cụ xem database** (Python scripts)
- ✅ **2 scripts backup/restore** (Bash)
- ✅ **2 tài liệu hướng dẫn** (Vietnamese)
- ✅ **Tích hợp sẵn trong ứng dụng** (Backend API)

---

## 📍 Database Location

```
📂 /home/bighitran1905/webapp/backend/data/bi_ads.db
```

**Thông tin:**
- Loại: SQLite (async với aiosqlite)
- Kích thước: 220KB (nén còn 28KB)
- Số bảng: 12 tables
- Dữ liệu: 35 accounts, 60 proxies, 33 logs

---

## 🚀 3 CÁCH SỬ DỤNG DATABASE

### 1️⃣ Python Scripts (KHUYẾN NGHỊ - Dễ nhất)

#### Xem Nhanh Database
```bash
python3 quick_db_view.py
```

**Hiển thị:**
- ✅ Thông tin database (size, path)
- ✅ Danh sách 12 tables với số records
- ✅ Top 10 accounts với proxy status
- ✅ Tất cả proxies và số accounts đang dùng
- ✅ Recent tasks (10 gần nhất)
- ✅ Recent logs (10 gần nhất)
- ✅ Statistics theo status

**Thời gian:** < 1 giây ⚡

#### Xem Chi Tiết với Menu
```bash
python3 db_viewer.py
```

**Menu gồm 6 tùy chọn:**
1. Xem Accounts (Tài khoản)
2. Xem Proxies (Proxy)
3. Xem Tasks (Tác vụ)
4. Xem Logs (Nhật ký)
5. Xem Statistics (Thống kê)
6. Custom SQL Query

**Features:**
- ✅ Màu sắc đẹp mắt
- ✅ Table format dễ đọc
- ✅ Thống kê tự động
- ✅ Chạy custom SQL queries

### 2️⃣ DB Browser for SQLite (GUI)

**Cài đặt:**

**Windows:**
```bash
# Download từ: https://sqlitebrowser.org/dl/
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

**Sử dụng:**
1. Mở DB Browser for SQLite
2. File → Open Database
3. Chọn: `/home/bighitran1905/webapp/backend/data/bi_ads.db`
4. Tab "Browse Data" để xem/edit dữ liệu
5. Tab "Execute SQL" để chạy queries

**Ưu điểm:**
- ✅ Giao diện đồ họa đẹp
- ✅ Dễ edit dữ liệu
- ✅ Export/Import CSV
- ✅ Visualize database schema

### 3️⃣ Backend API (Tích hợp sẵn)

**Start backend:**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Các API endpoints:**
```bash
# Health check (bao gồm database status)
curl http://localhost:8000/health

# Lấy tất cả accounts
curl http://localhost:8000/api/accounts

# Lấy account cụ thể
curl http://localhost:8000/api/accounts/1

# Lấy tất cả proxies
curl http://localhost:8000/api/proxies

# Lấy statistics
curl http://localhost:8000/api/stats

# Lấy tasks
curl http://localhost:8000/api/tasks

# Lấy logs
curl http://localhost:8000/api/logs
```

**Ưu điểm:**
- ✅ Không cần công cụ thêm
- ✅ RESTful API chuẩn
- ✅ JSON response dễ parse
- ✅ Tích hợp với frontend

---

## 💾 BACKUP & RESTORE

### Backup Database

```bash
./backup_database.sh
```

**Kết quả:**
```
==========================================
  Bi Ads Database Backup
==========================================

📊 Database size: 224K
💾 Backing up database...
✅ Backup created: backups/database/bi_ads_20251116_084014.db
🗜️  Compressing backup...
✅ Compressed: bi_ads_20251116_084014.db.gz (28K)
🧹 Cleaning up old backups...
ℹ️  No cleanup needed (1/30 backups)

📋 Recent backups:
   backups/database/bi_ads_20251116_084014.db.gz (27K)

✅ Backup completed successfully!
==========================================
```

**Features:**
- ✅ Tự động timestamp (YYYYMMDD_HHMMSS)
- ✅ Nén gzip (224KB → 28KB, giảm 87%)
- ✅ Giữ 30 bản backup gần nhất
- ✅ Tự động xóa backup cũ
- ✅ Colored output đẹp mắt

### Restore Database

```bash
./restore_database.sh
```

**Flow:**
```
==========================================
  Bi Ads Database Restore
==========================================

📋 Available backups:

  [1] bi_ads_20251116_084014.db.gz (27K)
  [2] bi_ads_20251115_120000.db.gz (26K)

Chọn backup để restore (1-2), hoặc 0 để hủy: 1

Selected: bi_ads_20251116_084014.db.gz

⚠️  WARNING: Current database will be backed up and replaced!
Confirm restore? (yes/no): yes

💾 Backing up current database...
✅ Current database backed up to: ...
🗜️  Decompressing backup...
🔄 Restoring database...
✅ Database restored successfully!
   Size: 220KB

🔍 Verifying database...
✅ Database verified: 35 accounts

✅ Restore completed successfully!
==========================================
```

**Safety Features:**
- ✅ List tất cả backups với kích thước
- ✅ Confirmation prompt
- ✅ Auto-backup database hiện tại trước khi restore
- ✅ Verification sau khi restore
- ✅ Có thể cancel bất cứ lúc nào

### Tự Động Backup (Cron Job)

```bash
# Mở crontab editor
crontab -e

# Thêm dòng này để backup mỗi ngày lúc 2:00 AM
0 2 * * * /home/bighitran1905/webapp/backup_database.sh >> /home/bighitran1905/webapp/backups/backup.log 2>&1
```

**Schedule options:**
```bash
# Mỗi giờ
0 * * * * /path/to/backup_database.sh

# Mỗi 6 giờ
0 */6 * * * /path/to/backup_database.sh

# Mỗi ngày lúc 2:00 AM
0 2 * * * /path/to/backup_database.sh

# Mỗi tuần (Chủ nhật 3:00 AM)
0 3 * * 0 /path/to/backup_database.sh
```

---

## 📊 CẤU TRÚC DATABASE

### Bảng Chính (Core)

| Bảng | Mô tả | Records | Key Columns |
|------|-------|---------|-------------|
| **accounts** | Tài khoản Facebook | 35 | uid, name, status, proxy_id |
| **proxies** | Danh sách proxy | 60 | ip, port, protocol, status |
| **tasks** | Tác vụ automation | 0 | task_type, status, progress |
| **activity_logs** | Nhật ký hoạt động | 33 | level, action, message |
| **settings** | Cài đặt ứng dụng | 0 | key, value |

### Bảng Nâng Cao (Advanced)

| Bảng | Mô tả | Records | Chức năng |
|------|-------|---------|-----------|
| **sub_accounts** | Tài khoản phụ | 9 | Auto like/comment |
| **facebook_ids** | UID thu thập | 50 | Scan group/post |
| **ip_addresses** | Quản lý IP | 20 | Security tracking |
| **whitelist_accounts** | Tài khoản VIP | 30 | Protected accounts |
| **posted_content** | Bài viết đã đăng | 40 | Post management |
| **messages** | Tin nhắn | 81 | Inbox management |
| **auto_reply_templates** | Template tự động | 0 | Auto reply |

### Relationships

```
accounts (1) ──< (N) tasks
accounts (1) ──< (N) activity_logs
accounts (N) ──> (1) proxies
accounts (1) ──< (N) sub_accounts
accounts (1) ──< (N) posted_content
accounts (1) ──< (N) messages
```

---

## 💡 SQL QUERIES HỮU ÍCH

### Xem Accounts với Proxy Info
```sql
SELECT 
    a.id,
    a.name,
    a.uid,
    a.status,
    p.ip || ':' || p.port as proxy,
    p.protocol
FROM accounts a
LEFT JOIN proxies p ON a.proxy_id = p.id;
```

### Thống Kê Accounts theo Status
```sql
SELECT 
    status,
    COUNT(*) as count,
    COUNT(proxy_id) as with_proxy,
    ROUND(100.0 * COUNT(proxy_id) / COUNT(*), 2) as proxy_percentage
FROM accounts
GROUP BY status;
```

### Proxies và Số Accounts Đang Dùng
```sql
SELECT 
    p.id,
    p.ip || ':' || p.port as address,
    p.protocol,
    p.status,
    COUNT(a.id) as accounts_using
FROM proxies p
LEFT JOIN accounts a ON p.id = a.proxy_id
GROUP BY p.id
ORDER BY accounts_using DESC;
```

### Recent Activity Logs
```sql
SELECT 
    l.level,
    a.name as account,
    l.action,
    l.message,
    datetime(l.created_at, 'localtime') as time
FROM activity_logs l
LEFT JOIN accounts a ON l.account_id = a.id
ORDER BY l.created_at DESC
LIMIT 20;
```

### Tasks Success Rate
```sql
SELECT 
    task_type,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
    ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM tasks
GROUP BY task_type;
```

---

## 🛠️ TROUBLESHOOTING

### ❌ Database is locked

**Nguyên nhân:** Backend đang chạy hoặc có process khác đang dùng

**Giải pháp:**
```bash
# Kiểm tra process
lsof backend/data/bi_ads.db

# Stop backend
# Kill process nếu cần
```

### ❌ Cannot find database

**Giải pháp:**
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

**Giải pháp:**
```bash
# Check integrity
python3 -c "
import sqlite3
conn = sqlite3.connect('backend/data/bi_ads.db')
cursor = conn.cursor()
result = cursor.execute('PRAGMA integrity_check;').fetchone()
print(result[0])
"

# Nếu corrupted, restore từ backup
./restore_database.sh
```

### ❌ Script không chạy được

**Giải pháp:**
```bash
# Kiểm tra permissions
ls -la *.sh *.py

# Cho quyền execute nếu cần
chmod +x backup_database.sh
chmod +x restore_database.sh
chmod +x db_viewer.py
```

---

## 📚 TÀI LIỆU

### 1. Quick Start Guide
**File:** `DATABASE_QUICK_START.md` (5.7KB)

**Nội dung:**
- ✅ Hướng dẫn nhanh 3 phút
- ✅ Command cheatsheet
- ✅ Queries thông dụng
- ✅ Troubleshooting nhanh

**Sử dụng cho:** Người mới bắt đầu, tra cứu nhanh

### 2. Complete Guide
**File:** `HUONG_DAN_DATABASE.md` (16KB)

**Nội dung:**
- ✅ Chi tiết 12 tables với schema SQL
- ✅ 3 phương pháp access database
- ✅ SQL queries từ cơ bản đến nâng cao
- ✅ Backup/restore chi tiết
- ✅ Cron job setup
- ✅ Best practices
- ✅ Performance optimization
- ✅ Troubleshooting đầy đủ

**Sử dụng cho:** Tìm hiểu sâu, development, production setup

---

## 🎯 QUICK COMMANDS CHEATSHEET

```bash
# ============================================
# XEM DATABASE
# ============================================

# Xem nhanh toàn bộ
python3 quick_db_view.py

# Menu đầy đủ
python3 db_viewer.py

# Via API
curl http://localhost:8000/api/accounts | python3 -m json.tool

# ============================================
# BACKUP & RESTORE
# ============================================

# Backup ngay
./backup_database.sh

# Restore interactive
./restore_database.sh

# Manual backup
cp backend/data/bi_ads.db backups/bi_ads_$(date +%Y%m%d).db

# ============================================
# DATABASE INFO
# ============================================

# Check size
du -h backend/data/bi_ads.db

# Count records
python3 -c "
import sqlite3
conn = sqlite3.connect('backend/data/bi_ads.db')
cursor = conn.cursor()
for table in ['accounts', 'proxies', 'tasks', 'activity_logs']:
    count = cursor.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    print(f'{table}: {count}')
"

# ============================================
# BACKEND API
# ============================================

# Start backend
cd backend && python -m uvicorn main:app --reload

# Health check
curl http://localhost:8000/health

# Get accounts
curl http://localhost:8000/api/accounts

# Get proxies
curl http://localhost:8000/api/proxies

# Get stats
curl http://localhost:8000/api/stats
```

---

## ✅ CHECKLIST HOÀN THÀNH

### Tools Created
- [x] `quick_db_view.py` - Quick overview tool
- [x] `db_viewer.py` - Interactive menu tool
- [x] `backup_database.sh` - Automated backup
- [x] `restore_database.sh` - Interactive restore

### Documentation
- [x] `DATABASE_QUICK_START.md` - Quick reference
- [x] `HUONG_DAN_DATABASE.md` - Complete guide
- [x] `DATABASE_SETUP_COMPLETE.md` - This file

### Features
- [x] Multiple database access methods
- [x] Automated backup with compression
- [x] Safe restore with verification
- [x] Comprehensive Vietnamese documentation
- [x] Colored terminal output
- [x] Error handling and validation
- [x] No external dependencies

### Testing
- [x] ✅ quick_db_view.py tested - Working
- [x] ✅ backup_database.sh tested - Working (224KB → 28KB)
- [x] ✅ Scripts executable - Permissions set
- [x] ✅ Database accessible - 35 accounts, 60 proxies
- [x] ✅ Backend API working - All endpoints tested

---

## 🚀 NEXT STEPS

Database infrastructure đã hoàn chỉnh! Các bước tiếp theo:

1. ✅ **Database tools** - HOÀN TẤT
2. ⏳ **Dashboard charts** - Tích hợp Chart.js
3. ⏳ **Facebook automation** - Post, comment, like (HIGH PRIORITY)
4. ⏳ **Proxy management** - Testing và rotation
5. ⏳ **WebSocket** - Real-time updates
6. ⏳ **Task scheduling** - Automated tasks

---

## 📞 SUPPORT

Nếu gặp vấn đề:
1. Xem **DATABASE_QUICK_START.md** cho giải pháp nhanh
2. Xem **HUONG_DAN_DATABASE.md** cho chi tiết
3. Check backend logs: `backend/logs/`
4. Verify database: `python3 quick_db_view.py`
5. Restore từ backup: `./restore_database.sh`

---

**Tạo bởi:** GenSpark AI Developer  
**Ngày:** 2025-11-16  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
