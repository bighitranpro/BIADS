/**
 * Bi Ads - Dashboard với thống kê real-time
 * Author: Bi Ads Team
 * Version: 3.0.0
 */

const Dashboard = {
    refreshInterval: null,
    charts: {},
    
    /**
     * Khởi tạo dashboard
     */
    init: function() {
        this.startAutoRefresh();
        this.loadAllStats();
    },
    
    /**
     * Render dashboard page
     */
    render: function(content) {
        content.innerHTML = `
            <div class="dashboard-container">
                <!-- Header -->
                <div class="dashboard-header">
                    <h1>📊 Dashboard - Tổng quan hệ thống</h1>
                    <div class="dashboard-actions">
                        <button class="btn-primary" onclick="Dashboard.refreshAll()">
                            🔄 Làm mới
                        </button>
                        <button class="btn-secondary" onclick="Dashboard.exportReport()">
                            📥 Xuất báo cáo
                        </button>
                    </div>
                </div>
                
                <!-- Thống kê tổng quan -->
                <div class="stats-overview">
                    <div class="stat-card stat-accounts">
                        <div class="stat-icon">👥</div>
                        <div class="stat-content">
                            <h3 id="totalAccounts">0</h3>
                            <p>Tổng tài khoản</p>
                            <span class="stat-detail">
                                <span class="stat-success" id="activeAccounts">0 active</span>
                                <span class="stat-danger" id="deadAccounts">0 dead</span>
                            </span>
                        </div>
                    </div>
                    
                    <div class="stat-card stat-proxies">
                        <div class="stat-icon">🌐</div>
                        <div class="stat-content">
                            <h3 id="totalProxies">0</h3>
                            <p>Proxy khả dụng</p>
                            <span class="stat-detail">
                                <span class="stat-success" id="activeProxies">0 hoạt động</span>
                            </span>
                        </div>
                    </div>
                    
                    <div class="stat-card stat-tasks">
                        <div class="stat-icon">⚙️</div>
                        <div class="stat-content">
                            <h3 id="totalTasks">0</h3>
                            <p>Tác vụ đang chạy</p>
                            <span class="stat-detail">
                                <span class="stat-warning" id="pendingTasks">0 chờ xử lý</span>
                            </span>
                        </div>
                    </div>
                    
                    <div class="stat-card stat-posts">
                        <div class="stat-icon">📝</div>
                        <div class="stat-content">
                            <h3 id="totalPosts">0</h3>
                            <p>Bài đăng hôm nay</p>
                            <span class="stat-detail">
                                <span class="stat-info" id="totalInteractions">0 tương tác</span>
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- Biểu đồ -->
                <div class="dashboard-charts">
                    <!-- Chart: Hoạt động theo giờ -->
                    <div class="card chart-card">
                        <div class="card-header">
                            📈 Hoạt động theo giờ (24h qua)
                        </div>
                        <div class="card-body">
                            <canvas id="activityChart" height="80"></canvas>
                        </div>
                    </div>
                    
                    <!-- Chart: Tài khoản theo trạng thái -->
                    <div class="card chart-card">
                        <div class="card-header">
                            🎯 Phân bổ tài khoản
                        </div>
                        <div class="card-body">
                            <canvas id="accountsChart" height="80"></canvas>
                        </div>
                    </div>
                </div>
                
                <!-- Hoạt động gần đây -->
                <div class="card">
                    <div class="card-header">
                        🕐 Hoạt động gần đây
                        <button class="btn-sm btn-secondary" onclick="Dashboard.loadRecentActivities()">
                            Làm mới
                        </button>
                    </div>
                    <div class="card-body">
                        <div id="recentActivities">
                            <div class="loading">
                                <div class="spinner"></div>
                                <p>Đang tải...</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Tài khoản cần chú ý -->
                <div class="card">
                    <div class="card-header">
                        ⚠️ Tài khoản cần chú ý
                    </div>
                    <div class="card-body">
                        <div id="warningAccounts">
                            <div class="loading">
                                <div class="spinner"></div>
                                <p>Đang tải...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Load dữ liệu
        setTimeout(() => {
            this.loadAllStats();
            this.initCharts();
        }, 100);
    },
    
    /**
     * Load tất cả thống kê
     */
    loadAllStats: async function() {
        try {
            await Promise.all([
                this.loadAccountStats(),
                this.loadProxyStats(),
                this.loadTaskStats(),
                this.loadPostStats(),
                this.loadRecentActivities(),
                this.loadWarningAccounts()
            ]);
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    },
    
    /**
     * Load thống kê tài khoản
     */
    loadAccountStats: async function() {
        try {
            const accounts = await apiClient.getAccounts();
            
            const total = accounts.length;
            const active = accounts.filter(a => a.status === 'active').length;
            const dead = accounts.filter(a => a.status === 'dead').length;
            
            document.getElementById('totalAccounts').textContent = total;
            document.getElementById('activeAccounts').textContent = `${active} active`;
            document.getElementById('deadAccounts').textContent = `${dead} dead`;
            
            // Animate số
            this.animateNumber('totalAccounts', 0, total, 1000);
        } catch (error) {
            console.error('Error loading account stats:', error);
        }
    },
    
    /**
     * Load thống kê proxy
     */
    loadProxyStats: async function() {
        try {
            const proxies = await apiClient.getProxies();
            
            const total = proxies.length;
            const active = proxies.filter(p => p.status === 'active').length;
            
            document.getElementById('totalProxies').textContent = total;
            document.getElementById('activeProxies').textContent = `${active} hoạt động`;
            
            this.animateNumber('totalProxies', 0, total, 1000);
        } catch (error) {
            console.error('Error loading proxy stats:', error);
        }
    },
    
    /**
     * Load thống kê tác vụ
     */
    loadTaskStats: async function() {
        try {
            // Mock data - cần implement API thật
            const total = 5;
            const pending = 2;
            
            document.getElementById('totalTasks').textContent = total;
            document.getElementById('pendingTasks').textContent = `${pending} chờ xử lý`;
            
            this.animateNumber('totalTasks', 0, total, 1000);
        } catch (error) {
            console.error('Error loading task stats:', error);
        }
    },
    
    /**
     * Load thống kê bài đăng
     */
    loadPostStats: async function() {
        try {
            // Mock data - cần implement API thật
            const total = 12;
            const interactions = 348;
            
            document.getElementById('totalPosts').textContent = total;
            document.getElementById('totalInteractions').textContent = `${interactions} tương tác`;
            
            this.animateNumber('totalPosts', 0, total, 1000);
        } catch (error) {
            console.error('Error loading post stats:', error);
        }
    },
    
    /**
     * Load hoạt động gần đây
     */
    loadRecentActivities: async function() {
        const container = document.getElementById('recentActivities');
        if (!container) return;
        
        try {
            // Mock data - cần implement API thật
            const activities = [
                {
                    type: 'success',
                    icon: '✅',
                    action: 'Đăng bài thành công',
                    account: 'Nguyễn Văn A',
                    time: '2 phút trước'
                },
                {
                    type: 'info',
                    icon: '📝',
                    action: 'Import tài khoản',
                    account: 'Hệ thống',
                    time: '15 phút trước'
                },
                {
                    type: 'warning',
                    icon: '⚠️',
                    action: 'Tài khoản checkpoint',
                    account: 'Trần Thị B',
                    time: '1 giờ trước'
                },
                {
                    type: 'success',
                    icon: '👍',
                    action: 'Like bài viết',
                    account: 'Lê Văn C',
                    time: '2 giờ trước'
                },
                {
                    type: 'info',
                    icon: '💬',
                    action: 'Comment bài viết',
                    account: 'Phạm Thị D',
                    time: '3 giờ trước'
                }
            ];
            
            container.innerHTML = `
                <div class="activity-timeline">
                    ${activities.map(activity => `
                        <div class="activity-item activity-${activity.type}">
                            <div class="activity-icon">${activity.icon}</div>
                            <div class="activity-content">
                                <div class="activity-title">${activity.action}</div>
                                <div class="activity-meta">
                                    <span class="activity-account">${activity.account}</span>
                                    <span class="activity-time">${activity.time}</span>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            container.innerHTML = `
                <div class="error-message">
                    ❌ Không thể tải hoạt động gần đây
                </div>
            `;
        }
    },
    
    /**
     * Load tài khoản cần chú ý
     */
    loadWarningAccounts: async function() {
        const container = document.getElementById('warningAccounts');
        if (!container) return;
        
        try {
            const accounts = await apiClient.getAccounts();
            const warningAccounts = accounts.filter(a => 
                a.status === 'checkpoint' || a.status === 'dead'
            ).slice(0, 5);
            
            if (warningAccounts.length === 0) {
                container.innerHTML = `
                    <div class="info-message">
                        ✅ Tất cả tài khoản đều hoạt động tốt
                    </div>
                `;
                return;
            }
            
            container.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>UID</th>
                            <th>Tên</th>
                            <th>Trạng thái</th>
                            <th>Hành động</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${warningAccounts.map(acc => `
                            <tr>
                                <td><code>${acc.uid}</code></td>
                                <td>${acc.name || 'N/A'}</td>
                                <td>
                                    <span class="badge badge-${acc.status === 'checkpoint' ? 'warning' : 'danger'}">
                                        ${acc.status.toUpperCase()}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn-sm btn-primary" onclick="BiAds.checkAccountStatus(${acc.id})">
                                        Kiểm tra
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } catch (error) {
            container.innerHTML = `
                <div class="error-message">
                    ❌ Không thể tải danh sách tài khoản
                </div>
            `;
        }
    },
    
    /**
     * Khởi tạo biểu đồ
     */
    initCharts: function() {
        this.initActivityChart();
        this.initAccountsChart();
    },
    
    /**
     * Biểu đồ hoạt động theo giờ
     */
    initActivityChart: function() {
        const ctx = document.getElementById('activityChart');
        if (!ctx) return;
        
        // Mock data cho 24 giờ qua
        const hours = Array.from({length: 24}, (_, i) => `${i}:00`);
        const data = Array.from({length: 24}, () => Math.floor(Math.random() * 50));
        
        this.charts.activity = this.createLineChart(ctx, {
            labels: hours,
            datasets: [{
                label: 'Hoạt động',
                data: data,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        });
    },
    
    /**
     * Biểu đồ tài khoản
     */
    initAccountsChart: function() {
        const ctx = document.getElementById('accountsChart');
        if (!ctx) return;
        
        this.charts.accounts = this.createDoughnutChart(ctx, {
            labels: ['Active', 'Dead', 'Checkpoint', 'Inactive'],
            datasets: [{
                data: [45, 10, 5, 8],
                backgroundColor: [
                    '#38ef7d',
                    '#f45c43',
                    '#fee140',
                    '#888'
                ]
            }]
        });
    },
    
    /**
     * Tạo line chart
     */
    createLineChart: function(ctx, data) {
        // Simple implementation without Chart.js
        // You can integrate Chart.js for better charts
        return {
            ctx: ctx,
            data: data,
            update: function(newData) {
                this.data = newData;
                // Re-render chart
            }
        };
    },
    
    /**
     * Tạo doughnut chart
     */
    createDoughnutChart: function(ctx, data) {
        // Simple implementation
        return {
            ctx: ctx,
            data: data,
            update: function(newData) {
                this.data = newData;
            }
        };
    },
    
    /**
     * Animate số
     */
    animateNumber: function(elementId, start, end, duration) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                element.textContent = end;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 16);
    },
    
    /**
     * Tự động làm mới
     */
    startAutoRefresh: function() {
        // Làm mới mỗi 30 giây
        this.refreshInterval = setInterval(() => {
            this.loadAllStats();
        }, 30000);
    },
    
    /**
     * Dừng tự động làm mới
     */
    stopAutoRefresh: function() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    },
    
    /**
     * Làm mới tất cả
     */
    refreshAll: async function() {
        const btn = event.target;
        btn.disabled = true;
        btn.innerHTML = '⏳ Đang làm mới...';
        
        try {
            await this.loadAllStats();
            btn.innerHTML = '✅ Đã làm mới!';
            setTimeout(() => {
                btn.disabled = false;
                btn.innerHTML = '🔄 Làm mới';
            }, 2000);
        } catch (error) {
            btn.innerHTML = '❌ Lỗi!';
            setTimeout(() => {
                btn.disabled = false;
                btn.innerHTML = '🔄 Làm mới';
            }, 2000);
        }
    },
    
    /**
     * Xuất báo cáo
     */
    exportReport: async function() {
        try {
            // Thu thập dữ liệu
            const data = {
                generatedAt: new Date().toISOString(),
                accounts: await apiClient.getAccounts(),
                proxies: await apiClient.getProxies(),
                // Thêm dữ liệu khác
            };
            
            // Tạo JSON
            const json = JSON.stringify(data, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            // Download
            const a = document.createElement('a');
            a.href = url;
            a.download = `bi-ads-report-${Date.now()}.json`;
            a.click();
            
            URL.revokeObjectURL(url);
            
            alert('✅ Đã xuất báo cáo thành công!');
        } catch (error) {
            alert('❌ Lỗi xuất báo cáo: ' + error.message);
        }
    },
    
    /**
     * Cleanup khi rời khỏi trang
     */
    destroy: function() {
        this.stopAutoRefresh();
    }
};

// Export
window.Dashboard = Dashboard;
