// Settings Module
const Settings = {
    init() {
        this.render();
    },
    
    render() {
        const content = document.getElementById('contentBody');
        const actions = document.getElementById('contentActions');
        
        actions.innerHTML = '';
        
        content.innerHTML = `
            <div class="card">
                <div class="card-header">⚙️ Cài đặt hệ thống</div>
                <div class="card-body">
                    <h3 style="color: #667eea; margin-bottom: 15px;">Thông tin hệ thống</h3>
                    <table class="data-table">
                        <tr>
                            <td><strong>Ứng dụng:</strong></td>
                            <td>${CONFIG.APP_NAME}</td>
                        </tr>
                        <tr>
                            <td><strong>Phiên bản:</strong></td>
                            <td>${CONFIG.APP_VERSION}</td>
                        </tr>
                        <tr>
                            <td><strong>Backend API:</strong></td>
                            <td>${window.API_URL}</td>
                        </tr>
                        <tr>
                            <td><strong>Trạng thái:</strong></td>
                            <td id="backendStatusText">Đang kiểm tra...</td>
                        </tr>
                    </table>
                    
                    <h3 style="color: #667eea; margin: 30px 0 15px 0;">Cài đặt nâng cao</h3>
                    <form id="settingsForm">
                        ${components.createFormField({ 
                            type: 'number', 
                            name: 'refresh_interval', 
                            label: 'Khoảng thời gian làm mới (giây)',
                            value: CONFIG.DATA_REFRESH_INTERVAL / 1000
                        })}
                        ${components.createFormField({ 
                            type: 'number', 
                            name: 'toast_duration', 
                            label: 'Thời gian hiển thị thông báo (giây)',
                            value: CONFIG.TOAST_DURATION / 1000
                        })}
                        <button type="submit" class="btn btn-primary">💾 Lưu cài đặt</button>
                    </form>
                    
                    <h3 style="color: #667eea; margin: 30px 0 15px 0;">Công cụ</h3>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <button class="btn btn-info" onclick="Settings.testConnection()">🔌 Kiểm tra kết nối</button>
                        <button class="btn btn-warning" onclick="Settings.clearCache()">🗑️ Xóa cache</button>
                        <button class="btn btn-secondary" onclick="Settings.exportAll()">💾 Export toàn bộ dữ liệu</button>
                    </div>
                </div>
            </div>
        `;
        
        this.setupEventListeners();
        this.checkConnection();
    },
    
    setupEventListeners() {
        document.getElementById('settingsForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            utils.showToast('Cài đặt đã được lưu', 'success');
        });
    },
    
    async checkConnection() {
        try {
            const health = await apiClient.healthCheck();
            document.getElementById('backendStatusText').innerHTML = 
                `<span style="color: #2ecc71;">✅ Online - ${health.version}</span>`;
        } catch (error) {
            document.getElementById('backendStatusText').innerHTML = 
                `<span style="color: #e74c3c;">❌ Offline</span>`;
        }
    },
    
    async testConnection() {
        await this.checkConnection();
        utils.showToast('Đã kiểm tra kết nối', 'info');
    },
    
    clearCache() {
        localStorage.clear();
        utils.showToast('Đã xóa cache', 'success');
    },
    
    async exportAll() {
        try {
            const [accounts, proxies, tasks] = await Promise.all([
                apiClient.getAccounts(),
                apiClient.getProxies(),
                apiClient.getTasks()
            ]);
            
            const data = { accounts, proxies, tasks, exported_at: new Date().toISOString() };
            utils.downloadFile(
                JSON.stringify(data, null, 2),
                `bi-ads-full-export-${new Date().toISOString().split('T')[0]}.json`,
                'application/json'
            );
            utils.showToast('Đã export toàn bộ dữ liệu', 'success');
        } catch (error) {
            utils.showToast('Lỗi export: ' + error.message, 'error');
        }
    }
};

window.Settings = Settings;
