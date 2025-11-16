# 🚀 Bi Ads Multi Tool PRO v3.0

Ứng dụng quản lý tài khoản Facebook toàn diện với automation và analytics.

## ✨ Tính năng chính

### 🔐 Quản lý Tài khoản
- ✅ Quản lý đa tài khoản Facebook
- ✅ Import/Export tài khoản từ file
- ✅ Kiểm tra trạng thái tài khoản tự động
- ✅ Quản lý proxy cho mỗi tài khoản
- ✅ Lưu trữ cookie và session

### 👥 Tài khoản phụ (Sub Accounts)
- ✅ Quản lý tài khoản phụ để tăng tương tác
- ✅ Tự động like, comment, share
- ✅ Import hàng loạt từ file
- ✅ Gán tài khoản chính

### 🆔 Quản lý Facebook IDs
- ✅ Lưu trữ và phân loại UID
- ✅ Import từ file hoặc URL Facebook
- ✅ Validation UID tự động
- ✅ Tìm kiếm và filter nâng cao
- ✅ Xuất danh sách theo format

### 📝 Bài viết đã đăng (Posted Content)
- ✅ Theo dõi bài viết đã đăng
- ✅ Thống kê engagement (likes, comments, shares)
- ✅ Tìm kiếm với highlighting
- ✅ Chỉnh sửa và xóa bài viết
- ✅ Bulk operations

### 🌐 Quản lý Proxy
- ✅ Import proxy từ file
- ✅ Kiểm tra proxy tự động
- ✅ Gán proxy cho tài khoản
- ✅ 3 chiến lược gán: Round Robin, Random, One-to-One
- ✅ Bulk operations với checkbox

### 🤖 Automation & Tasks
- ✅ Tự động like bài viết
- ✅ Tự động comment
- ✅ Tự động kết bạn
- ✅ Tự động join group
- ✅ Task scheduling và queuing
- ✅ Real-time task status

### 📊 Dashboard & Analytics
- ✅ Thống kê tổng quan
- ✅ Biểu đồ engagement
- ✅ Activity logs
- ✅ Performance metrics

### 🔧 Chrome Automation
- ✅ Tích hợp Chrome automation
- ✅ Quản lý Chrome profiles
- ✅ Auto-login Facebook
- ✅ 2FA auto-entry

## 📋 Yêu cầu hệ thống

- **Node.js**: 14.x hoặc cao hơn
- **Python**: 3.11 hoặc cao hơn
- **Chrome/Chromium**: Phiên bản mới nhất
- **OS**: Windows 10+, macOS 10.13+, Ubuntu 20.04+

## 🛠️ Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/bighitranpro/BIADS.git
cd BIADS
```

### 2. Cài đặt Backend (Python)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Cài đặt Frontend (Electron)

```bash
npm install
```

### 4. Cấu hình môi trường

```bash
# Copy file .env.example
cp .env.example .env
cp backend/.env.example backend/.env

# Chỉnh sửa .env với thông tin của bạn
```

## 🚀 Chạy ứng dụng

### Chạy Backend

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

Backend sẽ chạy tại: `http://localhost:8000`

### Chạy Frontend (Electron)

Trong terminal khác:

```bash
npm start
```

### Hoặc dùng script tự động

```bash
# Linux/macOS
./scripts/START_V3.sh

# Windows
scripts\START_BI_ADS.bat
```

## 📁 Cấu trúc dự án

```
BIADS/
├── backend/              # FastAPI Backend
│   ├── api/             # API Endpoints
│   │   ├── account_checker_api.py
│   │   ├── account_interactions_api.py
│   │   ├── facebook_ids_api.py
│   │   ├── sub_accounts_api.py
│   │   ├── posted_content_api.py
│   │   ├── proxy_bulk_api.py
│   │   └── ...
│   ├── core/            # Database & CRUD
│   │   ├── database.py
│   │   └── crud.py
│   ├── services/        # Business Logic
│   │   ├── chrome_manager.py
│   │   ├── facebook_automator.py
│   │   ├── activity_logger.py
│   │   └── ...
│   └── main.py         # FastAPI App
├── renderer/            # Electron Frontend
│   ├── index.html      # Main UI
│   ├── bi-ads-main.js  # Main Logic
│   ├── advanced-features.js
│   ├── modal-confirmation.js
│   └── styles.css
├── scripts/            # Utility Scripts
│   ├── START_V3.sh
│   └── START_BI_ADS.bat
├── docs/               # Documentation
│   ├── README.md
│   └── archive/
├── tests/              # Tests
│   └── frontend/
├── backups/            # Database Backups
│   └── database/
├── main.js            # Electron Main Process
├── preload.js         # Electron Preload
├── package.json       # Node.js Config
└── README.md          # This file
```

## 📚 Documentation

Chi tiết hơn về dự án, xem [docs/README.md](docs/README.md)

## 🔧 API Endpoints

Backend cung cấp RESTful API:

### Accounts
- `GET /api/accounts` - List accounts
- `POST /api/accounts` - Create account
- `PUT /api/accounts/{id}` - Update account
- `DELETE /api/accounts/{id}` - Delete account

### Sub Accounts (8 endpoints)
- `GET /api/sub-accounts/` - List với filters
- `POST /api/sub-accounts/` - Create
- `POST /api/sub-accounts/bulk/import` - Import từ file

### Facebook IDs (10 endpoints)
- `GET /api/facebook-ids/` - List với search
- `GET /api/facebook-ids/stats` - Statistics
- `POST /api/facebook-ids/bulk/import` - Import

### Posted Content (6 endpoints)
- `GET /api/posted-content/` - List với filters
- `GET /api/posted-content/search` - Search với highlighting
- `PUT /api/posted-content/{id}` - Update

### Proxies (7 endpoints)
- `POST /api/proxies/bulk/assign` - Bulk assign
- `POST /api/proxies/bulk/check-sync` - Bulk check

### Tasks & Activities
- `GET /api/tasks/running` - Running tasks
- `GET /api/activities/` - Activity logs

Chi tiết API: `http://localhost:8000/docs` (FastAPI Swagger UI)

## 🎯 Tiến độ hoàn thành

- ✅ **Backend APIs**: 100% (26/26 endpoints)
- ✅ **Frontend UI**: 80% (core features complete)
- ✅ **Database**: 100% (SQLAlchemy + SQLite)
- ✅ **Chrome Automation**: 90% (basic automation working)
- ✅ **Activity Logging**: 100%
- ⏳ **Testing**: 40% (in progress)
- ⏳ **Documentation**: 60% (in progress)

**Overall Completion**: ~80%

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

Mở `tests/frontend/test-accounts.html` trong trình duyệt

## 📦 Build & Deploy

### Build Electron App

```bash
npm run build          # All platforms
npm run build:win      # Windows
npm run build:mac      # macOS
npm run build:linux    # Linux
```

### Backup Database

```bash
./backup_database.sh
```

### Restore Database

```bash
./restore_database.sh backups/database/bi_ads_YYYYMMDD_HHMMSS.db.gz
```

## 🐛 Troubleshooting

### Backend không khởi động
```bash
cd backend
pip install --upgrade -r requirements.txt
python main.py
```

### Frontend lỗi kết nối API
- Kiểm tra backend đang chạy: `http://localhost:8000`
- Kiểm tra CORS settings trong `backend/main.py`

### Chrome automation lỗi
- Cài đặt Chrome/Chromium mới nhất
- Kiểm tra ChromeDriver version
- Xem logs trong Activity Log

## 🔐 Bảo mật

- ✅ Context Isolation trong Electron
- ✅ Environment variables cho sensitive data
- ✅ SQLite database với proper permissions
- ✅ API authentication (optional)
- ✅ Input validation và sanitization

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 📧 Contact & Support

- **GitHub**: https://github.com/bighitranpro/BIADS
- **Issues**: https://github.com/bighitranpro/BIADS/issues
- **Pull Requests**: https://github.com/bighitranpro/BIADS/pulls

## 🎉 Changelog

### v3.0.0 (2025-11-16)
- ✅ Complete frontend integration for 3 priority features
- ✅ Posted Content: Full CRUD + Search + Stats
- ✅ Facebook IDs: Auto-load + Import + Export
- ✅ Sub Accounts: Full management system
- ✅ Proxy Bulk UI: Checkbox selection + 4 bulk ops
- ✅ Project cleanup: Removed 19 unused docs, webapp-dist
- ✅ Organized documentation in docs/ folder

### Earlier versions
See [docs/archive/](docs/archive/) for historical changelogs

---

Made with ❤️ by bighitranpro
