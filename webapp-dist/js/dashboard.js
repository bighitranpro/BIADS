// Dashboard Module for Bi Ads Multi Tool PRO v3.0

const Dashboard = {
    data: {
        stats: null,
        accounts: [],
        proxies: [],
        tasks: [],
        logs: []
    },

    async init() {
        await this.loadData();
        this.render();
        
        // Auto refresh every minute
        setInterval(() => this.loadData(), CONFIG.DATA_REFRESH_INTERVAL);
    },

    async loadData() {
        try {
            // Load all data in parallel
            const [stats, accounts, proxies, tasks, logs] = await Promise.all([
                apiClient.getStats(),
                apiClient.getAccounts(),
                apiClient.getProxies(),
                apiClient.getTasks(),
                apiClient.getLogs(10)
            ]);

            this.data = { stats, accounts, proxies, tasks, logs };
            this.render();
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            utils.showToast('Không thể tải dữ liệu dashboard', 'error');
        }
    },

    render() {
        const content = document.getElementById('contentBody');
        if (!content) return;

        const stats = this.data.stats || {
            accounts: { total: 0, active: 0, inactive: 0 },
            proxies: { total: 0, active: 0 },
            tasks: { total: 0, pending: 0, processing: 0, completed: 0, failed: 0 }
        };

        content.innerHTML = `
            <!-- Stats Overview -->
            <div class="stats-grid">
                ${components.createStatsCard(stats.accounts.total, 'Tổng tài khoản', '👤')}
                ${components.createStatsCard(stats.accounts.active, 'Tài khoản hoạt động', '✅')}
                ${components.createStatsCard(stats.proxies.total, 'Tổng proxy', '🌐')}
                ${components.createStatsCard(stats.proxies.active, 'Proxy hoạt động', '🟢')}
                ${components.createStatsCard(stats.tasks.total, 'Tổng tác vụ', '📋')}
                ${components.createStatsCard(stats.tasks.completed, 'Tác vụ hoàn thành', '✔️')}
            </div>

            <!-- Account Status Chart -->
            <div class="card">
                <div class="card-header">📊 Thống kê tài khoản</div>
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                        <div>
                            <h4 style="color: #667eea; margin-bottom: 15px;">Trạng thái tài khoản</h4>
                            ${components.createProgressBar(
                                stats.accounts.total > 0 ? Math.round((stats.accounts.active / stats.accounts.total) * 100) : 0,
                                `Active: ${stats.accounts.active}/${stats.accounts.total}`
                            )}
                            ${components.createProgressBar(
                                stats.accounts.total > 0 ? Math.round((stats.accounts.inactive / stats.accounts.total) * 100) : 0,
                                `Inactive: ${stats.accounts.inactive}/${stats.accounts.total}`
                            )}
                        </div>
                        <div>
                            <h4 style="color: #667eea; margin-bottom: 15px;">Proxy</h4>
                            ${components.createProgressBar(
                                stats.proxies.total > 0 ? Math.round((stats.proxies.active / stats.proxies.total) * 100) : 0,
                                `Active: ${stats.proxies.active}/${stats.proxies.total}`
                            )}
                            ${components.createProgressBar(
                                stats.accounts.total > 0 ? Math.round((stats.accounts.with_proxy / stats.accounts.total) * 100) : 0,
                                `Accounts with proxy: ${stats.accounts.with_proxy}/${stats.accounts.total}`
                            )}
                        </div>
                        <div>
                            <h4 style="color: #667eea; margin-bottom: 15px;">Tác vụ</h4>
                            ${components.createProgressBar(
                                stats.tasks.total > 0 ? Math.round((stats.tasks.completed / stats.tasks.total) * 100) : 0,
                                `Completed: ${stats.tasks.completed}/${stats.tasks.total}`
                            )}
                            ${components.createProgressBar(
                                stats.tasks.total > 0 ? Math.round((stats.tasks.failed / stats.tasks.total) * 100) : 0,
                                `Failed: ${stats.tasks.failed}/${stats.tasks.total}`
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="card">
                <div class="card-header">📝 Hoạt động gần đây</div>
                <div class="card-body">
                    ${this.renderRecentLogs()}
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="card">
                <div class="card-header">⚡ Thao tác nhanh</div>
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        <button class="btn btn-primary" onclick="app.loadPage('accounts')">
                            👤 Quản lý tài khoản
                        </button>
                        <button class="btn btn-primary" onclick="app.loadPage('proxies')">
                            🌐 Quản lý proxy
                        </button>
                        <button class="btn btn-primary" onclick="app.loadPage('tasks')">
                            📋 Tạo tác vụ mới
                        </button>
                        <button class="btn btn-secondary" onclick="Dashboard.exportData()">
                            💾 Xuất dữ liệu
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    renderRecentLogs() {
        if (!this.data.logs || this.data.logs.length === 0) {
            return '<p style="text-align: center; color: #888;">Chưa có hoạt động nào</p>';
        }

        const logsHtml = this.data.logs.slice(0, 10).map(log => {
            const levelIcons = {
                'info': 'ℹ️',
                'success': '✅',
                'warning': '⚠️',
                'error': '❌'
            };
            return `
                <div style="padding: 10px; margin: 5px 0; background: rgba(255,255,255,0.03); border-left: 3px solid ${
                    log.level === 'error' ? '#e74c3c' : log.level === 'success' ? '#2ecc71' : '#667eea'
                }; border-radius: 4px;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <span style="margin-right: 8px;">${levelIcons[log.level] || 'ℹ️'}</span>
                            <span style="color: #e0e0e0;">${utils.escapeHtml(log.message)}</span>
                        </div>
                        <div style="color: #888; font-size: 12px; white-space: nowrap; margin-left: 15px;">
                            ${utils.formatRelativeTime(log.timestamp)}
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div style="max-height: 400px; overflow-y: auto;">
                ${logsHtml}
            </div>
        `;
    },

    async exportData() {
        try {
            const data = {
                stats: this.data.stats,
                accounts: this.data.accounts.length,
                proxies: this.data.proxies.length,
                tasks: this.data.tasks.length,
                exported_at: new Date().toISOString()
            };

            utils.downloadFile(
                JSON.stringify(data, null, 2),
                `bi-ads-stats-${new Date().toISOString().split('T')[0]}.json`,
                'application/json'
            );

            utils.showToast('Đã xuất dữ liệu thành công', 'success');
        } catch (error) {
            console.error('Export failed:', error);
            utils.showToast('Không thể xuất dữ liệu', 'error');
        }
    }
};

// Make Dashboard available globally
window.Dashboard = Dashboard;
