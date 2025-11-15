const { app, BrowserWindow, ipcMain, Menu, dialog } = require('electron');
const path = require('path');

// Biến lưu trữ cửa sổ chính
let mainWindow;

// Hàm tạo cửa sổ chính
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      enableRemoteModule: false
    },
    icon: path.join(__dirname, 'assets/icon.png')
  });

  // Load file HTML
  mainWindow.loadFile('renderer/index.html');

  // Mở DevTools khi debug
  if (process.argv.includes('--debug')) {
    mainWindow.webContents.openDevTools();
  }

  // Xử lý khi cửa sổ đóng
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Tạo menu
  createMenu();
}

// Tạo menu cho ứng dụng
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Mở File',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const result = await dialog.showOpenDialog(mainWindow, {
              properties: ['openFile']
            });
            if (!result.canceled) {
              mainWindow.webContents.send('file-opened', result.filePaths[0]);
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Thoát',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Chỉnh sửa',
      submenu: [
        { role: 'undo', label: 'Hoàn tác' },
        { role: 'redo', label: 'Làm lại' },
        { type: 'separator' },
        { role: 'cut', label: 'Cắt' },
        { role: 'copy', label: 'Sao chép' },
        { role: 'paste', label: 'Dán' },
        { role: 'selectAll', label: 'Chọn tất cả' }
      ]
    },
    {
      label: 'Xem',
      submenu: [
        { role: 'reload', label: 'Tải lại' },
        { role: 'forceReload', label: 'Tải lại mạnh' },
        { role: 'toggleDevTools', label: 'Developer Tools' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Reset Zoom' },
        { role: 'zoomIn', label: 'Phóng to' },
        { role: 'zoomOut', label: 'Thu nhỏ' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Toàn màn hình' }
      ]
    },
    {
      label: 'Trợ giúp',
      submenu: [
        {
          label: 'Giới thiệu',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'Giới thiệu',
              message: 'Ứng dụng ElectronJS',
              detail: 'Phiên bản 1.0.0\nĐược xây dựng với Electron'
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// IPC Handlers - Xử lý giao tiếp giữa main và renderer process
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('get-app-path', () => {
  return app.getAppPath();
});

ipcMain.handle('show-message', async (event, message) => {
  const result = await dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: 'Thông báo',
    message: message,
    buttons: ['OK']
  });
  return result.response;
});

ipcMain.handle('open-file-dialog', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Text Files', extensions: ['txt', 'md', 'json'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result;
});

ipcMain.handle('save-file-dialog', async () => {
  const result = await dialog.showSaveDialog(mainWindow, {
    filters: [
      { name: 'Text Files', extensions: ['txt', 'md', 'json'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result;
});

// Sự kiện khi ứng dụng sẵn sàng
app.whenReady().then(() => {
  createWindow();

  // Trên macOS, tạo lại cửa sổ khi click vào dock icon
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Thoát ứng dụng khi tất cả cửa sổ đóng (trừ macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Xử lý lỗi chưa xử lý
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});
