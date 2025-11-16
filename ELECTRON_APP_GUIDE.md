# 🖥️ HƯỚNG DẪN SỬ DỤNG ELECTRON APP - BI ADS MULTI TOOL PRO

## ✅ TRẠNG THÁI HIỆN TẠI

### 🟢 Đang Chạy
- ✅ **Electron App:** Đang chạy
- ✅ **Backend API:** Online (port 8000)
- ✅ **Database:** Online (35 accounts, 60 proxies)
- ✅ **Kết nối:** Hoạt động tốt

---

## 🎯 ELECTRON APP LÀ GÌ?

**Electron App** là ứng dụng desktop chạy trên máy tính của bạn (Windows/macOS/Linux).

### Đặc điểm:
- 🖥️ **Desktop Application** - Cửa sổ riêng
- ⚡ **Native Performance** - Nhanh và mượt
- 🔒 **Secure** - Dữ liệu local
- 💾 **Offline-ready** - Có thể làm việc offline

---

## 📋 CẤU TRÚC ỨNG DỤNG

```
Bi Ads Multi Tool PRO
│
├── Backend (FastAPI)
│   ├── API Server: http://localhost:8000
│   ├── Database: SQLite (bi_ads.db)
│   ├── Accounts: 35
│   ├── Proxies: 60
│   └── Status: ✅ Running
│
└── Frontend (Electron)
    ├── Main Process (main.js)
    ├── Renderer Process (renderer/)
    ├── UI: HTML/CSS/JavaScript
    └── Status: ✅ Running
```

---

## 🚀 CÁCH SỬ DỤNG ELECTRON APP

### 1️⃣ Khởi Động Ứng Dụng

#### Option A: Từ Terminal
```bash
cd /home/bighitran1905/webapp
npm start
```

#### Option B: Từ Package Manager
```bash
# Nếu đã build
./dist/bi-ads-multi-tool-pro
```

### 2️⃣ Giao Diện Chính

Khi mở app, bạn sẽ thấy:

```
╔═══════════════════════════════════════════════════════╗
║  File  Chỉnh sửa  Xem  Trợ giúp                     ║
╠═══════════════════════════════════════════════════════╣
║  🚀 Bi Ads - Multi Tool PRO v3.0                     ║
║                                                       ║
║  📊 Dashboard | 👤 Quản lý tài khoản | 🌐 Proxy...  ║
╠═══════════════════════════════════════════════════════╣
║  ┌─────────────────┐  ┌─────────────────────────┐   ║
║  │ 📋 Tác vụ Group │  │ [Nội dung chính]        │   ║
║  │                 │  │                         │   ║
║  │ • Nhóm đã tham  │  │ 📊 Dashboard            │   ║
║  │   gia           │  │                         │   ║
║  │ • Quét nhóm     │  │ Stats, Charts...        │   ║
║  │ • Tham gia nhóm │  │                         │   ║
║  │ • Rời nhóm      │  │                         │   ║
║  │                 │  │                         │   ║
║  │ 📝 Tác vụ tài   │  └─────────────────────────┘   ║
║  │    khoản        │                                ║
║  └─────────────────┘                                ║
╚═══════════════════════════════════════════════════════╝
```

---

## 🎮 CÁC CHỨC NĂNG CHÍNH

### 📊 Dashboard
**Truy cập:** Click "Dashboard" ở menu trên

**Tính năng:**
- Xem tổng quan hệ thống
- Thống kê accounts, proxies, tasks
- Biểu đồ trực quan
- Hoạt động gần đây

### 👤 Quản Lý Tài Khoản
**Truy cập:** Click "Quản lý tài khoản"

**Tính năng:**
- ✅ **Xem danh sách:** 35 accounts hiện có
- ✅ **Thêm tài khoản:** Click "Thêm" → Điền thông tin
- ✅ **Sửa tài khoản:** Click icon ✏️ → Chỉnh sửa
- ✅ **Xóa tài khoản:** Click icon 🗑️ → Xác nhận
- ✅ **Import:** Menu → Import file CSV/TXT
- ✅ **Export:** Menu → Export ra file
- ✅ **Gán Proxy:** Chọn account → Gán proxy

**Cách Import Accounts:**
```
1. Chuẩn bị file accounts.txt:
   Format: uid|username|password|cookies|2fa

2. Menu → File → Import Accounts
3. Chọn file
4. Click Import
```

### 🌐 Quản Lý Proxy
**Truy cập:** Click "Quản lý proxy"

**Tính năng:**
- ✅ **Xem danh sách:** 60 proxies hiện có
- ✅ **Thêm proxy:** Nhập IP:Port:User:Pass
- ✅ **Kiểm tra:** Test proxy hoạt động
- ✅ **Import bulk:** Import nhiều proxy cùng lúc
- ✅ **Gán cho accounts:** Auto assign

**Cách Import Proxies:**
```
1. Chuẩn bị file proxies.txt:
   Format: ip:port:username:password

2. Menu → File → Import Proxies
3. Chọn file
4. Click Import
```

### 📋 Tác Vụ Group

#### ▶️ Nhóm Đã Tham Gia
```
1. Sidebar → Click "Nhóm đã tham gia"
2. Chọn account
3. Click "Lấy danh sách"
4. Xem tất cả groups đã join
```

#### 🔍 Quét Nhóm Theo Từ Khóa
```
1. Sidebar → Click "Quét nhóm theo từ khóa"
2. Nhập từ khóa (VD: "Marketing", "Kinh doanh")
3. Chọn account để quét
4. Click "Bắt đầu quét"
5. Kết quả hiển thị danh sách groups
```

#### ➕ Tham Gia Nhóm
```
1. Sidebar → Click "Tham gia nhóm"
2. Paste danh sách group IDs (mỗi dòng 1 ID)
3. Chọn accounts sẽ join
4. Cài đặt delay (giây giữa mỗi join)
5. Click "Bắt đầu"
```

#### 🚪 Rời Nhóm
```
1. Sidebar → Click "Rời nhóm"
2. Chọn account
3. Chọn groups muốn leave
4. Click "Rời nhóm"
```

### 💬 Tác Vụ Bài Viết

#### 📝 Đăng Bài Viết
```
1. Sidebar → "Đăng bài viết"
2. Nhập nội dung bài viết
3. Chọn ảnh/video (optional)
4. Chọn account để đăng
5. Chọn target (Timeline/Group)
6. Click "Đăng bài"
```

#### 💬 Comment Bài Viết
```
1. Sidebar → "Bình luận bài viết"
2. Paste link bài viết
3. Nhập nội dung comment
4. Chọn accounts để comment
5. Cài đặt delay
6. Click "Bắt đầu"
```

### 👥 Tác Vụ Bạn Bè

#### ➕ Kết Bạn
```
1. Sidebar → "Kết bạn"
2. Paste danh sách UIDs
3. Chọn accounts gửi lời mời
4. Cài đặt delay
5. Click "Bắt đầu"
```

#### 💌 Gửi Tin Nhắn
```
1. Sidebar → "Gửi tin nhắn"
2. Nhập nội dung tin nhắn
3. Chọn người nhận (UIDs)
4. Chọn accounts gửi
5. Click "Gửi"
```

---

## 🔧 CÀI ĐẶT HỆ THỐNG

### ⚙️ Cài Đặt Chung
**Truy cập:** Menu → Cài đặt hệ thống

**Tùy chỉnh:**
- ✅ **Proxy mặc định:** Chọn proxy cho tất cả accounts
- ✅ **Delay:** Thời gian chờ giữa các thao tác
- ✅ **Retry:** Số lần thử lại khi thất bại
- ✅ **Timeout:** Thời gian timeout
- ✅ **Telegram:** Cấu hình bot notification

### 📱 Telegram Bot
**Nhận thông báo qua Telegram:**

```
1. Mở Telegram → Tìm @BotFather
2. Tạo bot mới → Lấy Bot Token
3. Vào Settings → Telegram
4. Nhập Bot Token và Chat ID
5. Click "Lưu"
6. Test: Click "Gửi test"
```

---

## 🎯 WORKFLOW THỰC TẾ

### Kịch Bản 1: Tham Gia Group Hàng Loạt

```
Bước 1: Chuẩn bị
  → Import 35 accounts (đã có sẵn)
  → Import 60 proxies (đã có sẵn)
  → Gán proxy cho accounts

Bước 2: Quét Groups
  → Vào "Quét nhóm theo từ khóa"
  → Nhập: "Marketing Facebook"
  → Quét và lưu kết quả

Bước 3: Tham Gia
  → Copy danh sách Group IDs
  → Vào "Tham gia nhóm"
  → Paste IDs
  → Chọn accounts (chọn tất cả 35)
  → Delay: 10 giây
  → Click "Bắt đầu"

Bước 4: Theo Dõi
  → Xem logs ở phần "Nhật ký hoạt động"
  → Nhận thông báo qua Telegram
```

### Kịch Bản 2: Đăng Bài Hàng Loạt

```
Bước 1: Chuẩn bị nội dung
  → Viết nội dung bài viết
  → Chuẩn bị ảnh (nếu có)

Bước 2: Chọn Target
  → Chọn đăng Timeline hoặc Groups
  → Nếu Groups: Chọn groups đã join

Bước 3: Đăng Bài
  → Vào "Đăng bài viết"
  → Paste nội dung
  → Upload ảnh
  → Chọn 35 accounts
  → Delay: 15 giây
  → Click "Đăng bài"

Bước 4: Kiểm Tra
  → Vào "Quản lý bài viết đã đăng"
  → Xem danh sách posts
  → Check status
```

### Kịch Bản 3: Tương Tác Bài Viết

```
Bước 1: Lấy Link Bài Viết
  → Copy link bài viết cần tương tác

Bước 2: Like Bài Viết
  → Vào "Tự động like bài viết"
  → Paste link
  → Chọn accounts
  → Click "Like"

Bước 3: Comment
  → Vào "Bình luận bài viết"
  → Paste link
  → Nhập comment (có thể dùng spin text)
  → Chọn accounts
  → Click "Comment"

Bước 4: Share
  → Vào "Chia sẻ bài viết"
  → Paste link
  → Chọn nơi share (Timeline/Groups)
  → Click "Share"
```

---

## 📊 DASHBOARD & MONITORING

### Xem Thống Kê
**Dashboard hiển thị:**
- 📈 **Total Accounts:** 35
- ✅ **Active Accounts:** 30
- 🌐 **Total Proxies:** 60
- 📋 **Tasks Running:** Số tasks đang chạy
- ✔️ **Tasks Completed:** Số tasks đã xong
- ❌ **Tasks Failed:** Số tasks thất bại

### Nhật Ký Hoạt Động
**Xem logs:**
```
Menu → Nhật ký hoạt động
→ Xem tất cả hoạt động
→ Filter theo level: Info/Success/Warning/Error
→ Export logs ra file
```

**Màu logs:**
- 🟢 **Success:** Thành công
- 🔵 **Info:** Thông tin
- 🟡 **Warning:** Cảnh báo
- 🔴 **Error:** Lỗi

---

## 🔧 TROUBLESHOOTING

### ❌ Backend Offline

**Triệu chứng:**
- App hiện "Backend Offline"
- Không load được data
- Các thao tác không hoạt động

**Giải quyết:**
```bash
# Terminal 1: Start Backend
cd /home/bighitran1905/webapp/backend
source ../venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Electron
cd /home/bighitran1905/webapp
npm start
```

### ❌ Không Load Được Accounts

**Giải quyết:**
```
1. Check backend: http://localhost:8000/health
2. Refresh app: Ctrl+R
3. Check database: ls -lh backend/bi_ads.db
4. View database: python3 backend/quick_db_view.py
```

### ❌ Task Không Chạy

**Kiểm tra:**
```
1. Account có active không?
2. Proxy hoạt động không?
3. Backend logs có lỗi gì?
4. Xem logs: Menu → Nhật ký
```

### ❌ Proxy Lỗi

**Giải quyết:**
```
1. Test proxy: curl --proxy http://ip:port http://google.com
2. Xóa proxy chết
3. Import proxy mới
4. Re-assign cho accounts
```

---

## 🎓 TIPS & TRICKS

### 1. Spin Text cho Comment
```
Dùng {option1|option2|option3} để random

Ví dụ:
"{Hay quá|Tuyệt vời|Xuất sắc} bạn {ơi|nhé|nha}!"

Kết quả random:
- "Hay quá bạn ơi!"
- "Tuyệt vời bạn nhé!"
- "Xuất sắc bạn nha!"
```

### 2. Schedule Tasks
```
Dùng delay để tạo schedule:
- Join groups: 10-15 giây/group
- Post: 30-60 giây/post
- Comment: 20-30 giây/comment
- Friend request: 15-20 giây/request
```

### 3. Backup Data
```bash
# Backup database
cd backend
./backup_database.sh

# Export accounts
Menu → File → Export Accounts

# Export proxies
Menu → File → Export Proxies
```

### 4. Bulk Operations
```
Chọn nhiều items:
- Ctrl+Click: Chọn từng cái
- Shift+Click: Chọn range
- Ctrl+A: Chọn tất cả
```

### 5. Keyboard Shortcuts
```
Ctrl+R    : Refresh app
Ctrl+Q    : Quit app
Ctrl+W    : Close window
F5        : Reload
F11       : Fullscreen
F12       : DevTools (debug)
```

---

## 📱 TELEGRAM INTEGRATION

### Setup Bot

**Bước 1: Tạo Bot**
```
1. Mở Telegram
2. Tìm @BotFather
3. Gửi: /newbot
4. Nhập tên bot
5. Nhập username bot
6. Nhận Bot Token
```

**Bước 2: Lấy Chat ID**
```
1. Tìm @userinfobot
2. Gửi /start
3. Nhận Chat ID
```

**Bước 3: Cấu Hình**
```
1. Vào Settings → Telegram
2. Paste Bot Token
3. Paste Chat ID
4. Click "Lưu"
5. Test: Click "Gửi tin nhắn test"
```

### Nhận Thông Báo

Bot sẽ gửi notification khi:
- ✅ Task hoàn thành
- ❌ Task thất bại
- 🚀 Hệ thống khởi động
- 🛑 Hệ thống tắt
- ⚠️ Cảnh báo quan trọng

---

## 💾 DATABASE MANAGEMENT

### View Database
```bash
cd backend
python3 quick_db_view.py
```

### Backup Database
```bash
cd backend
./backup_database.sh
# Kết quả: backups/bi_ads_YYYYMMDD_HHMMSS.db
```

### Restore Database
```bash
cd backend
./restore_database.sh
# Chọn file backup để restore
```

### Clear All Data
```bash
cd backend
rm bi_ads.db
python3 -m uvicorn main:app  # Tạo DB mới
```

---

## 🔐 SECURITY & BEST PRACTICES

### Bảo Mật
- 🔒 **Không share cookies:** Giữ bí mật
- 🔑 **Dùng 2FA:** Enable khi có thể
- 🌐 **Dùng proxy:** Luôn luôn
- 📱 **Telegram alerts:** Monitor real-time

### Best Practices
- ⏱️ **Delay hợp lý:** Tránh spam
- 📊 **Monitor logs:** Theo dõi thường xuyên
- 💾 **Backup thường xuyên:** Mỗi ngày
- 🔄 **Rotate proxies:** Thay đổi định kỳ
- 📉 **Start slow:** Test với ít accounts trước

### Limits Facebook
```
Recommended limits:
- Friend requests: 20-30/day per account
- Group joins: 20-30/day per account
- Posts: 5-10/day per account
- Comments: 30-50/day per account
- Likes: 100-200/day per account
```

---

## 🎯 CHECKLIST HÀNG NGÀY

### Morning Routine
```
□ Check backend status
□ Review logs từ đêm qua
□ Check accounts still active
□ Review proxy status
□ Plan tasks cho ngày hôm nay
```

### Evening Routine
```
□ Check completed tasks
□ Review success rate
□ Backup database
□ Export logs
□ Schedule tasks cho ngày mai
```

---

## 📞 SUPPORT

### Khi Cần Giúp Đỡ

**Kiểm tra:**
1. Backend running: `curl http://localhost:8000/health`
2. Electron logs: F12 → Console
3. Backend logs: `tail -f backend/logs/app.log`
4. Database: `python3 backend/quick_db_view.py`

**Files quan trọng:**
- `main.js` - Electron main process
- `renderer/bi-ads-main.js` - UI logic
- `backend/main.py` - API server
- `backend/bi_ads.db` - Database

---

## ✅ STATUS HIỆN TẠI

### Hệ Thống
- ✅ **Electron App:** Running
- ✅ **Backend API:** Running (port 8000)
- ✅ **Database:** Online
- ✅ **Telegram:** Configured

### Dữ Liệu
- ✅ **Accounts:** 35 (30 active)
- ✅ **Proxies:** 60 (all active)
- ✅ **Tasks:** 0 (ready to create)

### Kết Nối
- ✅ **Electron ↔ Backend:** Connected
- ✅ **Backend ↔ Database:** Connected
- ✅ **Backend ↔ Telegram:** Connected

---

## 🚀 BẮT ĐẦU SỬ DỤNG

**Ứng dụng đã sẵn sàng!**

Bạn có thể:
1. ✅ Xem dashboard
2. ✅ Quản lý 35 accounts
3. ✅ Quản lý 60 proxies
4. ✅ Tạo và chạy tasks
5. ✅ Monitor logs
6. ✅ Nhận Telegram alerts

**Hãy bắt đầu với task đầu tiên của bạn! 🎉**

---

**Created:** 2025-11-16  
**Version:** 3.0.0  
**Status:** ✅ Production Ready
