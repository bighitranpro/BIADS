// Main Application Controller for Bi Ads Multi Tool PRO v3.0

const app = {
    currentPage: 'dashboard',
    initialized: false,

    // Initialize application
    async init() {
        if (this.initialized) return;
        
        console.log(`🚀 Initializing ${CONFIG.APP_NAME} v${CONFIG.APP_VERSION}`);
        
        // Setup event listeners
        this.setupNavigationListeners();
        
        // Check backend connection
        await this.checkBackendConnection();
        
        // Start periodic health check
        setInterval(() => this.checkBackendConnection(), CONFIG.HEALTH_CHECK_INTERVAL);
        
        // Load default page
        await this.loadPage('dashboard');
        
        this.initialized = true;
        console.log('✅ Application initialized successfully');
    },

    // Setup navigation event listeners
    setupNavigationListeners() {
        document.querySelectorAll('.top-nav-item').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const page = btn.getAttribute('data-page');
                if (page) {
                    await this.loadPage(page);
                    
                    // Update active state
                    document.querySelectorAll('.top-nav-item').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                }
            });
        });
    },

    // Load page content
    async loadPage(pageName) {
        this.currentPage = pageName;
        const contentTitle = document.getElementById('contentTitle');
        const contentBody = document.getElementById('contentBody');
        const contentActions = document.getElementById('contentActions');
        
        if (!contentBody) {
            console.error('Content body element not found');
            return;
        }

        // Show loading
        utils.showLoading(contentBody);
        contentActions.innerHTML = '';

        // Page titles
        const pageTitles = {
            'dashboard': '📊 Dashboard - Tổng quan hệ thống',
            'accounts': '👤 Quản lý tài khoản',
            'proxies': '🌐 Quản lý proxy',
            'tasks': '📋 Quản lý tác vụ',
            'logs': '📝 Nhật ký hoạt động',
            'settings': '⚙️ Cài đặt hệ thống'
        };

        contentTitle.textContent = pageTitles[pageName] || 'Bi Ads Multi Tool PRO';

        try {
            // Load page module
            switch (pageName) {
                case 'dashboard':
                    await Dashboard.init();
                    break;
                case 'accounts':
                    await Accounts.init();
                    break;
                case 'proxies':
                    await Proxies.init();
                    break;
                case 'tasks':
                    await Tasks.init();
                    break;
                case 'logs':
                    await Logs.init();
                    break;
                case 'settings':
                    Settings.init();
                    break;
                default:
                    contentBody.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">🔍</div>
                            <div class="empty-state-title">Trang không tồn tại</div>
                            <div class="empty-state-message">Trang "${pageName}" chưa được triển khai</div>
                        </div>
                    `;
            }
        } catch (error) {
            console.error(`Failed to load page ${pageName}:`, error);
            contentBody.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">❌</div>
                    <div class="empty-state-title">Lỗi tải trang</div>
                    <div class="empty-state-message">${utils.escapeHtml(error.message)}</div>
                    <button class="btn btn-primary" onclick="app.loadPage('${pageName}')">
                        ↻ Thử lại
                    </button>
                </div>
            `;
        }
    },

    // Check backend connection
    async checkBackendConnection() {
        const statusEl = document.getElementById('backendStatus');
        if (!statusEl) return;

        try {
            const health = await apiClient.healthCheck();
            
            if (health.status === 'healthy') {
                statusEl.className = 'backend-status online';
                statusEl.querySelector('.status-text').textContent = `Backend Online v${health.version}`;
                
                // Update database status if available
                if (health.database === 'online') {
                    statusEl.title = `Database: ${health.database}\nTelegram: ${health.telegram_configured ? 'Configured' : 'Not configured'}`;
                }
            } else {
                throw new Error('Backend is not healthy');
            }
        } catch (error) {
            statusEl.className = 'backend-status offline';
            statusEl.querySelector('.status-text').textContent = 'Backend Offline';
            statusEl.title = error.message;
            
            console.warn('Backend connection failed:', error);
        }
    },

    // Reload current page
    async reloadCurrentPage() {
        await this.loadPage(this.currentPage);
    },

    // Show notification
    showNotification(message, type = 'info') {
        utils.showToast(message, type);
    },

    // Show error
    showError(message) {
        utils.showToast(message, 'error');
    },

    // Show success
    showSuccess(message) {
        utils.showToast(message, 'success');
    },

    // Show confirmation dialog
    async confirm(message, title = 'Xác nhận') {
        return await utils.confirm(message, title);
    }
};

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => app.init());
} else {
    app.init();
}

// Make app available globally
window.app = app;

// Handle errors globally
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    utils.showToast('Đã xảy ra lỗi: ' + event.error.message, 'error');
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    utils.showToast('Lỗi không xử lý: ' + event.reason, 'error');
});

console.log('📱 Bi Ads Multi Tool PRO - Web Application');
console.log('🔗 Backend API:', window.API_URL);
console.log('📅 Version:', CONFIG.APP_VERSION);
