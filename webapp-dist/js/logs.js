// Logs Module
const Logs = {
    data: { logs: [] },
    
    async init() {
        await this.loadData();
        this.render();
    },
    
    async loadData() {
        try {
            this.data.logs = await apiClient.getLogs(500);
        } catch (error) {
            utils.showToast('Không thể tải nhật ký', 'error');
        }
    },
    
    render() {
        const content = document.getElementById('contentBody');
        const actions = document.getElementById('contentActions');
        
        actions.innerHTML = components.createActionBar([
            { id: 'btnRefreshLogs', label: 'Làm mới', icon: '↻', class: 'btn-secondary' },
            { id: 'btnClearLogs', label: 'Xóa tất cả', icon: '🗑️', class: 'btn-danger' }
        ]);
        
        content.innerHTML = `
            <div class="card">
                <div class="card-header">📝 Nhật ký hoạt động (${this.data.logs.length} mục)</div>
                <div class="card-body">
                    <div style="max-height: 600px; overflow-y: auto;">
                        ${this.renderLogs()}
                    </div>
                </div>
            </div>
        `;
        
        this.setupEventListeners();
    },
    
    renderLogs() {
        if (this.data.logs.length === 0) {
            return '<p style="text-align: center; color: #888; padding: 40px;">Chưa có nhật ký nào</p>';
        }
        
        const levelIcons = { info: 'ℹ️', success: '✅', warning: '⚠️', error: '❌' };
        const levelColors = { info: '#3498db', success: '#2ecc71', warning: '#f39c12', error: '#e74c3c' };
        
        return this.data.logs.map(log => `
            <div style="padding: 12px; margin: 8px 0; background: rgba(255,255,255,0.03); border-left: 3px solid ${levelColors[log.level] || '#3498db'}; border-radius: 4px;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <span style="margin-right: 10px;">${levelIcons[log.level] || 'ℹ️'}</span>
                        <span style="color: #e0e0e0;">${utils.escapeHtml(log.message)}</span>
                    </div>
                    <div style="color: #888; font-size: 11px; white-space: nowrap; margin-left: 15px;">
                        ${utils.formatRelativeTime(log.timestamp)}
                    </div>
                </div>
                ${log.details ? `<div style="margin-left: 35px; margin-top: 5px; font-size: 12px; color: #888;">${utils.escapeHtml(log.details)}</div>` : ''}
            </div>
        `).join('');
    },
    
    setupEventListeners() {
        document.getElementById('btnRefreshLogs')?.addEventListener('click', () => {
            this.init();
            utils.showToast('Đã làm mới', 'success');
        });
        
        document.getElementById('btnClearLogs')?.addEventListener('click', async () => {
            if (await utils.confirm('Xóa tất cả nhật ký?', 'Cảnh báo')) {
                await apiClient.clearLogs();
                utils.showToast('Đã xóa tất cả nhật ký', 'success');
                await this.init();
            }
        });
    }
};

window.Logs = Logs;
