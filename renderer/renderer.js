// Renderer Process Script
// File này chạy trong renderer process và có thể truy cập DOM

// Đợi DOM load xong
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Renderer process đã sẵn sàng!');

    // Load thông tin ứng dụng
    await loadAppInfo();

    // Setup event listeners
    setupEventListeners();
});

// Load thông tin ứng dụng
async function loadAppInfo() {
    try {
        // Lấy phiên bản ứng dụng
        const version = await window.electronAPI.getAppVersion();
        document.getElementById('app-version').textContent = version;

        // Lấy đường dẫn ứng dụng
        const appPath = await window.electronAPI.getAppPath();
        document.getElementById('app-path').textContent = appPath;

        // Hiển thị thông tin hệ thống
        document.getElementById('platform').textContent = window.electronAPI.platform;
        document.getElementById('node-version').textContent = window.electronAPI.nodeVersion;
        document.getElementById('chrome-version').textContent = window.electronAPI.chromeVersion;
        document.getElementById('electron-version').textContent = window.electronAPI.electronVersion;
    } catch (error) {
        console.error('Lỗi khi load thông tin:', error);
        showOutput('Lỗi: ' + error.message, 'error');
    }
}

// Setup event listeners cho các nút
function setupEventListeners() {
    // Nút hiển thị thông báo
    document.getElementById('btn-show-message').addEventListener('click', async () => {
        try {
            await window.electronAPI.showMessage('Xin chào từ Electron! 👋');
            showOutput('Đã hiển thị thông báo thành công!', 'success');
        } catch (error) {
            showOutput('Lỗi: ' + error.message, 'error');
        }
    });

    // Nút mở file
    document.getElementById('btn-open-file').addEventListener('click', async () => {
        try {
            const result = await window.electronAPI.openFileDialog();
            if (!result.canceled && result.filePaths.length > 0) {
                showOutput(`Đã chọn file:\n${result.filePaths[0]}`, 'success');
            } else {
                showOutput('Không có file nào được chọn', 'info');
            }
        } catch (error) {
            showOutput('Lỗi: ' + error.message, 'error');
        }
    });

    // Nút lưu file
    document.getElementById('btn-save-file').addEventListener('click', async () => {
        try {
            const result = await window.electronAPI.saveFileDialog();
            if (!result.canceled) {
                showOutput(`Đường dẫn lưu file:\n${result.filePath}`, 'success');
            } else {
                showOutput('Đã hủy lưu file', 'info');
            }
        } catch (error) {
            showOutput('Lỗi: ' + error.message, 'error');
        }
    });

    // Nút cập nhật thông tin
    document.getElementById('btn-get-info').addEventListener('click', async () => {
        await loadAppInfo();
        showOutput('Đã cập nhật thông tin ứng dụng!', 'success');
    });

    // Nút xóa
    document.getElementById('btn-clear').addEventListener('click', () => {
        document.getElementById('demo-input').value = '';
        document.getElementById('demo-textarea').value = '';
        showOutput('Đã xóa nội dung!', 'info');
    });

    // Nút lưu
    document.getElementById('btn-save').addEventListener('click', () => {
        const inputValue = document.getElementById('demo-input').value;
        const textareaValue = document.getElementById('demo-textarea').value;

        if (inputValue || textareaValue) {
            const data = {
                input: inputValue,
                note: textareaValue,
                timestamp: new Date().toLocaleString('vi-VN')
            };
            showOutput(JSON.stringify(data, null, 2), 'success');
        } else {
            showOutput('Vui lòng nhập nội dung trước khi lưu!', 'warning');
        }
    });

    // Lắng nghe sự kiện từ main process
    window.electronAPI.onFileOpened((filePath) => {
        showOutput(`File được mở từ menu:\n${filePath}`, 'info');
    });
}

// Hiển thị kết quả trong output box
function showOutput(message, type = 'info') {
    const outputBox = document.getElementById('output');
    const timestamp = new Date().toLocaleTimeString('vi-VN');
    
    let emoji = 'ℹ️';
    let color = '#3498db';
    
    switch(type) {
        case 'success':
            emoji = '✅';
            color = '#2ecc71';
            break;
        case 'error':
            emoji = '❌';
            color = '#e74c3c';
            break;
        case 'warning':
            emoji = '⚠️';
            color = '#f39c12';
            break;
    }
    
    outputBox.innerHTML = `
        <div style="color: ${color}; font-weight: bold; margin-bottom: 10px;">
            ${emoji} ${type.toUpperCase()} - ${timestamp}
        </div>
        <div style="color: #2c3e50;">
            ${message}
        </div>
    `;
}

// Log thông tin khi có lỗi
window.addEventListener('error', (event) => {
    console.error('Window error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});
