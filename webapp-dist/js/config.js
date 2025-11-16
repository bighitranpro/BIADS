// Configuration for Bi Ads Multi Tool PRO v3.0

const CONFIG = {
    // API Configuration
    API_BASE_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:8000' 
        : `${window.location.protocol}//${window.location.hostname}:8000`,
    
    // Auto-detect backend URL based on current location
    getApiUrl: function() {
        // If accessing via IP like 35.247.153.179:3000, use same IP for backend
        const hostname = window.location.hostname;
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }
        // Use same hostname but port 8000 for backend
        return `http://${hostname}:8000`;
    },
    
    // Application Info
    APP_NAME: 'Bi Ads - Multi Tool PRO',
    APP_VERSION: '3.0.0',
    APP_DESCRIPTION: 'Công cụ quản lý tài khoản Facebook chuyên nghiệp',
    
    // Refresh Intervals (milliseconds)
    HEALTH_CHECK_INTERVAL: 30000,  // 30 seconds
    DATA_REFRESH_INTERVAL: 60000,   // 1 minute
    
    // Pagination
    DEFAULT_PAGE_SIZE: 50,
    
    // Toast Notification Duration
    TOAST_DURATION: 5000,  // 5 seconds
    
    // Task Status Colors
    TASK_STATUS_COLORS: {
        'pending': 'warning',
        'processing': 'info',
        'completed': 'success',
        'failed': 'danger'
    },
    
    // Account Status Colors
    ACCOUNT_STATUS_COLORS: {
        'active': 'success',
        'inactive': 'warning',
        'dead': 'danger'
    },
    
    // Proxy Status Colors
    PROXY_STATUS_COLORS: {
        'active': 'success',
        'inactive': 'danger'
    }
};

// Make API URL available globally
window.API_URL = CONFIG.getApiUrl();

console.log(`🚀 ${CONFIG.APP_NAME} v${CONFIG.APP_VERSION}`);
console.log(`📡 API URL: ${window.API_URL}`);
