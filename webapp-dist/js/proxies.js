// Proxies Module for Bi Ads Multi Tool PRO v3.0

const Proxies = {
    data: {
        proxies: [],
        filteredProxies: []
    },

    async init() {
        await this.loadData();
        this.render();
    },

    async loadData() {
        try {
            const proxies = await apiClient.getProxies();
            this.data.proxies = proxies;
            this.data.filteredProxies = proxies;
        } catch (error) {
            console.error('Failed to load proxies:', error);
            utils.showToast('Không thể tải danh sách proxy', 'error');
        }
    },

    render() {
        const content = document.getElementById('contentBody');
        const actions = document.getElementById('contentActions');
        
        if (!content) return;

        actions.innerHTML = components.createActionBar([
            { id: 'btnAddProxy', label: 'Thêm proxy', icon: '➕', class: 'btn-primary' },
            { id: 'btnImportProxies', label: 'Import bulk', icon: '📥', class: 'btn-success' },
            { id: 'btnExportProxies', label: 'Export', icon: '📤', class: 'btn-secondary' },
            { id: 'btnRefreshProxies', label: 'Làm mới', icon: '↻', class: 'btn-secondary' }
        ]);

        content.innerHTML = `
            <!-- Stats -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px;">
                <div style="background: rgba(46, 204, 113, 0.1); padding: 15px; border-radius: 8px; border-left: 3px solid #2ecc71;">
                    <div style="font-size: 24px; font-weight: bold; color: #2ecc71;">${this.data.proxies.length}</div>
                    <div style="font-size: 12px; color: #888;">Tổng proxy</div>
                </div>
                <div style="background: rgba(52, 152, 219, 0.1); padding: 15px; border-radius: 8px; border-left: 3px solid #3498db;">
                    <div style="font-size: 24px; font-weight: bold; color: #3498db;">${this.data.proxies.filter(p => p.status === 'active').length}</div>
                    <div style="font-size: 12px; color: #888;">Active</div>
                </div>
            </div>

            <!-- Proxies Table -->
            <div class="card">
                <div class="card-header">🌐 Danh sách proxy (${this.data.filteredProxies.length})</div>
                <div class="card-body">
                    <div id="proxiesTableContainer">${this.renderTable()}</div>
                </div>
            </div>
        `;

        this.setupEventListeners();
    },

    renderTable() {
        const columns = [
            { field: 'id', label: 'ID' },
            { field: 'ip', label: 'IP' },
            { field: 'port', label: 'Port' },
            { field: 'protocol', label: 'Protocol' },
            { 
                field: 'status', 
                label: 'Trạng thái',
                render: (value) => utils.getStatusBadge(value, 'proxy')
            },
            {
                field: 'created_at',
                label: 'Ngày tạo',
                render: (value) => utils.formatDate(value)
            }
        ];

        const actions = [
            { name: 'edit', label: 'Sửa', icon: '✏️', class: 'btn-warning' },
            { name: 'delete', label: 'Xóa', icon: '🗑️', class: 'btn-danger' }
        ];

        return components.createTable(columns, this.data.filteredProxies, actions);
    },

    setupEventListeners() {
        document.getElementById('btnAddProxy')?.addEventListener('click', () => this.showAddModal());
        document.getElementById('btnImportProxies')?.addEventListener('click', () => this.showImportModal());
        document.getElementById('btnExportProxies')?.addEventListener('click', () => this.exportProxies());
        document.getElementById('btnRefreshProxies')?.addEventListener('click', () => {
            this.init();
            utils.showToast('Đã làm mới danh sách', 'success');
        });
        this.setupTableActions();
    },

    setupTableActions() {
        document.querySelectorAll('[data-action="edit"]').forEach(btn => {
            btn.addEventListener('click', () => this.showEditModal(parseInt(btn.dataset.id)));
        });

        document.querySelectorAll('[data-action="delete"]').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                if (await utils.confirm('Bạn có chắc chắn muốn xóa proxy này?')) {
                    await this.deleteProxy(id);
                }
            });
        });
    },

    showAddModal() {
        const bodyHtml = `
            <form id="proxyForm">
                ${components.createFormField({ type: 'text', name: 'ip', label: 'IP Address', required: true, placeholder: '192.168.1.1' })}
                ${components.createFormField({ type: 'number', name: 'port', label: 'Port', required: true, placeholder: '8080' })}
                ${components.createFormField({ 
                    type: 'select', 
                    name: 'protocol', 
                    label: 'Protocol',
                    options: [
                        { value: 'http', label: 'HTTP' },
                        { value: 'https', label: 'HTTPS' },
                        { value: 'socks4', label: 'SOCKS4' },
                        { value: 'socks5', label: 'SOCKS5' }
                    ]
                })}
                ${components.createFormField({ type: 'text', name: 'username', label: 'Username (optional)' })}
                ${components.createFormField({ type: 'password', name: 'password', label: 'Password (optional)' })}
            </form>
        `;

        const modal = components.createModal('➕ Thêm proxy mới', bodyHtml, [
            { text: 'Hủy', class: 'btn-secondary', onClick: () => modal.close() },
            { text: 'Thêm', class: 'btn-primary', onClick: async () => { await this.saveProxy(); modal.close(); }}
        ]);
    },

    showEditModal(id) {
        const proxy = this.data.proxies.find(p => p.id === id);
        if (!proxy) return;

        const bodyHtml = `
            <form id="proxyForm">
                <input type="hidden" name="id" value="${proxy.id}">
                ${components.createFormField({ type: 'text', name: 'ip', label: 'IP Address', value: proxy.ip, required: true })}
                ${components.createFormField({ type: 'number', name: 'port', label: 'Port', value: proxy.port, required: true })}
                ${components.createFormField({ 
                    type: 'select', 
                    name: 'protocol', 
                    label: 'Protocol',
                    value: proxy.protocol,
                    options: [
                        { value: 'http', label: 'HTTP' },
                        { value: 'https', label: 'HTTPS' },
                        { value: 'socks4', label: 'SOCKS4' },
                        { value: 'socks5', label: 'SOCKS5' }
                    ]
                })}
                ${components.createFormField({ 
                    type: 'select', 
                    name: 'status', 
                    label: 'Trạng thái',
                    value: proxy.status,
                    options: [
                        { value: 'active', label: 'Active' },
                        { value: 'inactive', label: 'Inactive' }
                    ]
                })}
            </form>
        `;

        const modal = components.createModal('✏️ Chỉnh sửa proxy', bodyHtml, [
            { text: 'Hủy', class: 'btn-secondary', onClick: () => modal.close() },
            { text: 'Lưu', class: 'btn-primary', onClick: async () => { await this.saveProxy(id); modal.close(); }}
        ]);
    },

    showImportModal() {
        const bodyHtml = `
            <div>
                <p style="color: #888; margin-bottom: 15px;">Nhập danh sách proxy (mỗi dòng một proxy)</p>
                <textarea id="proxyListInput" class="form-textarea" rows="10" placeholder="Format: ip:port hoặc ip:port:username:password"></textarea>
                <p style="color: #888; font-size: 12px; margin-top: 10px;">
                    Ví dụ: 192.168.1.1:8080 hoặc 192.168.1.1:8080:user:pass
                </p>
            </div>
        `;

        const modal = components.createModal('📥 Import proxy bulk', bodyHtml, [
            { text: 'Hủy', class: 'btn-secondary', onClick: () => modal.close() },
            { text: 'Import', class: 'btn-primary', onClick: async () => { await this.importProxies(); modal.close(); }}
        ]);
    },

    async saveProxy(id = null) {
        const form = document.getElementById('proxyForm');
        const formData = new FormData(form);
        
        const proxyData = {
            ip: formData.get('ip'),
            port: parseInt(formData.get('port')),
            protocol: formData.get('protocol'),
            username: formData.get('username') || '',
            password: formData.get('password') || '',
            status: formData.get('status') || 'active'
        };

        try {
            if (id) {
                await apiClient.updateProxy(id, proxyData);
                utils.showToast('Đã cập nhật proxy', 'success');
            } else {
                await apiClient.createProxy(proxyData);
                utils.showToast('Đã thêm proxy mới', 'success');
            }
            await this.init();
        } catch (error) {
            utils.showToast('Lỗi: ' + error.message, 'error');
        }
    },

    async deleteProxy(id) {
        try {
            await apiClient.deleteProxy(id);
            utils.showToast('Đã xóa proxy', 'success');
            await this.init();
        } catch (error) {
            utils.showToast('Lỗi: ' + error.message, 'error');
        }
    },

    async importProxies() {
        const input = document.getElementById('proxyListInput');
        const text = input?.value.trim();
        
        if (!text) {
            utils.showToast('Vui lòng nhập danh sách proxy', 'warning');
            return;
        }

        const lines = text.split('\n').filter(line => line.trim());
        const proxies = lines.map(line => {
            const parsed = utils.parseProxyString(line.trim());
            return parsed;
        }).filter(p => p !== null);

        if (proxies.length === 0) {
            utils.showToast('Không có proxy hợp lệ', 'warning');
            return;
        }

        try {
            await apiClient.importProxies(proxies);
            utils.showToast(`Đã import ${proxies.length} proxy`, 'success');
            await this.init();
        } catch (error) {
            utils.showToast('Lỗi import: ' + error.message, 'error');
        }
    },

    async exportProxies() {
        try {
            await apiClient.exportProxies();
            utils.showToast('Đang tải file export...', 'info');
        } catch (error) {
            utils.showToast('Lỗi export: ' + error.message, 'error');
        }
    }
};

window.Proxies = Proxies;
