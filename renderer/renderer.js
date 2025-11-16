// Bi Ads - Multi Tool PRO v2.0 - Main Renderer Script
// This file handles navigation, UI interactions, and tool loading

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global App State
const app = {
    currentTool: 'dashboard',
    user: null,
    backendConnected: false
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    console.log('Bi Ads - Multi Tool PRO v2.0 loaded!');
    
    // Check backend connection
    checkBackendConnection();
    
    // Setup navigation
    setupNavigation();
    
    // Load default tool
    loadTool('dashboard');
    
    // Setup top bar actions
    setupTopBarActions();
    
    // Check backend every 10 seconds
    setInterval(checkBackendConnection, 10000);
});

// Setup Navigation
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tool = item.getAttribute('data-tool');
            
            // Remove active class from all items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Add active class to clicked item
            item.classList.add('active');
            
            // Load the tool
            loadTool(tool);
        });
    });
}

// Load Tool Content
function loadTool(toolName) {
    app.currentTool = toolName;
    const container = document.getElementById('contentContainer');
    const toolNameEl = document.getElementById('currentToolName');
    
    // Update breadcrumb
    const toolNames = {
        'dashboard': 'Trang Chủ',
        'facebook': 'Facebook Pro',
        'instagram': 'Instagram Pro',
        'youtube': 'YouTube Pro',
        'tiktok': 'TikTok Pro',
        'tools': 'Công Cụ',
        'settings': 'Cài Đặt'
    };
    
    toolNameEl.textContent = toolNames[toolName] || toolName;
    
    // Load tool content
    switch(toolName) {
        case 'dashboard':
            container.innerHTML = renderDashboard();
            break;
        case 'facebook':
            if (window.facebookPro && typeof window.facebookPro.init === 'function') {
                window.facebookPro.init();
            } else {
                container.innerHTML = `
                    <div class="card">
                        <div class="card-header">⚠️ Facebook Pro Module</div>
                        <div class="card-body">
                            <p style="color: #f39c12;">Module đang được tải...</p>
                        </div>
                    </div>
                `;
            }
            break;
        case 'instagram':
            container.innerHTML = renderComingSoon('Instagram');
            break;
        case 'youtube':
            container.innerHTML = renderComingSoon('YouTube');
            break;
        case 'tiktok':
            container.innerHTML = renderComingSoon('TikTok');
            break;
        case 'tools':
            container.innerHTML = renderTools();
            break;
        case 'settings':
            container.innerHTML = renderSettings();
            break;
        default:
            container.innerHTML = renderDashboard();
    }
}

// Render Dashboard
function renderDashboard() {
    return `
        <div class="card">
            <div class="card-header">📊 Dashboard Overview</div>
            <div class="card-body">
                <div class="grid-3">
                    <div class="stat-card">
                        <div class="stat-value">0</div>
                        <div class="stat-label">Facebook Accounts</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">0</div>
                        <div class="stat-label">Instagram Accounts</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">0</div>
                        <div class="stat-label">Total Tasks</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">🚀 Quick Actions</div>
            <div class="card-body">
                <div class="grid-2">
                    <button onclick="loadTool('facebook')">
                        📘 Open Facebook Pro
                    </button>
                    <button onclick="loadTool('instagram')">
                        📷 Open Instagram
                    </button>
                    <button onclick="loadTool('youtube')">
                        ▶️ Open YouTube
                    </button>
                    <button onclick="loadTool('tools')">
                        🔧 Open Tools
                    </button>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">📋 Recent Activity</div>
            <div class="card-body">
                <p style="color: #888; text-align: center;">Chưa có hoạt động nào</p>
            </div>
        </div>
    `;
}

// Render Coming Soon
function renderComingSoon(toolName) {
    return `
        <div class="card">
            <div class="card-header">🚧 ${toolName}</div>
            <div class="card-body">
                <div style="text-align: center; padding: 40px;">
                    <h2 style="font-size: 48px; margin-bottom: 20px;">🚧</h2>
                    <h3 style="color: #fff; margin-bottom: 10px;">Coming Soon</h3>
                    <p style="color: #888;">Module ${toolName} đang được phát triển</p>
                </div>
            </div>
        </div>
    `;
}

// Render Tools
function renderTools() {
    return `
        <div class="card">
            <div class="card-header">🔧 Utility Tools</div>
            <div class="card-body">
                <div class="grid-2">
                    <button onclick="app.showNotification('Text Generator', 'Feature coming soon!')">
                        📝 Text Generator
                    </button>
                    <button onclick="app.showNotification('Image Editor', 'Feature coming soon!')">
                        🖼️ Image Editor
                    </button>
                    <button onclick="app.showNotification('Video Downloader', 'Feature coming soon!')">
                        📥 Video Downloader
                    </button>
                    <button onclick="app.showNotification('Hash Generator', 'Feature coming soon!')">
                        🔐 Hash Generator
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Render Settings
function renderSettings() {
    return `
        <div class="card">
            <div class="card-header">⚙️ Application Settings</div>
            <div class="card-body">
                <div style="margin-bottom: 20px;">
                    <label>
                        <input type="checkbox" checked>
                        Enable notifications
                    </label>
                </div>
                <div style="margin-bottom: 20px;">
                    <label>
                        <input type="checkbox" checked>
                        Auto-save logs
                    </label>
                </div>
                <div style="margin-bottom: 20px;">
                    <label>
                        <input type="checkbox">
                        Dark mode (always on)
                    </label>
                </div>
                <button class="btn-primary">💾 Save Settings</button>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">ℹ️ About</div>
            <div class="card-body">
                <p style="margin-bottom: 10px;"><strong>Version:</strong> 1.0.0</p>
                <p style="margin-bottom: 10px;"><strong>Build:</strong> 2024.01</p>
                <p style="margin-bottom: 10px;"><strong>Author:</strong> Multi Tool Team</p>
            </div>
        </div>
    `;
}

// Setup Top Bar Actions
function setupTopBarActions() {
    const btnNotifications = document.getElementById('btnNotifications');
    const btnHelp = document.getElementById('btnHelp');
    
    btnNotifications.addEventListener('click', () => {
        app.showNotification('Notifications', 'No new notifications');
    });
    
    btnHelp.addEventListener('click', () => {
        app.showNotification('Help', 'Documentation coming soon!');
    });
}

// Show Notification
app.showNotification = function(title, message, type = 'info') {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    
    const icons = {
        'info': 'ℹ️',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️'
    };
    
    modal.innerHTML = `
        <div class="modal" style="max-width: 400px;">
            <div class="modal-header">
                <div class="modal-title">${icons[type]} ${title}</div>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
            </div>
            <div class="modal-body">
                <p style="color: #e0e0e0;">${message}</p>
            </div>
            <div class="modal-footer">
                <button onclick="this.closest('.modal-overlay').remove()">OK</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Auto close after 3 seconds
    setTimeout(() => {
        if (modal.parentElement) {
            modal.remove();
        }
    }, 3000);
};

// Export app to window for access in other scripts
window.app = app;

console.log('Renderer script initialized!');
