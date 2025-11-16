# 📖 HƯỚNG DẪN SỬ DỤNG - MULTI TOOL GUI PRO

## 🎯 Giới thiệu

**Multi Tool GUI PRO** là ứng dụng desktop toàn diện với tính năng **Facebook Pro** - hỗ trợ tự động hóa các thao tác trên Facebook.

### ✨ Tính năng chính

- ✅ **Hệ thống đăng nhập hoàn chỉnh** (3 phương thức)
- ✅ **Quản lý nhiều tài khoản Facebook**
- ✅ **Friend Management** (Add/Accept/Unfriend)
- ✅ **Group Management** (Join/Post)
- ✅ **Content Manager** (Text Spinning với Spintax)
- ✅ **Activity Log** theo thời gian thực
- ✅ **Giao diện đẹp, dễ sử dụng**

---

## 🚀 Cách khởi động ứng dụng

### Bước 1: Cài đặt Node.js (nếu chưa có)

Tải và cài đặt Node.js từ: https://nodejs.org/

### Bước 2: Cài đặt dependencies

```bash
cd /home/bighitran1905/webapp
npm install
```

### Bước 3: Chạy ứng dụng

```bash
npm start
```

Hoặc chế độ development (với DevTools):

```bash
npm run dev
```

---

## 🔐 HƯỚNG DẪN ĐĂNG NHẬP FACEBOOK

### Phương pháp 1: 🍪 Cookies (KHUYẾN NGHỊ)

**Đây là phương pháp an toàn nhất, tránh bị checkpoint!**

#### Các bước lấy Cookies:

1. **Đăng nhập Facebook trên Chrome hoặc Edge**
2. **Mở Developer Tools:**
   - Nhấn phím `F12`
   - Hoặc chuột phải → "Inspect"
3. **Vào tab Application:**
   - Click vào tab "Application" (hoặc "Ứng dụng")
   - Mở mục "Cookies" bên trái
   - Click vào "https://www.facebook.com"
4. **Copy các cookies quan trọng:**
   - `c_user` - ID người dùng
   - `xs` - Session key
   - `datr` - Device token
   - `sb` - Secure browsing
5. **Format JSON:**
```json
[
  {"name": "c_user", "value": "100012345678901"},
  {"name": "xs", "value": "xxx%3Axxx"},
  {"name": "datr", "value": "xxx"},
  {"name": "sb", "value": "xxx"}
]
```
6. **Paste vào dialog trong ứng dụng**

#### Ví dụ đầy đủ:
```json
[
  {"name": "c_user", "value": "100012345678901"},
  {"name": "xs", "value": "36%3AXnHkR9Q3g_xxx%3A2%3A1234567890%3A-1%3A12345"},
  {"name": "datr", "value": "AbCdEfGhIjKlMnOpQrStUvWxYz"},
  {"name": "sb", "value": "XyZ123456789"}
]
```

---

### Phương pháp 2: 📧 Email & Password

**Lưu ý:** Phương pháp này có thể gặp checkpoint nếu Facebook phát hiện đăng nhập bất thường.

#### Các bước:

1. Chọn phương thức "Email & Password" trong dialog
2. Nhập thông tin:
   - **Account Name:** Tên gợi nhớ (VD: "Tài khoản chính")
   - **Email or Phone:** Email hoặc số điện thoại đăng ký Facebook
   - **Password:** Mật khẩu Facebook
   - **2FA Code:** (Nếu bật xác thực 2 lớp)
   - **Proxy:** (Tùy chọn) `http://user:pass@host:port`
3. Click "Add Account"

#### Xử lý 2FA (Two-Factor Authentication):

- Nếu tài khoản có bật 2FA, nhập mã 6 số từ app xác thực
- Hoặc nhập mã từ SMS

---

### Phương pháp 3: 🔑 Access Token

**Dành cho developers hoặc người dùng có sẵn token.**

#### Các bước lấy Access Token:

1. Truy cập: https://developers.facebook.com/tools/explorer/
2. Chọn ứng dụng của bạn (hoặc tạo mới)
3. Click "Generate Access Token"
4. Cấp quyền cần thiết
5. Copy token (bắt đầu bằng `EAAB...`)
6. Paste vào ứng dụng

#### Lưu ý:
- Token có thời hạn (60 ngày hoặc vĩnh viễn)
- Cần quyền: `public_profile`, `email`, `user_friends`

---

## 👥 SỬ DỤNG FRIEND MANAGEMENT

### 1. Add Friends (Thêm bạn)

**Chức năng:** Gửi lời mời kết bạn đến danh sách UID

#### Các bước:

1. Click vào "Facebook Pro" trong menu bên trái
2. Đảm bảo đã đăng nhập tài khoản
3. Trong phần **Friend Management**:
   - Nhập danh sách UID (mỗi UID một dòng)
   - Ví dụ:
     ```
     100012345678901
     100012345678902
     100012345678903
     ```
4. Đặt số lượng tối đa mỗi phiên (khuyến nghị: 50)
5. Click "➕ Add Friends"

#### Tips:
- Không gửi quá nhiều trong 1 lúc (tối đa 50-100/ngày)
- Chờ 10-30 giây giữa mỗi request
- Sử dụng proxy để tăng bảo mật

---

### 2. Accept Friend Requests (Chấp nhận lời mời)

**Chức năng:** Tự động chấp nhận lời mời kết bạn đến

#### Các bước:

1. Đặt số lượng tối đa mỗi phiên
2. Click "✅ Accept Requests"

#### Lưu ý:
- Có thể filter tài khoản giả (< 5 mutual friends)
- Chấp nhận từ từ để tránh spam

---

## 🏢 SỬ DỤNG GROUP MANAGEMENT

### 1. Join Groups (Tham gia nhóm)

**Chức năng:** Tự động tham gia nhiều nhóm Facebook

#### Các bước:

1. Trong phần **Group Management**
2. Nhập danh sách Group ID hoặc URL (mỗi nhóm một dòng)
   - Ví dụ:
     ```
     https://facebook.com/groups/123456789
     987654321
     https://facebook.com/groups/mygroupname
     ```
3. Click "🚪 Join Groups"

#### Tips:
- Không join quá nhiều trong ngày (tối đa 20-30)
- Ưu tiên join nhóm liên quan đến niche của bạn

---

### 2. Post to Groups (Đăng bài vào nhóm)

**Chức năng:** Đăng nội dung vào nhiều nhóm cùng lúc

#### Các bước:

1. Nhập danh sách Group ID/URL
2. Nhập nội dung đăng bài (hỗ trợ **Spintax** để tạo nội dung unique)
3. Click "📝 Post to Groups"

#### Ví dụ Spintax:
```
{Hello|Hi|Hey} everyone! 👋

This is {amazing|awesome|great} {content|post}! {🔥|✨|💯}

Check out {my website|this link|our page}: example.com

{Thanks|Thank you|Appreciate it}! 🙏
```

**Kết quả:** Mỗi group sẽ nhận được 1 phiên bản khác nhau của bài viết.

---

## ✍️ SỬ DỤNG CONTENT MANAGER

### Text Spinning với Spintax

**Chức năng:** Tạo nhiều phiên bản khác nhau từ 1 template

#### Cú pháp Spintax:
```
{option1|option2|option3}
```

#### Ví dụ:

**Input:**
```
{Good morning|Hello|Hi} {friend|buddy|mate}! 

I want to {share|show|tell you about} this {amazing|awesome|incredible} {product|tool|app}. 

It's {really|super|very} {useful|helpful|great}! {🔥|✨|💯}

{Check it out|Try it now|Get started}: example.com
```

**Output (5 variations):**
```
Variation 1: Hi friend! I want to show this awesome tool. It's very helpful! 🔥 Try it now: example.com
Variation 2: Hello mate! I want to tell you about this incredible app. It's super useful! ✨ Check it out: example.com
Variation 3: Good morning buddy! I want to share this amazing product. It's really great! 💯 Get started: example.com
... (và 2 variations nữa)
```

#### Các bước:

1. Nhập text có Spintax vào ô "Text with spintax"
2. Chọn số lượng variations (1-20)
3. Click "🔄 Generate Variations"
4. Xem kết quả phía dưới

---

## 🔄 QUẢN LÝ NHIỀU TÀI KHOẢN

### Switch Account (Chuyển tài khoản)

1. Click "🔄 Switch Account" trong Account Management
2. Chọn tài khoản muốn sử dụng từ danh sách
3. Tất cả thao tác tiếp theo sẽ sử dụng tài khoản đã chọn

### Delete Account (Xóa tài khoản)

1. Mở Account Selector
2. Click "🗑️ Delete" bên cạnh tài khoản muốn xóa
3. Xác nhận xóa

**Lưu ý:** Xóa chỉ xóa khỏi ứng dụng, không ảnh hưởng đến tài khoản Facebook thật.

---

## 📋 ACTIVITY LOG

**Activity Log** hiển thị tất cả hoạt động của ứng dụng:

- ✅ **[SUCCESS]** - Thao tác thành công
- ℹ️ **[INFO]** - Thông tin thông thường
- ❌ **[ERROR]** - Lỗi xảy ra
- ⚠️ **[WARNING]** - Cảnh báo

---

## ⚠️ CẢNH BÁO & BEST PRACTICES

### ❌ KHÔNG NÊN:

- ❌ Spam quá nhiều request trong thời gian ngắn
- ❌ Sử dụng cùng IP cho nhiều tài khoản
- ❌ Đăng nội dung giống hệt nhau vào nhiều nhóm
- ❌ Add friend quá 100 người/ngày
- ❌ Join quá 30 nhóm/ngày

### ✅ NÊN:

- ✅ Sử dụng Cookies thay vì Email/Password
- ✅ Sử dụng Proxy riêng cho mỗi tài khoản
- ✅ Thêm random delay giữa các thao tác (10-30s)
- ✅ Sử dụng Spintax để tạo nội dung unique
- ✅ Giới hạn số lượng thao tác mỗi ngày
- ✅ Kiểm tra Activity Log thường xuyên

---

## 🛡️ BẢO MẬT

### Lưu trữ thông tin:

- **Cookies, Email, Password** được lưu trong **localStorage** của Electron
- Chỉ có thể truy cập từ máy của bạn
- Không gửi thông tin lên server nào

### Khuyến nghị:

1. **Không chia sẻ cookies** với người khác
2. **Đăng xuất Facebook** trên browser sau khi lấy cookies
3. **Sử dụng Proxy** để ẩn IP thật
4. **Đổi password định kỳ** nếu dùng phương pháp Email/Password
5. **Bật 2FA** trên tài khoản Facebook chính

---

## 🐛 TROUBLESHOOTING

### Lỗi thường gặp:

#### 1. "Cannot find module..."
```bash
npm install
```

#### 2. Ứng dụng không khởi động
```bash
# Xóa node_modules và cài lại
rm -rf node_modules package-lock.json
npm install
```

#### 3. Login thất bại với Cookies
- Đảm bảo cookies còn hiệu lực
- Kiểm tra format JSON đúng
- Lấy lại cookies mới từ browser

#### 4. Login thất bại với Email/Password
- Kiểm tra email/password chính xác
- Nhập mã 2FA nếu có
- Thử dùng Cookies thay thế

#### 5. Chức năng không hoạt động
- Kiểm tra đã đăng nhập tài khoản chưa
- Xem Activity Log để biết lỗi cụ thể
- Restart ứng dụng

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề, vui lòng:

1. Kiểm tra **Activity Log** trong ứng dụng
2. Đọc kỹ **Troubleshooting** phía trên
3. Liên hệ support team

---

## 📝 CHANGELOG

### Version 1.0.0 (2024-01-15)

✅ **Hoàn thành:**
- Hệ thống đăng nhập đầy đủ (3 phương thức)
- Account Manager (quản lý nhiều tài khoản)
- Friend Management (Add/Accept/Unfriend)
- Group Management (Join/Post)
- Content Manager (Text Spinning)
- Activity Log real-time
- Giao diện Modern Dark Theme

---

## 💡 TIPS & TRICKS

### 1. Tối ưu hiệu suất:

- Sử dụng Cookies để đăng nhập nhanh hơn
- Giới hạn số lượng request mỗi phiên
- Chạy automation vào giờ thấp điểm

### 2. Tăng tỷ lệ thành công:

- Sử dụng Proxy chất lượng cao
- Warm-up tài khoản mới trước khi automation
- Không thao tác quá nhiều trong 1 ngày

### 3. Tránh bị checkpoint:

- Sử dụng Cookies thay vì Email/Password
- Thêm random delay giữa các thao tác
- Không đổi IP đột ngột
- Hoạt động tự nhiên như người dùng thật

---

## 🎯 WORKFLOW KHUYẾN NGHỊ

### Quy trình sử dụng hàng ngày:

1. **Sáng (8-10h):**
   - Accept friend requests (20-30 requests)
   - Join 5-10 groups mới

2. **Trưa (12-14h):**
   - Post vào 5-10 groups với nội dung spintax
   - Tương tác với bạn bè

3. **Chiều (16-18h):**
   - Add 30-50 friends mới
   - Check Activity Log

4. **Tối (20-22h):**
   - Post content mới vào groups
   - Review toàn bộ hoạt động trong ngày

### Giới hạn an toàn:

- ✅ Add friends: **50-100/ngày**
- ✅ Accept requests: **50-100/ngày**
- ✅ Join groups: **20-30/ngày**
- ✅ Post to groups: **10-20/ngày**

---

## 🚀 KẾT LUẬN

**Multi Tool GUI PRO - Facebook Pro** là công cụ mạnh mẽ giúp bạn tự động hóa các thao tác trên Facebook một cách an toàn và hiệu quả.

### Điểm mạnh:

- ✅ Giao diện đẹp, dễ sử dụng
- ✅ Nhiều phương thức đăng nhập
- ✅ Quản lý nhiều tài khoản dễ dàng
- ✅ Spintax tạo nội dung unique
- ✅ Activity Log theo dõi real-time
- ✅ An toàn, không gửi data lên server

### Lưu ý:

⚠️ Sử dụng công cụ có trách nhiệm và tuân thủ các điều khoản của Facebook để tránh bị khóa tài khoản.

---

**Made with ❤️ by Multi Tool Team**

**Version:** 1.0.0  
**Last Updated:** 2024-01-15
