# 📚 Bi Ads Multi Tool PRO - Documentation

## 📖 Tài liệu chính

### [DEVELOPMENT_RECOMMENDATIONS.md](DEVELOPMENT_RECOMMENDATIONS.md)
Hướng dẫn phát triển và khuyến nghị kỹ thuật cho dự án.

### [CLEANUP_ANALYSIS.md](CLEANUP_ANALYSIS.md)
Phân tích và kế hoạch dọn dẹp cấu trúc dự án.

---

## 📁 Tài liệu lưu trữ

Các tài liệu cũ và báo cáo phát triển được lưu trong thư mục [`archive/`](archive/)

### Danh sách tài liệu lưu trữ:

- **HUONG_DAN_BI_ADS_V2.md** - Hướng dẫn phiên bản 2
- **HUONG_DAN_SU_DUNG.md** - Hướng dẫn sử dụng chi tiết
- **IMPLEMENTATION_SUMMARY.md** - Tóm tắt triển khai
- **BUGFIX_SUMMARY.md** - Tóm tắt sửa lỗi
- **PR_DESCRIPTION.md** - Mô tả Pull Request
- **QUICK_START_GUIDE.md** - Hướng dẫn bắt đầu nhanh
- **ADVANCED_DEVELOPMENT_PLAN.md** - Kế hoạch phát triển nâng cao
- **TOM_TAT_DE_XUAT.md** - Tóm tắt đề xuất
- **NANG_CAP_UNG_DUNG.md** - Nâng cấp ứng dụng

---

## 🚀 Quick Start

Để bắt đầu với dự án, xem [README.md](../README.md) ở thư mục gốc.

### Cài đặt Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Chạy Frontend (Electron)
```bash
npm install
npm start
```

### Truy cập Database
```bash
python db_viewer.py
# hoặc
python quick_db_view.py
```

---

## 📊 Cấu trúc dự án

```
webapp/
├── backend/           # FastAPI backend
│   ├── api/          # API endpoints
│   ├── core/         # Database và CRUD
│   ├── services/     # Business logic
│   └── tests/        # Backend tests
├── renderer/         # Electron frontend
│   ├── index.html    # Main UI
│   ├── *.js          # Frontend logic
│   └── styles.css    # Styling
├── scripts/          # Utility scripts
├── tests/            # Frontend tests
├── docs/             # Documentation (bạn đang ở đây)
└── backups/          # Database backups
```

---

## 🔗 Liên kết hữu ích

- **GitHub Repository**: https://github.com/bighitranpro/BIADS
- **Issue Tracker**: https://github.com/bighitranpro/BIADS/issues
- **Pull Requests**: https://github.com/bighitranpro/BIADS/pulls

---

## 📝 Ghi chú

Tài liệu này được tự động cập nhật. Nếu bạn muốn đóng góp, vui lòng tạo Pull Request.

**Cập nhật lần cuối**: 2025-11-16
