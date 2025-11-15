/**
 * Preload Script
 * File này chạy trong một context đặc biệt có quyền truy cập vào cả Node.js APIs và DOM
 * Được sử dụng để expose các APIs an toàn cho renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose các APIs an toàn cho renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    // Thông tin hệ thống (chỉ đọc)
    platform: process.platform,
    nodeVersion: process.versions.node,
    chromeVersion: process.versions.chrome,
    electronVersion: process.versions.electron,

    // Các hàm giao tiếp với main process
    getAppVersion: () => ipcRenderer.invoke('get-app-version'),
    getAppPath: () => ipcRenderer.invoke('get-app-path'),
    showMessage: (message) => ipcRenderer.invoke('show-message', message),
    openFileDialog: () => ipcRenderer.invoke('open-file-dialog'),
    saveFileDialog: () => ipcRenderer.invoke('save-file-dialog'),

    // Lắng nghe sự kiện từ main process
    onFileOpened: (callback) => {
        ipcRenderer.on('file-opened', (event, filePath) => {
            callback(filePath);
        });
    },

    // Gửi sự kiện tùy chỉnh
    send: (channel, data) => {
        // Danh sách các channel được phép
        const validChannels = ['custom-event', 'user-action'];
        if (validChannels.includes(channel)) {
            ipcRenderer.send(channel, data);
        }
    },

    // Nhận sự kiện tùy chỉnh
    receive: (channel, callback) => {
        // Danh sách các channel được phép
        const validChannels = ['custom-response', 'app-notification'];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, (event, ...args) => callback(...args));
        }
    },

    // Xóa listener
    removeListener: (channel, callback) => {
        const validChannels = ['custom-response', 'app-notification', 'file-opened'];
        if (validChannels.includes(channel)) {
            ipcRenderer.removeListener(channel, callback);
        }
    }
});

// Log khi preload script được load
console.log('Preload script đã được load thành công!');
console.log('Platform:', process.platform);
console.log('Node version:', process.versions.node);
console.log('Electron version:', process.versions.electron);

// Xử lý lỗi trong preload
window.addEventListener('error', (event) => {
    console.error('Preload error:', event.error);
});
