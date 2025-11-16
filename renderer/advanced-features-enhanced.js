/**
 * Bi Ads Multi Tool PRO v3.0 - Advanced Features Enhanced
 * Nâng cấp với API integration
 */

// Extend AdvancedFeatures with real API calls
if (window.AdvancedFeatures && window.AdvancedAPIClient) {
    
    // ============================================
    // SUB ACCOUNTS - Enhanced Functions
    // ============================================
    
    AdvancedFeatures.loadSubAccountsData = async function() {
        const tbody = document.getElementById('subAccountsTableBody');
        
        // Show loading state
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 40px; color: #888;">
                        <div class="spinner"></div>
                        <p>Đang tải dữ liệu...</p>
                    </td>
                </tr>
            `;
        }
        
        try {
            const [stats, subAccounts] = await Promise.all([
                AdvancedAPIClient.getSubAccountsStats(),
                AdvancedAPIClient.getSubAccounts()
            ]);
            
            // Update stats cards with animation
            const statsElements = {
                'totalSubAccounts': stats.total,
                'activeSubAccounts': stats.active,
                'inactiveSubAccounts': stats.inactive,
                'bannedSubAccounts': stats.banned
            };
            
            Object.keys(statsElements).forEach(id => {
                const el = document.getElementById(id);
                if (el) {
                    el.style.opacity = '0.5';
                    setTimeout(() => {
                        el.textContent = statsElements[id];
                        el.style.opacity = '1';
                    }, 100);
                }
            });
            
            // Update table
            if (tbody) {
                if (subAccounts.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="6" style="text-align: center; padding: 40px; color: #888;">
                                <p>Chưa có tài khoản phụ nào</p>
                                <p>Nhấn "➕ Thêm tài khoản phụ" để bắt đầu</p>
                            </td>
                        </tr>
                    `;
                } else {
                    tbody.innerHTML = subAccounts.map((acc, index) => {
                        const statusColor = acc.status === 'active' ? 'success' : 
                                          acc.status === 'banned' ? 'danger' : 'warning';
                        return `
                        <tr class="fade-in">
                            <td>${index + 1}</td>
                            <td><code>${acc.uid}</code></td>
                            <td>${acc.name || 'N/A'}</td>
                            <td>Account #${acc.main_account_id}</td>
                            <td><span class="badge badge-${statusColor}">${acc.status.toUpperCase()}</span></td>
                            <td>
                                <button class="btn-sm btn-primary" onclick="AdvancedFeatures.editSubAccount(${acc.id})" title="Chỉnh sửa">✏️</button>
                                <button class="btn-sm btn-danger" onclick="AdvancedFeatures.deleteSubAccountConfirm(${acc.id})" title="Xóa">🗑️</button>
                            </td>
                        </tr>
                    `}).join('');
                }
            }
            
            app.addLog('success', `✅ Đã tải ${subAccounts.length} tài khoản phụ thành công`);
        } catch (error) {
            app.addLog('error', '❌ Lỗi khi tải dữ liệu tài khoản phụ: ' + error.message);
            
            // Show error in table
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align: center; padding: 40px; color: #ff4444;">
                            <p>❌ Không thể tải dữ liệu</p>
                            <p style="font-size: 12px;">${error.message}</p>
                            <button class="btn-primary" onclick="AdvancedFeatures.loadSubAccountsData()" style="margin-top: 10px;">
                                🔄 Thử lại
                            </button>
                        </td>
                    </tr>
                `;
            }
        }
    };
    
    AdvancedFeatures.showAddSubAccountModal = function() {
        const modalContent = `
            <div class="modal-header">
                <h3>➕ Thêm tài khoản phụ mới</h3>
            </div>
            <div class="modal-body">
                <div class="input-group">
                    <label>UID Facebook <span style="color: red;">*</span></label>
                    <input type="text" id="subAccountUid" placeholder="Nhập UID Facebook">
                </div>
                <div class="input-group">
                    <label>Tên hiển thị</label>
                    <input type="text" id="subAccountName" placeholder="Tên tài khoản">
                </div>
                <div class="input-group">
                    <label>Tài khoản chính <span style="color: red;">*</span></label>
                    <select id="mainAccountId">
                        <option value="">Chọn tài khoản chính...</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>
                        <input type="checkbox" id="subAccountAutoLike" checked>
                        Tự động like bài viết
                    </label>
                </div>
                <div class="input-group">
                    <label>
                        <input type="checkbox" id="subAccountAutoComment">
                        Tự động comment
                    </label>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal()">Hủy</button>
                <button class="btn-primary" onclick="AdvancedFeatures.createSubAccount()">Thêm tài khoản</button>
            </div>
        `;
        
        showModal(modalContent);
        
        // Load main accounts for dropdown
        APIClient.getAccounts().then(accounts => {
            const select = document.getElementById('mainAccountId');
            if (select) {
                select.innerHTML = '<option value="">Chọn tài khoản chính...</option>' +
                    accounts.map(acc => `<option value="${acc.id}">${acc.name || acc.uid}</option>`).join('');
            }
        });
    };
    
    AdvancedFeatures.createSubAccount = async function() {
        const uid = document.getElementById('subAccountUid')?.value;
        const name = document.getElementById('subAccountName')?.value;
        const main_account_id = parseInt(document.getElementById('mainAccountId')?.value);
        const auto_like = document.getElementById('subAccountAutoLike')?.checked;
        const auto_comment = document.getElementById('subAccountAutoComment')?.checked;
        
        if (!uid || !main_account_id) {
            app.addLog('error', 'Vui lòng nhập đầy đủ thông tin bắt buộc');
            return;
        }
        
        try {
            const result = await AdvancedAPIClient.createSubAccount({
                uid,
                name,
                main_account_id,
                auto_like,
                auto_comment,
                status: 'active'
            });
            
            app.addLog('success', `Đã thêm tài khoản phụ ${uid}`);
            closeModal();
            AdvancedFeatures.loadSubAccountsData();
        } catch (error) {
            app.addLog('error', 'Lỗi khi thêm tài khoản phụ: ' + error.message);
        }
    };
    
    AdvancedFeatures.deleteSubAccountConfirm = async function(subAccountId) {
        if (confirm('Bạn có chắc chắn muốn xóa tài khoản phụ này?')) {
            try {
                await AdvancedAPIClient.deleteSubAccount(subAccountId);
                app.addLog('success', 'Đã xóa tài khoản phụ');
                AdvancedFeatures.loadSubAccountsData();
            } catch (error) {
                app.addLog('error', 'Lỗi khi xóa tài khoản phụ: ' + error.message);
            }
        }
    };
    
    AdvancedFeatures.importSubAccounts = function() {
        app.addLog('info', 'Chức năng import tài khoản phụ đang được phát triển');
    };
    
    // ============================================
    // FACEBOOK IDS - Enhanced Functions
    // ============================================
    
    AdvancedFeatures.loadFacebookIDsData = async function() {
        try {
            const stats = await AdvancedAPIClient.getFacebookIDsStats();
            const ids = await AdvancedAPIClient.getFacebookIDs();
            
            // Update stats
            const statsElements = {
                'totalFacebookIDs': stats.total,
                'validFacebookIDs': stats.valid,
                'usedFacebookIDs': stats.used
            };
            
            Object.keys(statsElements).forEach(id => {
                const el = document.getElementById(id);
                if (el) el.textContent = statsElements[id];
            });
            
            app.addLog('success', `Đã tải ${ids.length} Facebook IDs`);
        } catch (error) {
            app.addLog('error', 'Lỗi khi tải Facebook IDs: ' + error.message);
        }
    };
    
    // ============================================
    // WHITELIST - Enhanced Functions
    // ============================================
    
    AdvancedFeatures.loadWhitelistData = async function() {
        try {
            const stats = await AdvancedAPIClient.getWhitelistStats();
            const whitelist = await AdvancedAPIClient.getWhitelistAccounts();
            
            // Update stats
            const statsElements = {
                'totalWhitelist': stats.total,
                'vipWhitelist': stats.vip,
                'friendWhitelist': stats.friend
            };
            
            Object.keys(statsElements).forEach(id => {
                const el = document.getElementById(id);
                if (el) el.textContent = statsElements[id];
            });
            
            app.addLog('success', `Đã tải ${whitelist.length} tài khoản whitelist`);
        } catch (error) {
            app.addLog('error', 'Lỗi khi tải whitelist: ' + error.message);
        }
    };
    
    // ============================================
    // POSTS - Enhanced Functions
    // ============================================
    
    AdvancedFeatures.loadPostsData = async function() {
        try {
            const stats = await AdvancedAPIClient.getPostsStats();
            const posts = await AdvancedAPIClient.getPostedContent();
            
            // Update stats
            const statsElements = {
                'totalPosts': stats.total,
                'totalLikes': stats.total_likes,
                'totalComments': stats.total_comments,
                'totalShares': stats.total_shares
            };
            
            Object.keys(statsElements).forEach(id => {
                const el = document.getElementById(id);
                if (el) el.textContent = statsElements[id];
            });
            
            app.addLog('success', `Đã tải ${posts.length} bài viết`);
        } catch (error) {
            app.addLog('error', 'Lỗi khi tải bài viết: ' + error.message);
        }
    };
    
    // ============================================
    // MESSAGES - Enhanced Functions
    // ============================================
    
    AdvancedFeatures.loadMessagesData = async function() {
        try {
            const stats = await AdvancedAPIClient.getMessagesStats();
            
            // Update stats
            const statsElements = {
                'totalConversations': stats.conversations || 0,
                'unreadMessages': stats.unread,
                'sentMessages': stats.sent
            };
            
            Object.keys(statsElements).forEach(id => {
                const el = document.getElementById(id);
                if (el) el.textContent = statsElements[id];
            });
            
            app.addLog('success', 'Đã tải thống kê tin nhắn');
        } catch (error) {
            app.addLog('error', 'Lỗi khi tải tin nhắn: ' + error.message);
        }
    };
    
    // ============================================
    // IP ADDRESSES - Enhanced Functions
    // ============================================
    
    AdvancedFeatures.loadIPAddressesData = async function() {
        try {
            const stats = await AdvancedAPIClient.getIPAddressesStats();
            const ips = await AdvancedAPIClient.getIPAddresses();
            
            // Update stats
            const statsElements = {
                'totalIPs': stats.total,
                'activeIPs': stats.active,
                'blockedIPs': stats.blocked,
                'trustedIPs': stats.trusted
            };
            
            Object.keys(statsElements).forEach(id => {
                const el = document.getElementById(id);
                if (el) el.textContent = statsElements[id];
            });
            
            app.addLog('success', `Đã tải ${ips.length} địa chỉ IP`);
        } catch (error) {
            app.addLog('error', 'Lỗi khi tải IP addresses: ' + error.message);
        }
    };
    
    // ============================================
    // Auto-load data when pages are rendered
    // ============================================
    
    const originalRenderSubAccountsPage = AdvancedFeatures.renderSubAccountsPage;
    AdvancedFeatures.renderSubAccountsPage = function(content) {
        originalRenderSubAccountsPage.call(this, content);
        setTimeout(() => AdvancedFeatures.loadSubAccountsData(), 500);
    };
    
    const originalRenderIDsPage = AdvancedFeatures.renderIDsPage;
    AdvancedFeatures.renderIDsPage = function(content) {
        originalRenderIDsPage.call(this, content);
        setTimeout(() => AdvancedFeatures.loadFacebookIDsData(), 500);
    };
    
    const originalRenderIPsPage = AdvancedFeatures.renderIPsPage;
    AdvancedFeatures.renderIPsPage = function(content) {
        originalRenderIPsPage.call(this, content);
        setTimeout(() => AdvancedFeatures.loadIPAddressesData(), 500);
    };
    
    const originalRenderWhitelistPage = AdvancedFeatures.renderWhitelistPage;
    AdvancedFeatures.renderWhitelistPage = function(content) {
        originalRenderWhitelistPage.call(this, content);
        setTimeout(() => AdvancedFeatures.loadWhitelistData(), 500);
    };
    
    const originalRenderPostsPage = AdvancedFeatures.renderPostsPage;
    AdvancedFeatures.renderPostsPage = function(content) {
        originalRenderPostsPage.call(this, content);
        setTimeout(() => AdvancedFeatures.loadPostsData(), 500);
    };
    
    const originalRenderMessagesPage = AdvancedFeatures.renderMessagesPage;
    AdvancedFeatures.renderMessagesPage = function(content) {
        originalRenderMessagesPage.call(this, content);
        setTimeout(() => AdvancedFeatures.loadMessagesData(), 500);
    };
    
    console.log('✅ Advanced Features Enhanced loaded successfully!');
} else {
    console.error('❌ AdvancedFeatures or AdvancedAPIClient not found!');
}
