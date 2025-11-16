# 🚀 Bi Ads Multi Tool PRO - Web Application v3.0.0

Ứng dụng web quản lý tài khoản Facebook chuyên nghiệp với giao diện hiện đại và đầy đủ tính năng.

## ✨ Tính Năng Chính

### 📊 Dashboard
- Thống kê tổng quan hệ thống
- Biểu đồ trực quan về accounts, proxies, tasks
- Hiển thị hoạt động gần đây
- Thao tác nhanh

### 👤 Quản Lý Tài Khoản
- ✅ Xem danh sách tài khoản (35 accounts)
- ✅ Thêm/sửa/xóa tài khoản
- ✅ Import/Export tài khoản (CSV/TXT)
- ✅ Gán/gỡ proxy cho tài khoản
- ✅ Lọc và tìm kiếm nâng cao
- ✅ Hiển thị trạng thái real-time

### 🌐 Quản Lý Proxy
- ✅ Xem danh sách proxy (60 proxies)
- ✅ Thêm/sửa/xóa proxy
- ✅ Import proxy bulk (nhiều proxy cùng lúc)
- ✅ Export proxy
- ✅ Hỗ trợ HTTP, HTTPS, SOCKS4, SOCKS5
- ✅ Hiển thị trạng thái proxy

### 📋 Quản Lý Tác Vụ
- ✅ Xem danh sách tác vụ
- ✅ Tạo tác vụ mới
- ✅ Xóa tác vụ
- ✅ Theo dõi tiến độ

### 📝 Nhật Ký Hoạt Động
- ✅ Xem chi tiết nhật ký (500 mục gần nhất)
- ✅ Lọc theo mức độ (info, success, warning, error)
- ✅ Làm mới real-time
- ✅ Xóa nhật ký

### ⚙️ Cài Đặt
- ✅ Thông tin hệ thống
- ✅ Kiểm tra kết nối backend
- ✅ Export toàn bộ dữ liệu
- ✅ Xóa cache

## 🎯 Công Nghệ Sử Dụng

- **Frontend:** Pure JavaScript (Vanilla JS) - No frameworks
- **UI:** Custom CSS with gradient themes
- **API Client:** Fetch API with async/await
- **Architecture:** Modular component-based
- **Responsive:** Mobile-friendly design

## 📋 Yêu Cầu Hệ Thống

### Bắt Buộc
- Python 3.7 or higher (để chạy web server)
- Backend API running on port 8000
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Khuyến Nghị
- RAM: 512MB+
- Disk: 50MB+
- Network: Backend phải accessible

## 🚀 Cài Đặt & Chạy

### Phương pháp 1: Sử dụng built package (Khuyến nghị)

```bash
# Extract package
tar -xzf bi-ads-webapp-v3.0.0.tar.gz
cd bi-ads-webapp

# Start web server
./start.sh
# Hoặc trên Windows: start.bat
# Hoặc thủ công: python3 server.py
```

### Phương pháp 2: Chạy từ source

```bash
# Di chuyển vào thư mục webapp-dist
cd webapp-dist

# Start web server
python3 server.py
```

### Phương pháp 3: Sử dụng web server khác

```bash
# Với Node.js http-server
npm install -g http-server
http-server -p 5000

# Với Python http.server
python3 -m http.server 5000

# Với PHP
php -S 0.0.0.0:5000
```

## 🌐 Truy Cập Ứng Dụng

Sau khi start server, mở browser và truy cập:

- **Local:** http://localhost:5000
- **Network:** http://<your-ip>:5000
- **Public (nếu có):** http://<public-ip>:5000

## 🔧 Cấu Hình

### Thay đổi Backend API URL

Edit file `js/config.js`:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://your-backend-ip:8000',
    // ... other configs
};
```

### Thay đổi Port

Edit file `server.py`:

```python
PORT = 5000  # Change to your desired port
```

## 📁 Cấu Trúc Thư Mục

```
webapp-dist/
├── index.html              # Main HTML file
├── server.py              # Simple HTTP server
├── build.sh               # Build script
├── README.md              # This file
├── css/
│   ├── styles.css         # Main styles (from Electron)
│   └── additional-styles.css  # Webapp-specific styles
├── js/
│   ├── config.js          # Configuration
│   ├── api-client.js      # API communication
│   ├── utils.js           # Utility functions
│   ├── components.js      # UI components
│   ├── dashboard.js       # Dashboard module
│   ├── accounts.js        # Accounts module
│   ├── proxies.js         # Proxies module
│   ├── tasks.js           # Tasks module
│   ├── logs.js            # Logs module
│   ├── settings.js        # Settings module
│   └── app.js             # Main application controller
└── build/
    └── bi-ads-webapp-v3.0.0.tar.gz  # Packaged app
```

## 🔌 Kiểm Tra Backend

Trước khi chạy webapp, đảm bảo backend đang hoạt động:

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "version": "3.0.0",
  "database": "online",
  "telegram_configured": true
}
```

## 🐛 Troubleshooting

### Backend Offline
- Kiểm tra backend có đang chạy: `curl http://localhost:8000/health`
- Start backend: `cd backend && python -m uvicorn main:app --reload`
- Kiểm tra port 8000 có bị chiếm: `lsof -i:8000`

### Port Already in Use
- Thay đổi port trong `server.py`
- Hoặc kill process đang chiếm port: `lsof -i:5000` và `kill <PID>`

### CORS Error
- Backend đã config CORS `allow_origins=["*"]`
- Nếu vẫn lỗi, check backend logs
- Đảm bảo không dùng `file://` protocol

### Cannot Load Data
- Check browser console (F12)
- Verify API URL in `js/config.js`
- Test API endpoints với curl
- Check network tab in browser DevTools

## 📊 API Endpoints

Webapp sử dụng các endpoints sau:

### Health & Stats
- `GET /health` - Health check
- `GET /api/stats` - Get statistics

### Accounts
- `GET /api/accounts` - List all accounts
- `POST /api/accounts` - Create account
- `PUT /api/accounts/{id}` - Update account
- `DELETE /api/accounts/{id}` - Delete account
- `PUT /api/accounts/{id}/assign-proxy` - Assign proxy
- `PUT /api/accounts/{id}/remove-proxy` - Remove proxy

### Proxies
- `GET /api/proxies` - List all proxies
- `POST /api/proxies` - Create proxy
- `PUT /api/proxies/{id}` - Update proxy
- `DELETE /api/proxies/{id}` - Delete proxy
- `POST /api/proxies/import` - Import multiple proxies

### Tasks
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create task
- `DELETE /api/tasks/{id}` - Delete task

### Logs
- `GET /api/logs` - Get logs
- `DELETE /api/logs` - Clear logs

## 🔐 Security Notes

### Development Mode
- Server hiện tại chỉ dành cho development
- Không sử dụng trong production environment
- Không có authentication/authorization

### Production Deployment
Để deploy production, sử dụng:

1. **Nginx** (Khuyến nghị)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/webapp-dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
    }
}
```

2. **Apache**
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    DocumentRoot /path/to/webapp-dist
    
    <Directory /path/to/webapp-dist>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    ProxyPass /api/ http://localhost:8000/api/
    ProxyPassReverse /api/ http://localhost:8000/api/
</VirtualHost>
```

## 📦 Build Package

Để tạo package mới:

```bash
cd webapp-dist
./build.sh
```

Kết quả: `build/bi-ads-webapp-v3.0.0.tar.gz`

## 🔄 Updates & Maintenance

### Update từ Electron App
Nếu có thay đổi trong Electron version:

1. Copy styles mới: `cp renderer/styles.css webapp-dist/css/`
2. Update modules nếu cần
3. Test thoroughly
4. Build package mới

### Database Backup
Webapp không chứa database, tất cả data ở backend. Để backup:

```bash
cd backend
./backup_database.sh
```

## 🆘 Support

### Documentation
- Backend API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Common Issues
1. **Backend not responding:** Check if uvicorn is running
2. **CORS errors:** Backend CORS is set to allow all origins
3. **Cannot import accounts:** Check file format (CSV/TXT)
4. **Proxy not working:** Verify proxy format (ip:port[:user:pass])

## 📈 Performance

### Optimization Tips
- Enable browser cache in production
- Minify JS/CSS files
- Use CDN for assets
- Enable gzip compression
- Use HTTP/2

### Monitoring
- Check browser console for errors
- Monitor backend logs: `tail -f backend/logs/app.log`
- Use browser DevTools Network tab

## 🎨 Customization

### Change Theme Colors
Edit `css/additional-styles.css`:

```css
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --background-color: #0f0f1e;
}
```

### Add New Features
1. Create new module in `js/`
2. Add route in `app.js`
3. Add menu item in `index.html`
4. Test thoroughly

## 📝 Changelog

### Version 3.0.0 (Current)
- ✨ Convert từ Electron app sang Web app
- ✅ Hoàn thiện Dashboard với charts
- ✅ Accounts management với import/export
- ✅ Proxies management với bulk import
- ✅ Tasks management
- ✅ Activity logs viewer
- ✅ Settings page
- ✅ Responsive design
- ✅ Toast notifications
- ✅ Modal dialogs
- ✅ Real-time backend status

## 📄 License

Proprietary - Bi Ads Team

## 👥 Credits

- **Author:** Bi Ads Team
- **Version:** 3.0.0
- **Release Date:** 2025-11-16

---

**🎉 Enjoy using Bi Ads Multi Tool PRO!**

For support: Check backend logs and browser console first.
