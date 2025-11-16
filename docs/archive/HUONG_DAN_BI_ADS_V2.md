# 🚀 BI ADS - MULTI TOOL PRO V2.0

## 📖 HƯỚNG DẪN SỬ DỤNG HOÀN CHỈNH

---

## ✨ GIỚI THIỆU

**Bi Ads - Multi Tool PRO v2.0** là công cụ tự động hóa Facebook chuyên nghiệp với **40+ tính năng** hoạt động **TRỰC TUYẾN** thông qua backend API.

### Nhà phát triển: **Bi Ads Team**
### Phiên bản: **2.0.0**
### Ngôn ngữ: **100% Tiếng Việt**

---

## 🎯 TÍNH NĂNG CHỦ YẾU

### 📊 9 Trang Quản Lý:
1. 👤 **Quản lý tài khoản** - Thêm, xóa, chuyển đổi tài khoản Facebook
2. 🌐 **Quản lý proxy** - Quản lý proxy cho từng tài khoản
3. 👥 **Quản lý tài khoản phụ** - Tài khoản phụ trợ
4. 🆔 **Quản lý ID** - Danh sách UID
5. 📡 **Quản lý IP thiết bị** - Quản lý IP devices
6. ✅ **Quản lý whitelist** - Danh sách trắng
7. 📝 **Quản lý bài viết** - Bài đã đăng
8. 💬 **Quản lý tin nhắn** - Messages
9. ⚙️ **Cài đặt hệ thống** - Settings

### 🏢 Tác vụ Group (5 tính năng):
- ✅ Nhóm đã tham gia
- ✅ Quét nhóm theo từ khóa
- ✅ Tham gia nhóm
- ✅ Rời nhóm
- ✅ Mời bạn bè vào nhóm

### 💬 Tác vụ tương tác tài khoản (12 tính năng):
- ✅ Đăng bài viết (hỗ trợ spintax)
- ✅ Cắm link bài viết
- ✅ Bình luận bài viết
- ✅ Tự động like bài viết/comment
- ✅ Chia sẻ bài viết
- ✅ Update bio
- ✅ Tự động ẩn thông báo
- ✅ Tự động xem tin [Newsfeed]
- ✅ Tự động xem video
- ✅ Xóa bài viết
- ✅ Chọc bạn bè
- ✅ Join via UID

### 👥 Tác vụ bạn bè (7 tính năng):
- ✅ Kết bạn (add friends)
- ✅ Từ chối lời mời
- ✅ Đồng ý kết bạn
- ✅ Hủy lời mời đã gửi
- ✅ Hủy kết bạn (unfriend)
- ✅ Gửi tin nhắn
- ✅ Duyệt thẻ (approve tags)

### 📄 Tác vụ Fanpage (10 tính năng):
- ✅ Quản lý fanpage
- ✅ Mở comment & Inbox
- ✅ Tự động chỉnh fanpage
- ✅ Đăng bài fanpage
- ✅ Cắm link bài fanpage
- ✅ Tự comment tại wall
- ✅ Gửi tin nhắn fanpage
- ✅ Đẩy comment tin nhắn
- ✅ Mời thích fanpage từ UID/bạn bè
- ✅ Xóa bài viết fanpage

### 📊 Danh sách đã quét (7 tính năng):
- ✅ Danh sách bạn bè
- ✅ Bạn bè gợi ý
- ✅ Bạn bè đã thêm gần đây
- ✅ Danh sách theo dõi (followers)
- ✅ UID chưa đổi tên
- ✅ Danh sách chủ bài viết
- ✅ Quét bài viết

---

## 🚀 CÁCH CÀI ĐẶT & CHẠY

### Yêu cầu hệ thống:
- **Node.js** >= 14.x (https://nodejs.org/)
- **Python** >= 3.8 (https://www.python.org/)
- **Git** (optional)

### Cài đặt:

#### Windows:
```bash
# Bước 1: Mở Command Prompt hoặc PowerShell
cd C:\path\to\webapp

# Bước 2: Cài đặt dependencies (chỉ làm 1 lần)
npm install
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Bước 3: Chạy ứng dụng
START_BI_ADS.bat
```

#### Linux / macOS:
```bash
# Bước 1: Mở Terminal
cd /path/to/webapp

# Bước 2: Cài đặt dependencies (chỉ làm 1 lần)
npm install
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Bước 3: Chạy ứng dụng
./START_BI_ADS.sh
```

### Chạy nhanh (sau khi đã cài đặt):
```bash
# Windows
START_BI_ADS.bat

# Linux/Mac
./START_BI_ADS.sh
```

---

## 📖 HƯỚNG DẪN SỬ DỤNG

### 1. Thêm tài khoản Facebook

1. Click **"Quản lý tài khoản"** ở menu trên
2. Click **"➕ Thêm tài khoản"**
3. Chọn phương thức đăng nhập:

#### 🍪 Cookies (Khuyến nghị - An toàn nhất):
```
Bước 1: Đăng nhập Facebook trên Chrome/Edge
Bước 2: Nhấn F12 → Tab "Application" → "Cookies" → "facebook.com"
Bước 3: Copy các cookies: c_user, xs, datr, sb
Bước 4: Format JSON:
[
  {"name": "c_user", "value": "100012345678901"},
  {"name": "xs", "value": "xxx%3Axxx"},
  {"name": "datr", "value": "xxx"},
  {"name": "sb", "value": "xxx"}
]
Bước 5: Paste vào ứng dụng và submit
```

#### 📧 Email & Password:
```
- Nhập email hoặc số điện thoại
- Nhập mật khẩu
- Nhập mã 2FA nếu có
- Thêm proxy (optional)
```

#### 🔑 Access Token:
```
- Lấy token từ: https://developers.facebook.com/tools/explorer/
- Paste token vào ứng dụng
```

### 2. Sử dụng tính năng

#### A. Tham gia nhóm:
```
1. Click "Tác vụ Group" → "Tham gia nhóm"
2. Nhập danh sách Group ID hoặc URL (mỗi dòng 1 nhóm):
   https://facebook.com/groups/123456789
   987654321
   https://facebook.com/groups/mygroup
3. Đặt delay: 10-30 giây
4. Đặt số nhóm tối đa: 20-30
5. Click "▶️ Bắt đầu tác vụ"
6. Theo dõi log ở phần "Nhật ký hoạt động"
```

#### B. Kết bạn:
```
1. Click "Tác vụ bạn bè" → "Kết bạn"
2. Nhập danh sách UID (mỗi dòng 1 UID):
   100012345678901
   100012345678902
3. Đặt delay: 15-30 giây
4. Đặt số lời mời tối đa: 50-100
5. Click "▶️ Bắt đầu tác vụ"
```

#### C. Đăng bài viết:
```
1. Click "Tác vụ tương tác" → "Đăng bài viết"
2. Nhập nội dung (hỗ trợ spintax):
   {Chào|Hello|Hi} mọi người! 
   Đây là {bài viết|nội dung} {tuyệt vời|hay ho}! {🔥|✨|💯}
3. Thêm hình ảnh (URL, mỗi dòng 1 ảnh)
4. Chọn "Đăng vào các nhóm" nếu muốn
5. Click "▶️ Bắt đầu tác vụ"
```

#### D. Quản lý Fanpage:
```
1. Click "Tác vụ Fanpage" → "Đăng bài fanpage"
2. Nhập nội dung và hình ảnh
3. Chọn fanpage target
4. Click "▶️ Bắt đầu tác vụ"
```

---

## 🔧 BACKEND API

### API Server:
- **URL:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

### Endpoints chính:

#### Group Operations:
- `POST /api/groups/join` - Tham gia nhóm
- `POST /api/groups/leave` - Rời nhóm
- `POST /api/groups/scan` - Quét nhóm

#### Friend Operations:
- `POST /api/friends/add` - Kết bạn
- `POST /api/friends/accept` - Chấp nhận kết bạn
- `POST /api/friends/unfriend` - Hủy kết bạn

#### Post Operations:
- `POST /api/posts/create` - Đăng bài
- `POST /api/posts/comment` - Bình luận
- `POST /api/posts/like` - Like
- `POST /api/posts/share` - Chia sẻ

#### Fanpage Operations:
- `POST /api/fanpage/post` - Đăng bài fanpage
- `POST /api/fanpage/interact` - Tương tác fanpage

#### Task Management:
- `POST /api/start-task` - Bắt đầu tác vụ
- `GET /api/task/{task_id}` - Lấy trạng thái tác vụ

---

## ⚠️ LƯU Ý & BEST PRACTICES

### ✅ NÊN:
- ✅ Sử dụng Cookies để đăng nhập (an toàn nhất)
- ✅ Sử dụng Proxy riêng cho mỗi tài khoản
- ✅ Đặt delay hợp lý (10-30 giây)
- ✅ Giới hạn số lượng tác vụ mỗi ngày
- ✅ Sử dụng Spintax để tạo nội dung unique
- ✅ Kiểm tra "Nhật ký hoạt động" thường xuyên
- ✅ Chạy backend trước khi sử dụng

### ❌ KHÔNG NÊN:
- ❌ Spam quá nhiều request trong thời gian ngắn
- ❌ Sử dụng cùng IP cho nhiều tài khoản
- ❌ Đăng nội dung giống hệt vào nhiều nhóm
- ❌ Add friend > 100 người/ngày
- ❌ Join > 30 nhóm/ngày
- ❌ Bỏ qua delay giữa các request

### Giới hạn khuyến nghị:
| Tác vụ | Số lượng/ngày |
|--------|---------------|
| Kết bạn | 50-100 |
| Chấp nhận kết bạn | 50-100 |
| Tham gia nhóm | 20-30 |
| Đăng bài | 10-20 |
| Comment | 50-100 |
| Like | 100-200 |

---

## 🐛 TROUBLESHOOTING

### Lỗi: "Backend Offline"
```bash
# Kiểm tra backend có chạy không:
# Mở browser: http://localhost:8000/health

# Nếu không chạy, khởi động lại:
cd backend
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate      # Windows
python main.py
```

### Lỗi: "Cannot connect to backend"
```bash
# Kiểm tra port 8000 có bị chiếm không:
netstat -an | grep 8000     # Linux/Mac
netstat -an | findstr 8000  # Windows

# Kill process nếu cần:
kill -9 $(lsof -t -i:8000)  # Linux/Mac
taskkill /F /IM python.exe  # Windows
```

### Lỗi: "Module not found"
```bash
# Cài lại dependencies:
cd backend
pip install -r requirements.txt

# Frontend:
npm install
```

### Lỗi đăng nhập:
```
1. Cookies: Lấy lại cookies mới từ browser
2. Email/Password: Kiểm tra credentials chính xác
3. Token: Kiểm tra token còn hiệu lực
```

---

## 📊 KIẾN TRÚC HỆ THỐNG

```
┌─────────────────────────────────────────┐
│     Electron Frontend (Renderer)        │
│  - Bi Ads UI (HTML/CSS/JS)              │
│  - Account Management                    │
│  - Task Selection                        │
│  - Activity Log Display                  │
└────────────┬────────────────────────────┘
             │
             │ HTTP REST API
             │ (localhost:8000)
             │
┌────────────▼────────────────────────────┐
│     Python FastAPI Backend              │
│  - REST API Server                       │
│  - Task Processing                       │
│  - Facebook Automation Logic             │
│  - Browser Automation (Playwright)       │
└──────────────────────────────────────────┘
```

---

## 📚 CẤU TRÚC FILE

```
webapp/
├── START_BI_ADS.bat          # Windows launcher
├── START_BI_ADS.sh           # Linux/Mac launcher
├── package.json              # Node.js config
├── main.js                   # Electron main process
├── preload.js                # Electron preload
│
├── renderer/                 # Frontend files
│   ├── index.html           # Main HTML
│   ├── styles.css           # Purple theme CSS
│   ├── renderer.js          # Base app logic
│   ├── bi-ads-main.js       # Main application (33KB)
│   └── api-client.js        # Backend API client
│
├── backend/                  # Backend files
│   ├── main.py              # FastAPI server
│   └── requirements.txt     # Python dependencies
│
└── docs/
    └── HUONG_DAN_BI_ADS_V2.md   # This file
```

---

## 💡 WORKFLOW KHUYẾN NGHỊ

### Quy trình hàng ngày:

**Sáng (8-10h):**
- ✅ Chấp nhận lời mời kết bạn (20-30)
- ✅ Tham gia 5-10 nhóm mới
- ✅ Đăng bài vào 3-5 nhóm

**Trưa (12-14h):**
- ✅ Like các bài viết (50-100)
- ✅ Comment vào bài viết (10-20)
- ✅ Chia sẻ bài viết quan trọng

**Chiều (16-18h):**
- ✅ Gửi lời mời kết bạn (30-50)
- ✅ Đăng status cá nhân
- ✅ Tương tác với fanpage

**Tối (20-22h):**
- ✅ Đăng bài vào nhóm (5-10)
- ✅ Gửi tin nhắn (nếu cần)
- ✅ Review log và kết quả

---

## 🔒 BẢO MẬT & PRIVACY

### Lưu trữ dữ liệu:
- ✅ Tất cả data lưu **LOCAL** trong localStorage
- ✅ Không gửi data lên server nào
- ✅ Cookies/Passwords được mã hóa
- ✅ Backend chạy trên **localhost** (máy bạn)

### Khuyến nghị bảo mật:
1. ✅ Không chia sẻ cookies với người khác
2. ✅ Sử dụng proxy để ẩn IP
3. ✅ Đổi password định kỳ
4. ✅ Bật 2FA trên Facebook
5. ✅ Không chạy trên máy công cộng

---

## 📞 HỖ TRỢ

### Kiểm tra trước khi hỏi:
1. ✅ Đọc kỹ phần Troubleshooting
2. ✅ Kiểm tra backend có chạy không
3. ✅ Xem log lỗi ở "Nhật ký hoạt động"
4. ✅ Kiểm tra internet connection

### Liên hệ:
- **Team:** Bi Ads Team
- **Version:** 2.0.0
- **License:** MIT

---

## 🎯 CHANGELOG

### Version 2.0.0 (Current):
- ✅ Complete redesign với UI mới
- ✅ Thêm 40+ tính năng automation
- ✅ Python FastAPI backend
- ✅ REST API integration
- ✅ 100% tiếng Việt
- ✅ Auto-start scripts
- ✅ Real-time activity logging
- ✅ Multi-account management
- ✅ Proxy support
- ✅ Spintax content generation

---

## 🎊 KẾT LUẬN

**Bi Ads - Multi Tool PRO v2.0** là công cụ tự động hóa Facebook **HOÀN CHỈNH** và **CHUYÊN NGHIỆP** với:

✅ **40+ tính năng** automation  
✅ **Backend API** hoạt động THẬT  
✅ **100% tiếng Việt**  
✅ **Modern UI** đẹp mắt  
✅ **Easy to use** dễ sử dụng  
✅ **Safe & Secure** an toàn  

### Phát triển bởi: **Bi Ads Team** 🚀

---

**Made with ❤️ by Bi Ads Team**  
**Version 2.0.0 | 2024**
