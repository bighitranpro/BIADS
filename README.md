# 🚀 Ứng dụng ElectronJS

Ứng dụng desktop đa nền tảng được xây dựng với ElectronJS - hỗ trợ Windows, macOS và Linux.

## ✨ Tính năng

- 🖥️ **Đa nền tảng**: Chạy trên Windows, macOS và Linux
- 🎨 **Giao diện đẹp**: UI hiện đại với gradient và animations
- 🔒 **Bảo mật**: Sử dụng Context Isolation và Preload Script
- 📂 **Xử lý File**: Mở và lưu file với native dialogs
- 💬 **Thông báo**: Hiển thị message boxes và notifications
- ⚡ **IPC Communication**: Giao tiếp an toàn giữa Main và Renderer process
- 📦 **Packaging**: Dễ dàng đóng gói thành file cài đặt

## 📋 Yêu cầu hệ thống

- Node.js 14.x hoặc cao hơn
- npm hoặc yarn
- Windows 7/macOS 10.10/Ubuntu 12.04 trở lên

## 🛠️ Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd webapp
```

### 2. Cài đặt dependencies

```bash
npm install
```

## 🚀 Chạy ứng dụng

### Chế độ phát triển

```bash
npm start
```

### Chế độ debug (mở DevTools)

```bash
npm run dev
```

## 📦 Đóng gói ứng dụng

### Build cho tất cả nền tảng

```bash
npm run build
```

### Build cho nền tảng cụ thể

```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

File build sẽ được tạo trong thư mục `dist/`

## 📁 Cấu trúc dự án

```
webapp/
├── main.js                 # Main process (Node.js + Electron APIs)
├── preload.js             # Preload script (Bridge giữa main và renderer)
├── package.json           # Cấu hình dự án và dependencies
├── renderer/              # Renderer process (Frontend)
│   ├── index.html        # HTML chính
│   ├── styles.css        # Styles
│   └── renderer.js       # JavaScript cho renderer
├── assets/               # Icons và tài nguyên
│   ├── icon.png
│   ├── icon.ico
│   └── icon.icns
├── node_modules/         # Dependencies (auto-generated)
└── dist/                 # Build output (auto-generated)
```

## 🏗️ Kiến trúc

### Main Process (`main.js`)
- Quản lý vòng đời ứng dụng
- Tạo và quản lý windows
- Xử lý system events
- Tương tác với OS APIs
- Xử lý IPC từ renderer process

### Preload Script (`preload.js`)
- Bridge an toàn giữa main và renderer
- Expose APIs cho renderer process
- Context Isolation để bảo mật

### Renderer Process (`renderer/`)
- Giao diện người dùng (HTML/CSS/JS)
- Tương tác với user
- Gửi/nhận messages từ main process
- Không có quyền truy cập trực tiếp Node.js APIs

## 🔐 Bảo mật

Ứng dụng này tuân thủ các best practices về bảo mật của Electron:

- ✅ Context Isolation enabled
- ✅ Node Integration disabled
- ✅ Remote Module disabled
- ✅ Preload script để expose APIs an toàn
- ✅ Content Security Policy trong HTML

## 📝 Các lệnh npm

| Lệnh | Mô tả |
|------|-------|
| `npm start` | Chạy ứng dụng ở chế độ production |
| `npm run dev` | Chạy ứng dụng với DevTools |
| `npm run build` | Build cho tất cả nền tảng |
| `npm run build:win` | Build cho Windows |
| `npm run build:mac` | Build cho macOS |
| `npm run build:linux` | Build cho Linux |

## 🎨 Tùy chỉnh

### Thay đổi thông tin ứng dụng

Chỉnh sửa `package.json`:

```json
{
  "name": "ten-ung-dung",
  "version": "1.0.0",
  "description": "Mo ta ung dung",
  "author": "Ten ban"
}
```

### Thay đổi icon

Đặt các file icon vào thư mục `assets/`:
- `icon.png` (1024x1024) - cho Linux
- `icon.ico` (256x256) - cho Windows
- `icon.icns` - cho macOS

### Thay đổi cấu hình build

Chỉnh sửa section `build` trong `package.json`

## 🐛 Debug

### DevTools

Mở DevTools bằng cách:
1. Chạy `npm run dev`
2. Hoặc trong menu: View → Toggle Developer Tools

### Console Logs

- Main process logs: Terminal/Console
- Renderer process logs: DevTools Console

## 📚 Tài liệu tham khảo

- [Electron Documentation](https://www.electronjs.org/docs)
- [Electron API Demos](https://github.com/electron/electron-api-demos)
- [Electron Builder](https://www.electron.build/)

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo issue hoặc pull request.

## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

## 🎯 TODO / Roadmap

- [ ] Thêm auto-updater
- [ ] Thêm system tray icon
- [ ] Thêm keyboard shortcuts
- [ ] Thêm themes (light/dark mode)
- [ ] Thêm settings page
- [ ] Thêm database (SQLite)
- [ ] Thêm testing (Jest/Spectron)
- [ ] CI/CD pipeline

## ⚡ Performance Tips

- Sử dụng `webPreferences.nodeIntegration: false` để tăng bảo mật
- Load assets cục bộ thay vì từ CDN
- Tối ưu hóa images và assets
- Sử dụng lazy loading cho các component lớn
- Minimize và bundle code trước khi build production

## 🆘 Troubleshooting

### Lỗi khi cài đặt dependencies

```bash
# Xóa node_modules và package-lock.json
rm -rf node_modules package-lock.json

# Cài lại
npm install
```

### Lỗi khi build

```bash
# Clear cache của electron-builder
npm run build -- --clear
```

### Ứng dụng không khởi động

1. Kiểm tra console logs
2. Kiểm tra file paths trong main.js
3. Đảm bảo tất cả dependencies đã được cài đặt

## 📧 Liên hệ

Nếu có câu hỏi hoặc vấn đề, vui lòng tạo issue trên GitHub.

---

Made with ❤️ using Electron
