// Accounts Module for Bi Ads Multi Tool PRO v3.0

const Accounts = {
    data: {
        accounts: [],
        proxies: [],
        filteredAccounts: []
    },

    async init() {
        await this.loadData();
        this.render();
    },

    async loadData() {
        try {
            const [accounts, proxies] = await Promise.all([
                apiClient.getAccounts(),
                apiClient.getProxies()
            ]);
            this.data.accounts = accounts;
            this.data.proxies = proxies;
            this.data.filteredAccounts = accounts;
        } catch (error) {
            console.error('Failed to load accounts:', error);
            utils.showToast('Không thể tải danh sách tài khoản', 'error');
        }
    },

    render() {
        const content = document.getElementById('contentBody');
        const actions = document.getElementById('contentActions');
        
        if (!content) return;

        // Action buttons
        actions.innerHTML = components.createActionBar([
            { id: 'btnAddAccount', label: 'Thêm tài khoản', icon: '➕', class: 'btn-primary' },
            { id: 'btnImportAccounts', label: 'Import', icon: '📥', class: 'btn-success' },
            { id: 'btnExportAccounts', label: 'Export', icon: '📤', class: 'btn-secondary' },
            { id: 'btnRefreshAccounts', label: 'Làm mới', icon: '↻', class: 'btn-secondary' }
        ]);

        // Render accounts table
        content.innerHTML = `
            <!-- Filter -->
            ${components.createFilterForm([
                {
                    type: 'text',
                    name: 'search',
                    label: 'Tìm kiếm',
                    placeholder: 'UID, Username, Email...'
                },
                {
                    type: 'select',
                    name: 'status',
                    label: 'Trạng thái',
                    options: [
                        { value: '', label: 'Tất cả' },
                        { value: 'active', label: 'Active' },
                        { value: 'inactive', label: 'Inactive' },
                        { value: 'dead', label: 'Dead' }
                    ]
                },
                {
                    type: 'select',
                    name: 'hasProxy',
                    label: 'Proxy',
                    options: [
                        { value: '', label: 'Tất cả' },
                        { value: 'yes', label: 'Có proxy' },
                        { value: 'no', label: 'Không có proxy' }
                    ]
                }
            ])}

            <!-- Stats -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px;">
                <div style="background: rgba(46, 204, 113, 0.1); padding: 15px; border-radius: 8px; border-left: 3px solid #2ecc71;">
                    <div style="font-size: 24px; font-weight: bold; color: #2ecc71;">${this.data.accounts.length}</div>
                    <div style="font-size: 12px; color: #888;">Tổng tài khoản</div>
                </div>
                <div style="background: rgba(52, 152, 219, 0.1); padding: 15px; border-radius: 8px; border-left: 3px solid #3498db;">
                    <div style="font-size: 24px; font-weight: bold; color: #3498db;">${this.data.accounts.filter(a => a.status === 'active').length}</div>
                    <div style="font-size: 12px; color: #888;">Active</div>
                </div>
                <div style="background: rgba(243, 156, 18, 0.1); padding: 15px; border-radius: 8px; border-left: 3px solid #f39c12;">
                    <div style="font-size: 24px; font-weight: bold; color: #f39c12;">${this.data.accounts.filter(a => a.proxy_id).length}</div>
                    <div style="font-size: 12px; color: #888;">Có proxy</div>
                </div>
            </div>

            <!-- Accounts Table -->
            <div class="card">
                <div class="card-header">
                    👤 Danh sách tài khoản (${this.data.filteredAccounts.length})
                </div>
                <div class="card-body">
                    <div id="accountsTableContainer">
                        ${this.renderTable()}
                    </div>
                </div>
            </div>
        `;

        this.setupEventListeners();
    },

    renderTable() {
        const columns = [
            { field: 'id', label: 'ID' },
            { field: 'uid', label: 'UID' },
            { field: 'username', label: 'Username' },
            { field: 'name', label: 'Tên' },
            { field: 'email', label: 'Email' },
            { 
                field: 'status', 
                label: 'Trạng thái',
                render: (value) => utils.getStatusBadge(value, 'account')
            },
            {
                field: 'proxy_id',
                label: 'Proxy',
                render: (value, row) => {
                    if (value) {
                        const proxy = this.data.proxies.find(p => p.id === value);
                        return proxy ? `${proxy.ip}:${proxy.port}` : 'N/A';
                    }
                    return '<span style="color: #888;">Chưa gán</span>';
                }
            },
            {
                field: 'created_at',
                label: 'Ngày tạo',
                render: (value) => utils.formatDate(value)
            }
        ];

        const actions = [
            { name: 'edit', label: 'Sửa', icon: '✏️', class: 'btn-warning' },
            { name: 'assignProxy', label: 'Gán proxy', icon: '🌐', class: 'btn-info' },
            { name: 'delete', label: 'Xóa', icon: '🗑️', class: 'btn-danger' }
        ];

        return components.createTable(columns, this.data.filteredAccounts, actions);
    },

    setupEventListeners() {
        // Add account button
        document.getElementById('btnAddAccount')?.addEventListener('click', () => this.showAddModal());
        
        // Import button
        document.getElementById('btnImportAccounts')?.addEventListener('click', () => this.showImportModal());
        
        // Export button
        document.getElementById('btnExportAccounts')?.addEventListener('click', () => this.exportAccounts());
        
        // Refresh button
        document.getElementById('btnRefreshAccounts')?.addEventListener('click', () => {
            this.init();
            utils.showToast('Đã làm mới danh sách', 'success');
        });

        // Filter form
        document.getElementById('filterForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.applyFilter(new FormData(e.target));
        });

        document.getElementById('btnResetFilter')?.addEventListener('click', () => {
            document.getElementById('filterForm')?.reset();
            this.data.filteredAccounts = this.data.accounts;
            document.getElementById('accountsTableContainer').innerHTML = this.renderTable();
            this.setupTableActions();
        });

        // Table actions
        this.setupTableActions();
    },

    setupTableActions() {
        document.querySelectorAll('[data-action="edit"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = parseInt(btn.dataset.id);
                this.showEditModal(id);
            });
        });

        document.querySelectorAll('[data-action="assignProxy"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = parseInt(btn.dataset.id);
                this.showAssignProxyModal(id);
            });
        });

        document.querySelectorAll('[data-action="delete"]').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = parseInt(btn.dataset.id);
                if (await utils.confirm('Bạn có chắc chắn muốn xóa tài khoản này?', 'Xác nhận xóa')) {
                    await this.deleteAccount(id);
                }
            });
        });
    },

    applyFilter(formData) {
        const search = formData.get('search')?.toLowerCase() || '';
        const status = formData.get('status') || '';
        const hasProxy = formData.get('hasProxy') || '';

        this.data.filteredAccounts = this.data.accounts.filter(account => {
            // Search filter
            if (search) {
                const searchMatch = 
                    account.uid?.toLowerCase().includes(search) ||
                    account.username?.toLowerCase().includes(search) ||
                    account.email?.toLowerCase().includes(search) ||
                    account.name?.toLowerCase().includes(search);
                if (!searchMatch) return false;
            }

            // Status filter
            if (status && account.status !== status) return false;

            // Proxy filter
            if (hasProxy === 'yes' && !account.proxy_id) return false;
            if (hasProxy === 'no' && account.proxy_id) return false;

            return true;
        });

        document.getElementById('accountsTableContainer').innerHTML = this.renderTable();
        this.setupTableActions();
    },

    showAddModal() {
        const bodyHtml = `
            <form id="accountForm">
                ${components.createFormField({ type: 'text', name: 'uid', label: 'UID', required: true })}
                ${components.createFormField({ type: 'text', name: 'username', label: 'Username', required: true })}
                ${components.createFormField({ type: 'text', name: 'name', label: 'Tên hiển thị', required: true })}
                ${components.createFormField({ type: 'email', name: 'email', label: 'Email' })}
                ${components.createFormField({ 
                    type: 'select', 
                    name: 'status', 
                    label: 'Trạng thái',
                    options: [
                        { value: 'active', label: 'Active' },
                        { value: 'inactive', label: 'Inactive' },
                        { value: 'dead', label: 'Dead' }
                    ]
                })}
                ${components.createFormField({ 
                    type: 'select', 
                    name: 'method', 
                    label: 'Phương thức đăng nhập',
                    options: [
                        { value: 'cookies', label: 'Cookies' },
                        { value: 'token', label: 'Token' }
                    ]
                })}
                ${components.createFormField({ type: 'textarea', name: 'cookies', label: 'Cookies/Token' })}
            </form>
        `;

        const modal = components.createModal('➕ Thêm tài khoản mới', bodyHtml, [
            { text: 'Hủy', class: 'btn-secondary', onClick: () => modal.close() },
            { 
                text: 'Thêm', 
                class: 'btn-primary', 
                onClick: async () => {
                    await this.saveAccount();
                    modal.close();
                }
            }
        ]);
    },

    showEditModal(id) {
        const account = this.data.accounts.find(a => a.id === id);
        if (!account) return;

        const bodyHtml = `
            <form id="accountForm">
                <input type="hidden" name="id" value="${account.id}">
                ${components.createFormField({ type: 'text', name: 'uid', label: 'UID', value: account.uid, required: true })}
                ${components.createFormField({ type: 'text', name: 'username', label: 'Username', value: account.username, required: true })}
                ${components.createFormField({ type: 'text', name: 'name', label: 'Tên hiển thị', value: account.name, required: true })}
                ${components.createFormField({ type: 'email', name: 'email', label: 'Email', value: account.email })}
                ${components.createFormField({ 
                    type: 'select', 
                    name: 'status', 
                    label: 'Trạng thái',
                    value: account.status,
                    options: [
                        { value: 'active', label: 'Active' },
                        { value: 'inactive', label: 'Inactive' },
                        { value: 'dead', label: 'Dead' }
                    ]
                })}
            </form>
        `;

        const modal = components.createModal('✏️ Chỉnh sửa tài khoản', bodyHtml, [
            { text: 'Hủy', class: 'btn-secondary', onClick: () => modal.close() },
            { 
                text: 'Lưu', 
                class: 'btn-primary', 
                onClick: async () => {
                    await this.saveAccount(id);
                    modal.close();
                }
            }
        ]);
    },

    showAssignProxyModal(accountId) {
        const account = this.data.accounts.find(a => a.id === accountId);
        if (!account) return;

        const proxyOptions = [
            { value: '', label: '-- Chọn proxy --' },
            ...this.data.proxies.filter(p => p.status === 'active').map(p => ({
                value: p.id,
                label: `${p.ip}:${p.port} (${p.protocol})`
            }))
        ];

        const bodyHtml = `
            <form id="assignProxyForm">
                <p style="color: #888; margin-bottom: 15px;">Tài khoản: <strong>${account.username}</strong></p>
                ${components.createFormField({ 
                    type: 'select', 
                    name: 'proxy_id', 
                    label: 'Chọn proxy',
                    value: account.proxy_id || '',
                    options: proxyOptions
                })}
                ${account.proxy_id ? '<button type="button" id="btnRemoveProxy" class="btn btn-danger btn-small">🗑️ Gỡ proxy hiện tại</button>' : ''}
            </form>
        `;

        const modal = components.createModal('🌐 Gán proxy cho tài khoản', bodyHtml, [
            { text: 'Hủy', class: 'btn-secondary', onClick: () => modal.close() },
            { 
                text: 'Gán proxy', 
                class: 'btn-primary', 
                onClick: async () => {
                    const form = document.getElementById('assignProxyForm');
                    const formData = new FormData(form);
                    const proxyId = parseInt(formData.get('proxy_id'));
                    
                    if (proxyId) {
                        await this.assignProxy(accountId, proxyId);
                    }
                    modal.close();
                }
            }
        ]);

        // Remove proxy button
        document.getElementById('btnRemoveProxy')?.addEventListener('click', async () => {
            if (await utils.confirm('Bạn có chắc chắn muốn gỡ proxy khỏi tài khoản này?')) {
                await this.removeProxy(accountId);
                modal.close();
            }
        });
    },

    showImportModal() {
        const bodyHtml = `
            <div>
                <p style="color: #888; margin-bottom: 15px;">Chọn file CSV hoặc TXT để import tài khoản</p>
                <input type="file" id="importFile" accept=".csv,.txt" class="form-input">
                <p style="color: #888; font-size: 12px; margin-top: 10px;">
                    Format: uid,username,name,email,status,method,cookies
                </p>
            </div>
        `;

        const modal = components.createModal('📥 Import tài khoản', bodyHtml, [
            { text: 'Hủy', class: 'btn-secondary', onClick: () => modal.close() },
            { 
                text: 'Import', 
                class: 'btn-primary', 
                onClick: async () => {
                    await this.importAccounts();
                    modal.close();
                }
            }
        ]);
    },

    async saveAccount(id = null) {
        const form = document.getElementById('accountForm');
        const formData = new FormData(form);
        
        const accountData = {
            uid: formData.get('uid'),
            username: formData.get('username'),
            name: formData.get('name'),
            email: formData.get('email'),
            status: formData.get('status'),
            method: formData.get('method') || 'cookies',
            cookies: formData.get('cookies') || ''
        };

        try {
            if (id) {
                await apiClient.updateAccount(id, accountData);
                utils.showToast('Đã cập nhật tài khoản', 'success');
            } else {
                await apiClient.createAccount(accountData);
                utils.showToast('Đã thêm tài khoản mới', 'success');
            }
            await this.init();
        } catch (error) {
            utils.showToast('Lỗi: ' + error.message, 'error');
        }
    },

    async deleteAccount(id) {
        try {
            await apiClient.deleteAccount(id);
            utils.showToast('Đã xóa tài khoản', 'success');
            await this.init();
        } catch (error) {
            utils.showToast('Lỗi: ' + error.message, 'error');
        }
    },

    async assignProxy(accountId, proxyId) {
        try {
            await apiClient.assignProxy(accountId, proxyId);
            utils.showToast('Đã gán proxy cho tài khoản', 'success');
            await this.init();
        } catch (error) {
            utils.showToast('Lỗi: ' + error.message, 'error');
        }
    },

    async removeProxy(accountId) {
        try {
            await apiClient.removeProxy(accountId);
            utils.showToast('Đã gỡ proxy khỏi tài khoản', 'success');
            await this.init();
        } catch (error) {
            utils.showToast('Lỗi: ' + error.message, 'error');
        }
    },

    async importAccounts() {
        const fileInput = document.getElementById('importFile');
        const file = fileInput?.files[0];
        
        if (!file) {
            utils.showToast('Vui lòng chọn file', 'warning');
            return;
        }

        try {
            await apiClient.importAccounts(file);
            utils.showToast('Đã import tài khoản thành công', 'success');
            await this.init();
        } catch (error) {
            utils.showToast('Lỗi import: ' + error.message, 'error');
        }
    },

    async exportAccounts() {
        try {
            await apiClient.exportAccounts();
            utils.showToast('Đang tải file export...', 'info');
        } catch (error) {
            utils.showToast('Lỗi export: ' + error.message, 'error');
        }
    }
};

// Make Accounts available globally
window.Accounts = Accounts;
