// Bi Ads - Multi Tool PRO v3.0 - Main Application Logic
// Author: Bi Ads Team
// Version: 3.0.0

const BiAds = {
    currentTask: null,
    currentPage: 'accounts',
    accounts: [],
    currentAccount: null,
    taskRunning: false,
    toastQueue: [],
    
    // Initialize
    init: function() {
        console.log('🚀 Bi Ads Multi Tool PRO v3.0 initialized');
        
        // Load saved data
        this.loadData();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Check backend connection
        this.checkBackend();
        
        // Load default content
        this.loadWelcomeScreen();
        
        // Show welcome toast
        setTimeout(() => {
            this.showToast('success', 'Hệ thống khởi động thành công', 'Chào mừng đến với Bi Ads Multi Tool PRO v3.0! 🚀');
        }, 500);
    },

    // Load saved data from localStorage
    loadData: function() {
        try {
            const savedAccounts = localStorage.getItem('bi_ads_accounts');
            if (savedAccounts) {
                this.accounts = JSON.parse(savedAccounts);
            }
            
            const savedCurrentAccount = localStorage.getItem('bi_ads_current_account');
            if (savedCurrentAccount) {
                this.currentAccount = JSON.parse(savedCurrentAccount);
            }
        } catch (error) {
            console.error('Error loading data:', error);
        }
    },

    // Save data to localStorage
    saveData: function() {
        try {
            localStorage.setItem('bi_ads_accounts', JSON.stringify(this.accounts));
            if (this.currentAccount) {
                localStorage.setItem('bi_ads_current_account', JSON.stringify(this.currentAccount));
            }
        } catch (error) {
            console.error('Error saving data:', error);
        }
    },

    // Setup event listeners
    setupEventListeners: function() {
        // Top nav page buttons
        document.querySelectorAll('.top-nav-item').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const page = btn.getAttribute('data-page');
                this.loadPage(page);
                
                // Update active state
                document.querySelectorAll('.top-nav-item').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
        
        // Special handling for Settings, Plugins, Help pages
        const settingsBtn = document.querySelector('[data-page="settings"]');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.loadSettingsPage());
        }

        // Task items
        document.querySelectorAll('.task-item').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const task = btn.getAttribute('data-task');
                this.loadTask(task);
                
                // Update active state
                document.querySelectorAll('.task-item').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        // Start/Stop task buttons
        document.getElementById('btnStartTask')?.addEventListener('click', () => this.startTask());
        document.getElementById('btnStopTask')?.addEventListener('click', () => this.stopTask());
    },

    // Check backend connection
    checkBackend: async function() {
        const loadingToast = this.showLoading('Đang kết nối...', 'Kiểm tra kết nối backend');
        
        try {
            const response = await fetch('http://localhost:8000/health');
            const data = await response.json();
            
            this.hideToast(loadingToast);
            
            if (data.status === 'healthy') {
                this.updateBackendStatus(true);
                this.log('success', 'Đã kết nối backend thành công');
                this.showToast('success', 'Backend đã kết nối', `Version: ${data.version || 'N/A'}`);
            }
        } catch (error) {
            this.hideToast(loadingToast);
            this.updateBackendStatus(false);
            this.log('error', 'Không thể kết nối backend. Vui lòng chạy: npm run backend');
            this.showToast('error', 'Backend không kết nối được', 'Vui lòng khởi động backend trước khi sử dụng');
        }
    },

    // Update backend status indicator
    updateBackendStatus: function(connected) {
        const statusEl = document.getElementById('backendStatus');
        if (statusEl) {
            statusEl.className = 'backend-status ' + (connected ? 'online' : 'offline');
            statusEl.querySelector('.status-text').textContent = connected ? 'Backend Online' : 'Backend Offline';
        }
    },

    // Load welcome screen
    loadWelcomeScreen: function() {
        const content = document.getElementById('contentBody');
        const title = document.getElementById('contentTitle');
        
        title.textContent = 'Chào mừng đến Bi Ads Multi Tool PRO v2.0';
        
        content.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${this.accounts.length}</div>
                    <div class="stat-label">Tài khoản</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">0</div>
                    <div class="stat-label">Tác vụ đang chạy</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">0</div>
                    <div class="stat-label">Tác vụ hoàn thành</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">2.0</div>
                    <div class="stat-label">Phiên bản</div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">📌 Hướng dẫn sử dụng nhanh</div>
                <div class="card-body">
                    <ol style="line-height: 2; color: #b0b0b0; padding-left: 20px;">
                        <li>Chọn tác vụ từ menu bên trái</li>
                        <li>Điền thông tin cần thiết vào form</li>
                        <li>Nhấn "▶️ Bắt đầu tác vụ" để chạy</li>
                        <li>Theo dõi tiến trình ở phần "Nhật ký hoạt động"</li>
                        <li>Nhấn "⏸️ Dừng tác vụ" khi cần dừng</li>
                    </ol>
                </div>
            </div>

            <div class="card">
                <div class="card-header">🚀 Tính năng nổi bật v2.0</div>
                <div class="card-body">
                    <div class="grid-2">
                        <div style="padding: 15px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <h4 style="color: #667eea; margin-bottom: 10px;">🏢 Tác vụ Group</h4>
                            <p style="font-size: 13px; color: #888;">Quét, tham gia, rời nhóm, mời bạn bè</p>
                        </div>
                        <div style="padding: 15px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <h4 style="color: #667eea; margin-bottom: 10px;">💬 Tương tác tài khoản</h4>
                            <p style="font-size: 13px; color: #888;">Đăng bài, comment, like, chia sẻ</p>
                        </div>
                        <div style="padding: 15px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <h4 style="color: #667eea; margin-bottom: 10px;">👥 Tác vụ bạn bè</h4>
                            <p style="font-size: 13px; color: #888;">Kết bạn, hủy kết bạn, gửi tin nhắn</p>
                        </div>
                        <div style="padding: 15px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <h4 style="color: #667eea; margin-bottom: 10px;">📄 Tác vụ Fanpage</h4>
                            <p style="font-size: 13px; color: #888;">Quản lý, đăng bài, tương tác fanpage</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // Load page content
    loadPage: function(page) {
        this.currentPage = page;
        const content = document.getElementById('contentBody');
        const title = document.getElementById('contentTitle');
        
        switch(page) {
            case 'dashboard':
                title.textContent = '📊 Dashboard - Tổng quan hệ thống';
                Dashboard.render(content);
                Dashboard.init();
                break;
            case 'accounts':
                title.textContent = '👤 Quản lý tài khoản';
                this.renderAccountsPage(content);
                break;
            case 'proxy':
                title.textContent = '🌐 Quản lý proxy';
                this.renderProxyPage(content);
                break;
            case 'sub-accounts':
                title.textContent = '👥 Quản lý tài khoản phụ';
                this.renderSubAccountsPage(content);
                break;
            case 'ids':
                title.textContent = '🆔 Quản lý ID';
                this.renderIDsPage(content);
                break;
            case 'ips':
                title.textContent = '📡 Quản lý IP thiết bị';
                this.renderIPsPage(content);
                break;
            case 'whitelist':
                title.textContent = '✅ Quản lý tài khoản whitelist';
                this.renderWhitelistPage(content);
                break;
            case 'posts':
                title.textContent = '📝 Quản lý bài viết đã đăng';
                this.renderPostsPage(content);
                break;
            case 'messages':
                title.textContent = '💬 Quản lý tin nhắn';
                this.renderMessagesPage(content);
                break;
            case 'settings':
                title.textContent = '⚙️ Cài đặt hệ thống';
                this.renderSettingsPage(content);
                break;
            default:
                this.loadWelcomeScreen();
        }
    },

    // Render Accounts Page
    renderAccountsPage: function(content) {
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    📋 Quản lý tài khoản (${this.accounts.length})
                    <div style="float: right;">
                        <button class="btn-success" style="margin-right: 10px;" onclick="BiAds.checkAllAccountsStatus()" title="Kiểm tra tất cả tài khoản">
                            🔄 Check All
                        </button>
                        <button class="btn-primary" style="margin-right: 10px;" onclick="BiAds.loadAccountsFromBackend()" title="Tải lại danh sách">
                            🔄 Tải lại
                        </button>
                        <button class="btn-primary" style="margin-right: 10px;" onclick="FileImport.showImportAccountsModal()">
                            📥 Import
                        </button>
                        <button class="btn-primary" onclick="BiAds.showAddAccountModal()">
                            ➕ Thêm
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div id="accountsTableContainer">
                        ${this.accounts.length === 0 ? `
                            <div style="text-align: center; padding: 40px; color: #888;">
                                <div class="spinner" style="margin: 0 auto 20px;"></div>
                                <h3>Đang tải danh sách tài khoản...</h3>
                                <p>Vui lòng đợi trong giây lát</p>
                            </div>
                        ` : `
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>STT</th>
                                        <th>UID</th>
                                        <th>Tên</th>
                                        <th>Email</th>
                                        <th>Proxy</th>
                                        <th>Trạng thái</th>
                                        <th>Hành động</th>
                                    </tr>
                                </thead>
                                <tbody id="accountsTableBody">
                                    ${this.accounts.map((acc, index) => {
                                        const statusClass = acc.status === 'active' ? 'success' : 
                                                          acc.status === 'dead' ? 'danger' : 
                                                          acc.status === 'checkpoint' ? 'warning' : 'secondary';
                                        return `
                                            <tr class="fade-in">
                                                <td>${index + 1}</td>
                                                <td><code>${acc.uid}</code></td>
                                                <td>${acc.name || 'N/A'}</td>
                                                <td>${acc.email || 'N/A'}</td>
                                                <td>${acc.proxy_id ? `Proxy #${acc.proxy_id}` : '❌ Chưa có'}</td>
                                                <td><span class="badge badge-${statusClass}">${acc.status.toUpperCase()}</span></td>
                                                <td>
                                                    <button class="btn-info" style="padding: 5px 10px; font-size: 12px; margin: 2px;" 
                                                            onclick="BiAds.checkAccountStatus(${acc.id})" title="Kiểm tra live/die">
                                                        🔍 Check
                                                    </button>
                                                    <button class="btn-primary" style="padding: 5px 10px; font-size: 12px; margin: 2px;" 
                                                            onclick="BiAds.showAssignProxyModal(${acc.id})" title="Gán proxy">
                                                        🌐 Proxy
                                                    </button>
                                                    <button class="btn-success" style="padding: 5px 10px; font-size: 12px; margin: 2px;" 
                                                            onclick="BiAds.useAccountById(${acc.id})">
                                                        ✅ Dùng
                                                    </button>
                                                    <button class="btn-danger" style="padding: 5px 10px; font-size: 12px; margin: 2px;"
                                                            onclick="BiAds.deleteAccountById(${acc.id})">
                                                        🗑️ Xóa
                                                    </button>
                                                </td>
                                            </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        `}
                    </div>
                </div>
            </div>

            ${this.currentAccount ? `
                <div class="card">
                    <div class="card-header">✅ Tài khoản đang sử dụng</div>
                    <div class="card-body">
                        <div class="grid-2">
                            <div>
                                <strong>UID:</strong> <code>${this.currentAccount.uid}</code>
                            </div>
                            <div>
                                <strong>Tên:</strong> ${this.currentAccount.name || 'N/A'}
                            </div>
                            <div>
                                <strong>Email:</strong> ${this.currentAccount.email || 'N/A'}
                            </div>
                            <div>
                                <strong>Trạng thái:</strong> <span class="badge badge-success">${this.currentAccount.status}</span>
                            </div>
                        </div>
                    </div>
                </div>
            ` : ''}
        `;
        
        // Auto-load accounts from backend
        setTimeout(() => {
            this.loadAccountsFromBackend();
        }, 100);
    },

    // Load accounts from backend
    loadAccountsFromBackend: async function() {
        try {
            this.log('info', '🔄 Đang tải danh sách tài khoản từ backend...');
            
            const accounts = await apiClient.getAccounts();
            this.accounts = accounts;
            
            this.log('success', `✅ Đã tải ${accounts.length} tài khoản thành công`);
            
            // Re-render the table
            const tbody = document.getElementById('accountsTableBody');
            if (tbody) {
                tbody.innerHTML = this.accounts.map((acc, index) => {
                    const statusClass = acc.status === 'active' ? 'success' : 
                                      acc.status === 'dead' ? 'danger' : 
                                      acc.status === 'checkpoint' ? 'warning' : 'secondary';
                    return `
                        <tr class="fade-in">
                            <td>${index + 1}</td>
                            <td><code>${acc.uid}</code></td>
                            <td>${acc.name || 'N/A'}</td>
                            <td>${acc.email || 'N/A'}</td>
                            <td>${acc.proxy_id ? `Proxy #${acc.proxy_id}` : '❌ Chưa có'}</td>
                            <td><span class="badge badge-${statusClass}">${acc.status.toUpperCase()}</span></td>
                            <td>
                                <button class="btn-info" style="padding: 5px 10px; font-size: 12px; margin: 2px;" 
                                        onclick="BiAds.checkAccountStatus(${acc.id})" title="Kiểm tra live/die">
                                    🔍 Check
                                </button>
                                <button class="btn-primary" style="padding: 5px 10px; font-size: 12px; margin: 2px;" 
                                        onclick="BiAds.showAssignProxyModal(${acc.id})" title="Gán proxy">
                                    🌐 Proxy
                                </button>
                                <button class="btn-success" style="padding: 5px 10px; font-size: 12px; margin: 2px;" 
                                        onclick="BiAds.useAccountById(${acc.id})">
                                    ✅ Dùng
                                </button>
                                <button class="btn-danger" style="padding: 5px 10px; font-size: 12px; margin: 2px;"
                                        onclick="BiAds.deleteAccountById(${acc.id})">
                                    🗑️ Xóa
                                </button>
                            </td>
                        </tr>
                    `;
                }).join('');
            }
            
            // Update header count
            const header = document.querySelector('.card-header');
            if (header) {
                header.childNodes[0].textContent = `📋 Quản lý tài khoản (${accounts.length})`;
            }
            
        } catch (error) {
            this.log('error', `❌ Lỗi tải tài khoản: ${error.message}`);
            
            const container = document.getElementById('accountsTableContainer');
            if (container) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #ff4444;">
                        <h3>❌ Không thể tải danh sách tài khoản</h3>
                        <p>${error.message}</p>
                        <button class="btn-primary" onclick="BiAds.loadAccountsFromBackend()">
                            🔄 Thử lại
                        </button>
                    </div>
                `;
            }
        }
    },

    // Check account status (live/die)
    checkAccountStatus: async function(accountId) {
        try {
            this.log('info', `🔍 Đang kiểm tra tài khoản ID ${accountId}...`);
            
            const result = await apiClient.checkAccountStatus(accountId);
            
            const status = result.is_live ? '✅ LIVE' : '❌ DIE';
            this.log('success', `${status} - ${result.reason}`);
            
            // Reload accounts to show updated status
            await this.loadAccountsFromBackend();
            
        } catch (error) {
            this.log('error', `❌ Lỗi kiểm tra: ${error.message}`);
        }
    },

    // Check all accounts status
    checkAllAccountsStatus: async function() {
        if (!confirm('Kiểm tra tất cả tài khoản? Quá trình này có thể mất vài phút.')) {
            return;
        }
        
        try {
            this.log('info', '🔄 Đang kiểm tra tất cả tài khoản...');
            
            const result = await apiClient.checkAccountsStatusBulk();
            
            this.log('success', `✅ Hoàn thành: ${result.live_count} live, ${result.die_count} die`);
            
            // Reload accounts
            await this.loadAccountsFromBackend();
            
        } catch (error) {
            this.log('error', `❌ Lỗi: ${error.message}`);
        }
    },

    // Show assign proxy modal
    showAssignProxyModal: async function(accountId) {
        try {
            // Load proxies from backend
            const proxies = await apiClient.getProxies();
            
            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.id = 'assignProxyModal';
            
            modal.innerHTML = `
                <div class="modal">
                    <div class="modal-header">
                        <div class="modal-title">🌐 Gán proxy cho tài khoản</div>
                        <button class="modal-close" onclick="document.getElementById('assignProxyModal').remove()">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="input-group">
                            <label>Chọn proxy:</label>
                            <select id="proxySelect" class="input">
                                <option value="">❌ Không dùng proxy</option>
                                ${proxies.map(proxy => `
                                    <option value="${proxy.id}">
                                        ${proxy.ip}:${proxy.port} (${proxy.protocol.toUpperCase()}) - ${proxy.status}
                                    </option>
                                `).join('')}
                            </select>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-secondary" onclick="document.getElementById('assignProxyModal').remove()">Hủy</button>
                        <button class="btn-primary" onclick="BiAds.assignProxy(${accountId})">
                            💾 Gán proxy
                        </button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
        } catch (error) {
            alert(`Lỗi: ${error.message}`);
        }
    },

    // Assign proxy to account
    assignProxy: async function(accountId) {
        try {
            const select = document.getElementById('proxySelect');
            const proxyId = select.value ? parseInt(select.value) : null;
            
            this.log('info', `🌐 Đang gán proxy cho tài khoản ID ${accountId}...`);
            
            const result = await apiClient.assignProxyToAccount(accountId, proxyId);
            
            const proxyText = proxyId ? `Proxy #${proxyId}` : 'Không dùng proxy';
            this.log('success', `✅ Đã gán ${proxyText} thành công`);
            
            // Close modal
            const modal = document.getElementById('assignProxyModal');
            if (modal) {
                modal.remove();
            }
            
            // Reload accounts to show updated proxy
            await this.loadAccountsFromBackend();
            
        } catch (error) {
            this.log('error', `❌ Lỗi: ${error.message}`);
        }
    },

    // Use account by ID
    useAccountById: async function(accountId) {
        try {
            const account = await apiClient.getAccountById(accountId);
            this.currentAccount = account;
            this.saveData();
            this.log('success', `✅ Đang sử dụng tài khoản: ${account.name || account.uid}`);
            
            // Re-render page
            this.loadPage('accounts');
        } catch (error) {
            this.log('error', `❌ Lỗi: ${error.message}`);
        }
    },

    // Delete account by ID
    deleteAccountById: async function(accountId) {
        if (!confirm('Bạn có chắc muốn xóa tài khoản này?')) {
            return;
        }
        
        try {
            await apiClient.deleteAccount(accountId);
            this.log('success', '✅ Đã xóa tài khoản');
            
            // Reload accounts
            await this.loadAccountsFromBackend();
        } catch (error) {
            this.log('error', `❌ Lỗi: ${error.message}`);
        }
    },

    // Show Add Account Modal
    showAddAccountModal: function() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.id = 'addAccountModal';
        
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <div class="modal-title">➕ Thêm tài khoản Facebook</div>
                    <button class="modal-close" onclick="document.getElementById('addAccountModal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="input-group">
                        <label>Phương thức đăng nhập:</label>
                        <select id="loginMethod" class="input" onchange="BiAds.switchLoginMethod()">
                            <option value="cookies">🍪 Cookies (Khuyến nghị)</option>
                            <option value="email">📧 Email & Password</option>
                            <option value="token">🔑 Access Token</option>
                        </select>
                    </div>

                    <div id="cookiesForm">
                        <div class="input-group">
                            <label>Tên tài khoản:</label>
                            <input type="text" id="accName" class="input" placeholder="Tài khoản chính">
                        </div>
                        <div class="input-group">
                            <label>Cookies (JSON):</label>
                            <textarea id="accCookies" class="input" rows="6" placeholder='[{"name": "c_user", "value": "123..."}, {"name": "xs", "value": "xxx"}]'></textarea>
                        </div>
                        <div class="input-group">
                            <label>Proxy (optional):</label>
                            <input type="text" id="accProxy" class="input" placeholder="http://user:pass@host:port">
                        </div>
                    </div>

                    <div id="emailForm" class="hidden">
                        <div class="input-group">
                            <label>Tên tài khoản:</label>
                            <input type="text" id="accNameEmail" class="input" placeholder="Tài khoản chính">
                        </div>
                        <div class="input-group">
                            <label>Email/Phone:</label>
                            <input type="text" id="accEmail" class="input" placeholder="email@example.com">
                        </div>
                        <div class="input-group">
                            <label>Password:</label>
                            <input type="password" id="accPassword" class="input">
                        </div>
                        <div class="input-group">
                            <label>Proxy (optional):</label>
                            <input type="text" id="accProxyEmail" class="input" placeholder="http://user:pass@host:port">
                        </div>
                    </div>

                    <div id="tokenForm" class="hidden">
                        <div class="input-group">
                            <label>Tên tài khoản:</label>
                            <input type="text" id="accNameToken" class="input" placeholder="Tài khoản chính">
                        </div>
                        <div class="input-group">
                            <label>Access Token:</label>
                            <textarea id="accToken" class="input" rows="4" placeholder="EAAB..."></textarea>
                        </div>
                        <div class="input-group">
                            <label>Proxy (optional):</label>
                            <input type="text" id="accProxyToken" class="input" placeholder="http://user:pass@host:port">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="document.getElementById('addAccountModal').remove()">Hủy</button>
                    <button class="btn-primary" onclick="BiAds.submitAddAccount()">Thêm tài khoản</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    },

    // Switch login method
    switchLoginMethod: function() {
        const method = document.getElementById('loginMethod').value;
        
        document.getElementById('cookiesForm').classList.add('hidden');
        document.getElementById('emailForm').classList.add('hidden');
        document.getElementById('tokenForm').classList.add('hidden');
        
        if (method === 'cookies') {
            document.getElementById('cookiesForm').classList.remove('hidden');
        } else if (method === 'email') {
            document.getElementById('emailForm').classList.remove('hidden');
        } else if (method === 'token') {
            document.getElementById('tokenForm').classList.remove('hidden');
        }
    },

    // Submit add account
    submitAddAccount: function() {
        const method = document.getElementById('loginMethod').value;
        let account = {};
        
        try {
            if (method === 'cookies') {
                account = {
                    id: Date.now(),
                    name: document.getElementById('accName').value,
                    cookies: JSON.parse(document.getElementById('accCookies').value),
                    proxy: document.getElementById('accProxy').value,
                    method: 'cookies',
                    status: 'active',
                    createdAt: new Date().toISOString()
                };
            } else if (method === 'email') {
                account = {
                    id: Date.now(),
                    name: document.getElementById('accNameEmail').value,
                    email: document.getElementById('accEmail').value,
                    password: document.getElementById('accPassword').value,
                    proxy: document.getElementById('accProxyEmail').value,
                    method: 'email',
                    status: 'active',
                    createdAt: new Date().toISOString()
                };
            } else if (method === 'token') {
                account = {
                    id: Date.now(),
                    name: document.getElementById('accNameToken').value,
                    token: document.getElementById('accToken').value,
                    proxy: document.getElementById('accProxyToken').value,
                    method: 'token',
                    status: 'active',
                    createdAt: new Date().toISOString()
                };
            }
            
            if (!account.name) {
                throw new Error('Vui lòng nhập tên tài khoản');
            }
            
            this.accounts.push(account);
            this.saveData();
            
            document.getElementById('addAccountModal').remove();
            this.log('success', `Đã thêm tài khoản: ${account.name}`);
            this.loadPage('accounts');
            
        } catch (error) {
            alert('Lỗi: ' + error.message);
        }
    },

    // Use account
    useAccount: function(index) {
        this.currentAccount = this.accounts[index];
        this.saveData();
        this.log('success', `Đang sử dụng tài khoản: ${this.currentAccount.name}`);
        this.loadPage('accounts');
    },

    // Delete account
    deleteAccount: function(index) {
        if (confirm('Bạn có chắc muốn xóa tài khoản này?')) {
            const account = this.accounts[index];
            this.accounts.splice(index, 1);
            this.saveData();
            this.log('warning', `Đã xóa tài khoản: ${account.name}`);
            this.loadPage('accounts');
        }
    },

    // Render other pages (simplified for now)
    renderProxyPage: function(content) {
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    🌐 Quản lý Proxy
                    <button class="btn-primary" style="float: right;" onclick="FileImport.showImportProxiesModal()">
                        📥 Import proxy từ file
                    </button>
                </div>
                <div class="card-body">
                    <p>Chức năng quản lý proxy.</p>
                    <p>Nhấn nút <strong>"📥 Import proxy từ file"</strong> để nhập danh sách proxy từ file proxy.txt</p>
                    <div style="margin-top: 20px;">
                        <button class="btn-success" onclick="BiAds.loadProxiesFromBackend()">
                            🔄 Tải danh sách proxy
                        </button>
                        <button class="btn-primary" onclick="BiAds.autoAssignProxies()">
                            🎯 Tự động gán proxy
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    renderSubAccountsPage: function(content) {
        // Delegate to AdvancedFeatures module
        if (window.AdvancedFeatures && window.AdvancedFeatures.renderSubAccountsPage) {
            window.AdvancedFeatures.renderSubAccountsPage(content);
        } else {
            content.innerHTML = `
                <div class="card">
                    <div class="card-header">👥 Quản lý tài khoản phụ</div>
                    <div class="card-body">
                        <p>Đang tải module quản lý tài khoản phụ...</p>
                    </div>
                </div>
            `;
        }
    },

    renderIDsPage: function(content) {
        // Delegate to AdvancedFeatures module
        if (window.AdvancedFeatures && window.AdvancedFeatures.renderIDsPage) {
            window.AdvancedFeatures.renderIDsPage(content);
        } else {
            content.innerHTML = `
                <div class="card">
                    <div class="card-header">🆔 Quản lý ID</div>
                    <div class="card-body">
                        <p>Đang tải module quản lý ID...</p>
                    </div>
                </div>
            `;
        }
    },

    renderIPsPage: function(content) {
        // Delegate to AdvancedFeatures module
        if (window.AdvancedFeatures && window.AdvancedFeatures.renderIPsPage) {
            window.AdvancedFeatures.renderIPsPage(content);
        } else {
            content.innerHTML = `
                <div class="card">
                    <div class="card-header">📡 Quản lý IP thiết bị</div>
                    <div class="card-body">
                        <p>Đang tải module quản lý IP...</p>
                    </div>
                </div>
            `;
        }
    },

    renderWhitelistPage: function(content) {
        // Delegate to AdvancedFeatures module
        if (window.AdvancedFeatures && window.AdvancedFeatures.renderWhitelistPage) {
            window.AdvancedFeatures.renderWhitelistPage(content);
        } else {
            content.innerHTML = `
                <div class="card">
                    <div class="card-header">✅ Quản lý tài khoản whitelist</div>
                    <div class="card-body">
                        <p>Đang tải module quản lý whitelist...</p>
                    </div>
                </div>
            `;
        }
    },

    renderPostsPage: function(content) {
        // Delegate to AdvancedFeatures module
        if (window.AdvancedFeatures && window.AdvancedFeatures.renderPostsPage) {
            window.AdvancedFeatures.renderPostsPage(content);
        } else {
            content.innerHTML = `
                <div class="card">
                    <div class="card-header">📝 Quản lý bài viết đã đăng</div>
                    <div class="card-body">
                        <p>Đang tải module quản lý bài viết...</p>
                    </div>
                </div>
            `;
        }
    },

    renderMessagesPage: function(content) {
        // Delegate to AdvancedFeatures module
        if (window.AdvancedFeatures && window.AdvancedFeatures.renderMessagesPage) {
            window.AdvancedFeatures.renderMessagesPage(content);
        } else {
            content.innerHTML = `
                <div class="card">
                    <div class="card-header">💬 Quản lý tin nhắn</div>
                    <div class="card-body">
                        <p>Đang tải module quản lý tin nhắn...</p>
                    </div>
                </div>
            `;
        }
    },

    renderSettingsPage: function(content) {
        content.innerHTML = `
            <div class="card">
                <div class="card-header">⚙️ Cài đặt hệ thống</div>
                <div class="card-body">
                    <div class="input-group">
                        <label>
                            <input type="checkbox" checked> Tự động lưu log
                        </label>
                    </div>
                    <div class="input-group">
                        <label>
                            <input type="checkbox" checked> Hiển thị thông báo
                        </label>
                    </div>
                    <div class="input-group">
                        <label>
                            <input type="checkbox"> Chế độ tối (Luôn bật)
                        </label>
                    </div>
                    <button class="btn-primary" style="margin-top: 20px;">💾 Lưu cài đặt</button>
                </div>
            </div>

            <div class="card">
                <div class="card-header">ℹ️ Thông tin ứng dụng</div>
                <div class="card-body">
                    <p><strong>Tên:</strong> Bi Ads Multi Tool PRO</p>
                    <p><strong>Phiên bản:</strong> 2.0.0</p>
                    <p><strong>Nhà phát triển:</strong> Bi Ads Team</p>
                    <p><strong>License:</strong> MIT</p>
                </div>
            </div>
        `;
    },

    // Load task content
    loadTask: function(task) {
        this.currentTask = task;
        const content = document.getElementById('contentBody');
        const title = document.getElementById('contentTitle');
        
        // Map tasks to titles
        const taskTitles = {
            // Group tasks
            'groups-joined': '📋 Nhóm đã tham gia',
            'scan-groups': '🔍 Quét nhóm theo từ khóa',
            'join-groups': '➕ Tham gia nhóm',
            'leave-groups': '🚪 Rời nhóm',
            'invite-to-group': '👋 Mời bạn bè vào nhóm',
            
            // Account interaction tasks
            'post-status': '✍️ Đăng bài viết',
            'share-post': '🔗 Cắm link bài viết',
            'comment-post': '💬 Bình luận bài viết',
            'auto-like': '❤️ Tự động like',
            
            // Friend tasks
            'add-friend': '➕ Kết bạn',
            'accept-friend': '✅ Đồng ý kết bạn',
            'unfriend': '💔 Hủy kết bạn',
            'send-message': '✉️ Gửi tin nhắn',
            
            // Fanpage tasks
            'manage-fanpage': '📊 Quản lý fanpage',
            'post-fanpage': '📝 Đăng bài fanpage',
            
            // Scanned lists
            'scanned-friend-suggestions': '👤 Danh sách bạn bè',
            'scan-posts-action': '🔍 Quét bài viết'
        };
        
        title.textContent = taskTitles[task] || 'Tác vụ';
        
        // Render task form based on task type
        this.renderTaskForm(task, content);
    },

    // Render task form
    renderTaskForm: function(task, content) {
        // Example: Join Groups task
        if (task === 'join-groups') {
            content.innerHTML = `
                <div class="card">
                    <div class="card-header">➕ Tham gia nhóm</div>
                    <div class="card-body">
                        <div class="input-group">
                            <label>Danh sách ID nhóm hoặc URL (mỗi dòng 1 nhóm):</label>
                            <textarea id="groupList" class="input" rows="8" placeholder="https://facebook.com/groups/123456789&#10;987654321&#10;..."></textarea>
                        </div>
                        <div class="grid-2">
                            <div class="input-group">
                                <label>Delay giữa các request (giây):</label>
                                <input type="number" id="joinDelay" class="input" value="10" min="5" max="60">
                            </div>
                            <div class="input-group">
                                <label>Số nhóm tối đa:</label>
                                <input type="number" id="maxGroups" class="input" value="20" min="1" max="100">
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        // Add Friend task
        else if (task === 'add-friend') {
            content.innerHTML = `
                <div class="card">
                    <div class="card-header">➕ Kết bạn</div>
                    <div class="card-body">
                        <div class="input-group">
                            <label>Danh sách UID (mỗi dòng 1 UID):</label>
                            <textarea id="uidList" class="input" rows="8" placeholder="100012345678901&#10;100012345678902&#10;..."></textarea>
                        </div>
                        <div class="grid-2">
                            <div class="input-group">
                                <label>Delay giữa các request (giây):</label>
                                <input type="number" id="friendDelay" class="input" value="15" min="10" max="60">
                            </div>
                            <div class="input-group">
                                <label>Số lời mời tối đa:</label>
                                <input type="number" id="maxFriends" class="input" value="50" min="1" max="100">
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        // Post Status task
        else if (task === 'post-status') {
            content.innerHTML = `
                <div class="card">
                    <div class="card-header">✍️ Đăng bài viết</div>
                    <div class="card-body">
                        <div class="input-group">
                            <label>Nội dung bài viết (hỗ trợ spintax {option1|option2}):</label>
                            <textarea id="postContent" class="input" rows="6" placeholder="{Chào|Xin chào|Hello} mọi người! Đây là {bài viết|nội dung} {tuyệt vời|hay ho|thú vị}! {🔥|✨|💯}"></textarea>
                        </div>
                        <div class="input-group">
                            <label>Hình ảnh (URL, mỗi dòng 1 ảnh):</label>
                            <textarea id="postImages" class="input" rows="3" placeholder="https://example.com/image1.jpg&#10;https://example.com/image2.jpg"></textarea>
                        </div>
                        <div class="input-group">
                            <label>
                                <input type="checkbox" id="postToGroups"> Đăng vào các nhóm đã tham gia
                            </label>
                        </div>
                    </div>
                </div>
            `;
        }
        // Default generic form
        else {
            content.innerHTML = `
                <div class="card">
                    <div class="card-header">Tác vụ: ${task}</div>
                    <div class="card-body">
                        <p style="color: #888;">Giao diện chi tiết cho tác vụ này đang được phát triển...</p>
                        <p style="color: #888; margin-top: 10px;">Tác vụ đã được tích hợp backend và sẵn sàng hoạt động.</p>
                    </div>
                </div>
            `;
        }
    },

    // Start task
    startTask: function() {
        if (!this.currentAccount) {
            this.showToast('warning', 'Chưa chọn tài khoản', 'Vui lòng chọn tài khoản trước khi bắt đầu tác vụ');
            return;
        }
        
        if (!this.currentTask) {
            this.showToast('warning', 'Chưa chọn tác vụ', 'Vui lòng chọn tác vụ từ menu bên trái');
            return;
        }
        
        this.taskRunning = true;
        this.log('info', `Bắt đầu tác vụ: ${this.currentTask}`);
        this.log('info', `Tài khoản: ${this.currentAccount.name}`);
        this.showToast('info', 'Bắt đầu tác vụ', `Đang chạy: ${this.currentTask}`);
        
        // Call API to start task
        this.callAPI('start-task', {
            task: this.currentTask,
            account: this.currentAccount
        });
    },

    // Stop task
    stopTask: function() {
        if (!this.taskRunning) {
            this.showToast('warning', 'Không có tác vụ đang chạy', 'Chưa có tác vụ nào được khởi động');
            return;
        }
        
        this.taskRunning = false;
        this.log('warning', 'Đã dừng tác vụ');
        this.showToast('warning', 'Đã dừng tác vụ', 'Tác vụ đã được dừng lại');
    },

    // Call API
    callAPI: async function(endpoint, data) {
        const loadingToast = this.showLoading('Đang xử lý...', 'Gửi request tới backend');
        
        try {
            this.log('info', `Đang gửi request tới backend...`);
            
            const response = await fetch(`http://localhost:8000/api/${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            this.hideToast(loadingToast);
            
            if (result.success) {
                this.log('success', `Tác vụ đã được tạo! Task ID: ${result.task_id || 'N/A'}`);
                this.showToast('success', 'Tác vụ đã được tạo', `Task ID: ${result.task_id || 'N/A'}`);
            } else {
                this.log('error', `Lỗi: ${result.message}`);
                this.showToast('error', 'Lỗi xử lý tác vụ', result.message || 'Không rõ nguyên nhân');
            }
        } catch (error) {
            this.hideToast(loadingToast);
            this.log('error', `Không thể kết nối backend: ${error.message}`);
            this.showToast('error', 'Lỗi kết nối backend', error.message);
        }
    },

    // Log to activity log
    log: function(level, message) {
        const log = document.getElementById('activityLog');
        if (!log) {
            console.log(`[${level.toUpperCase()}] ${message}`);
            return;
        }
        
        const line = document.createElement('div');
        line.className = 'console-line';
        
        const levelText = {
            'info': '[THÔNG TIN]',
            'success': '[THÀNH CÔNG]',
            'error': '[LỖI]',
            'warning': '[CẢNH BÁO]'
        };
        
        const levelClass = {
            'info': 'info',
            'success': 'success',
            'error': 'error',
            'warning': 'warning'
        };
        
        line.innerHTML = `
            <span class="console-timestamp">${new Date().toLocaleTimeString('vi-VN')}</span>
            <span class="console-level ${levelClass[level]}">${levelText[level]}</span>
            <span class="console-message">${message}</span>
        `;
        
        log.appendChild(line);
        log.scrollTop = log.scrollHeight;
        
        // Limit log lines to 100
        const lines = log.querySelectorAll('.console-line');
        if (lines.length > 100) {
            lines[0].remove();
        }
    },

    // Clear log
    clearLog: function() {
        const log = document.getElementById('activityLog');
        if (log) {
            log.innerHTML = '';
            this.log('info', 'Đã xóa log');
        }
    },

    // Load proxies from backend
    loadProxiesFromBackend: async function() {
        try {
            this.log('info', 'Đang tải danh sách proxy...');
            
            const response = await fetch('http://localhost:8000/api/proxies');
            if (!response.ok) {
                throw new Error('Không thể tải danh sách proxy');
            }
            
            const proxies = await response.json();
            this.log('success', `Đã tải ${proxies.length} proxy từ backend`);
            
            // Display proxies
            this.showProxyList(proxies);
        } catch (error) {
            this.log('error', `Lỗi tải proxy: ${error.message}`);
        }
    },

    // Show proxy list
    showProxyList: function(proxies) {
        const content = document.getElementById('contentBody');
        const existingCard = content.querySelector('.card:last-child');
        
        if (existingCard) {
            const proxyListHTML = `
                <div class="card" style="margin-top: 20px;">
                    <div class="card-header">Danh sách Proxy (${proxies.length})</div>
                    <div class="card-body">
                        ${proxies.length === 0 ? `
                            <p style="text-align: center; color: #888;">Chưa có proxy nào</p>
                        ` : `
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>STT</th>
                                        <th>IP</th>
                                        <th>Port</th>
                                        <th>Protocol</th>
                                        <th>Trạng thái</th>
                                        <th>Hành động</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${proxies.map((proxy, index) => `
                                        <tr>
                                            <td>${index + 1}</td>
                                            <td>${proxy.ip}</td>
                                            <td>${proxy.port}</td>
                                            <td><span class="badge badge-info">${proxy.protocol.toUpperCase()}</span></td>
                                            <td><span class="badge badge-success">${proxy.status}</span></td>
                                            <td>
                                                <button class="btn-secondary" style="padding: 5px 10px; font-size: 12px;"
                                                        onclick="BiAds.deleteProxyById(${proxy.id})">
                                                    Xóa
                                                </button>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        `}
                    </div>
                </div>
            `;
            
            // Append or replace proxy list
            const proxyListCard = content.querySelector('.card:last-child');
            if (proxyListCard && proxyListCard.querySelector('.data-table')) {
                proxyListCard.outerHTML = proxyListHTML;
            } else {
                content.insertAdjacentHTML('beforeend', proxyListHTML);
            }
        }
    },

    // Auto assign proxies
    autoAssignProxies: async function() {
        try {
            this.log('info', 'Đang tự động gán proxy...');
            
            const response = await fetch('http://localhost:8000/api/proxies/auto-assign', {
                method: 'POST'
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Không thể gán proxy');
            }
            
            const result = await response.json();
            this.log('success', result.message);
        } catch (error) {
            this.log('error', `Lỗi gán proxy: ${error.message}`);
        }
    },

    // Delete proxy by ID
    deleteProxyById: async function(proxyId) {
        if (!confirm('Bạn có chắc chắn muốn xóa proxy này?')) {
            return;
        }
        
        try {
            const response = await fetch(`http://localhost:8000/api/proxies/${proxyId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Không thể xóa proxy');
            }
            
            this.log('success', 'Đã xóa proxy');
            this.loadProxiesFromBackend();
        } catch (error) {
            this.log('error', `Lỗi xóa proxy: ${error.message}`);
        }
    },
    
    // Load Settings Page
    renderSettingsPage: async function(content) {
        try {
            const response = await fetch('settings.html');
            const html = await response.text();
            content.innerHTML = html;
        } catch (error) {
            content.innerHTML = '<div class="info-box"><h4>⚙️ Settings Page</h4><p>Loading settings...</p></div>';
        }
    },
    
    // Load Plugins Page  
    loadPluginsPage: async function() {
        const content = document.getElementById('contentBody');
        const title = document.getElementById('contentTitle');
        title.textContent = '🔌 Quản lý Plugin';
        
        try {
            const response = await fetch('plugins.html');
            const html = await response.text();
            content.innerHTML = html;
        } catch (error) {
            content.innerHTML = '<div class="info-box"><h4>🔌 Plugins</h4><p>Loading plugins...</p></div>';
        }
    },
    
    // Load Help Page
    loadHelpPage: async function() {
        const content = document.getElementById('contentBody');
        const title = document.getElementById('contentTitle');
        title.textContent = '❓ Trợ giúp & Tài liệu';
        
        try {
            const response = await fetch('help.html');
            const html = await response.text();
            content.innerHTML = html;
        } catch (error) {
            content.innerHTML = '<div class="info-box"><h4>❓ Help</h4><p>Loading help...</p></div>';
        }
    },
    
    // Load Test API Page
    loadTestAPIPage: async function() {
        const content = document.getElementById('contentBody');
        const title = document.getElementById('contentTitle');
        title.textContent = '🧪 Test API & Debug Tool';
        
        try {
            const response = await fetch('test-api-content.html');
            const html = await response.text();
            content.innerHTML = html;
            
            // Execute any scripts in the loaded content
            const scripts = content.querySelectorAll('script');
            scripts.forEach(script => {
                const newScript = document.createElement('script');
                newScript.textContent = script.textContent;
                document.body.appendChild(newScript);
                document.body.removeChild(newScript);
            });
        } catch (error) {
            console.error('Error loading test API page:', error);
            content.innerHTML = '<div class="info-box"><h4>🧪 Test API</h4><p>Đang tải công cụ test...</p></div>';
        }
    },
    
    // Toast Notification System
    showToast: function(type, title, message, duration = 5000) {
        const container = document.getElementById('toastContainer');
        if (!container) {
            console.error('Toast container not found');
            return;
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        // Icon based on type
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️',
            loading: '⏳'
        };
        
        const icon = icons[type] || '📢';
        
        // Build toast content
        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                ${message ? `<div class="toast-message">${message}</div>` : ''}
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        // Add to container
        container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.add('hiding');
                setTimeout(() => {
                    toast.remove();
                }, 400);
            }, duration);
        }
        
        // Log to console
        console.log(`[${type.toUpperCase()}] ${title}${message ? ': ' + message : ''}`);
        
        return toast;
    },
    
    // Show loading toast (returns toast element for later removal)
    showLoading: function(title, message) {
        return this.showToast('loading', title, message, 0); // 0 = no auto-hide
    },
    
    // Hide specific toast
    hideToast: function(toastElement) {
        if (toastElement && toastElement.parentElement) {
            toastElement.classList.add('hiding');
            setTimeout(() => {
                toastElement.remove();
            }, 400);
        }
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    BiAds.init();
});

// Make BiAds available globally
window.BiAds = BiAds;
