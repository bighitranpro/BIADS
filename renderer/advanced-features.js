// Bi Ads Multi Tool PRO v3.0 - Advanced Features
// Nâng cấp các chức năng quản lý

const AdvancedFeatures = {
    // Quản lý tài khoản phụ
    renderSubAccountsPage: async function(content) {
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    👥 Quản lý tài khoản phụ
                    <div style="float: right;">
                        <button class="btn-primary" onclick="AdvancedFeatures.showAddSubAccountModal()">
                            ➕ Thêm tài khoản phụ
                        </button>
                        <button class="btn-secondary" onclick="AdvancedFeatures.importSubAccounts()">
                            📥 Import từ file
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="info-box">
                        <h4>ℹ️ Tài khoản phụ là gì?</h4>
                        <p>Tài khoản phụ là các tài khoản Facebook phụ dùng để tương tác, tăng tương tác cho tài khoản chính.</p>
                        <p><strong>Công dụng:</strong></p>
                        <ul style="margin-left: 20px; color: #888;">
                            <li>Tự động like, comment cho bài viết của tài khoản chính</li>
                            <li>Tạo lượng tương tác tự nhiên</li>
                            <li>Tăng độ tin cậy cho tài khoản chính</li>
                        </ul>
                    </div>

                    <div id="subAccountsList">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>STT</th>
                                    <th>UID</th>
                                    <th>Tên</th>
                                    <th>Tài khoản chính</th>
                                    <th>Trạng thái</th>
                                    <th>Hành động</th>
                                </tr>
                            </thead>
                            <tbody id="subAccountsTableBody">
                                <tr>
                                    <td colspan="6" style="text-align: center; padding: 40px; color: #888;">
                                        <p>Chưa có tài khoản phụ nào</p>
                                        <p>Nhấn "➕ Thêm tài khoản phụ" để bắt đầu</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="card" style="margin-top: 20px; background: rgba(102, 126, 234, 0.1);">
                        <div class="card-header">⚙️ Cài đặt tự động</div>
                        <div class="card-body">
                            <div class="grid-2">
                                <div class="input-group">
                                    <label>
                                        <input type="checkbox" id="autoLikeMainPosts" checked>
                                        Tự động like bài viết tài khoản chính
                                    </label>
                                </div>
                                <div class="input-group">
                                    <label>
                                        <input type="checkbox" id="autoCommentMainPosts">
                                        Tự động comment bài viết tài khoản chính
                                    </label>
                                </div>
                            </div>
                            <div class="input-group">
                                <label>Delay giữa các tương tác (giây)</label>
                                <input type="number" id="interactionDelay" value="5" min="1" max="60">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Load sub accounts data
        await this.loadSubAccounts();
    },

    // Quản lý ID
    renderIDsPage: function(content) {
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    🆔 Quản lý ID Facebook
                    <div style="float: right;">
                        <button class="btn-primary" onclick="AdvancedFeatures.addIDsManually()">
                            ➕ Thêm ID
                        </button>
                        <button class="btn-secondary" onclick="AdvancedFeatures.importIDsFromFile()">
                            📥 Import từ file
                        </button>
                        <button class="btn-success" onclick="AdvancedFeatures.scanIDsFromGroup()">
                            🔍 Quét từ nhóm
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value" id="totalIDs">0</div>
                            <div class="stat-label">Tổng số ID</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="validIDs">0</div>
                            <div class="stat-label">ID hợp lệ</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="usedIDs">0</div>
                            <div class="stat-label">Đã sử dụng</div>
                        </div>
                    </div>

                    <div class="card" style="margin-top: 20px;">
                        <div class="card-header">
                            🔧 Công cụ xử lý ID
                            <div style="float: right;">
                                <button class="btn-warning" onclick="AdvancedFeatures.validateAllIDs()">
                                    ✓ Kiểm tra tất cả
                                </button>
                                <button class="btn-secondary" onclick="AdvancedFeatures.exportIDs()">
                                    📤 Xuất file
                                </button>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="grid-2">
                                <div class="input-group">
                                    <label>Lọc theo trạng thái</label>
                                    <select id="idStatusFilter" onchange="AdvancedFeatures.filterIDs()">
                                        <option value="all">Tất cả</option>
                                        <option value="valid">Hợp lệ</option>
                                        <option value="invalid">Không hợp lệ</option>
                                        <option value="used">Đã sử dụng</option>
                                        <option value="unused">Chưa sử dụng</option>
                                    </select>
                                </div>
                                <div class="input-group">
                                    <label>Tìm kiếm ID</label>
                                    <input type="text" id="idSearch" placeholder="Nhập ID hoặc tên..." onkeyup="AdvancedFeatures.searchIDs()">
                                </div>
                            </div>
                        </div>
                    </div>

                    <div id="idsList" style="margin-top: 20px;">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th><input type="checkbox" onclick="AdvancedFeatures.selectAllIDs(this)"></th>
                                    <th>STT</th>
                                    <th>UID</th>
                                    <th>Tên</th>
                                    <th>Trạng thái</th>
                                    <th>Nguồn</th>
                                    <th>Ngày thêm</th>
                                    <th>Hành động</th>
                                </tr>
                            </thead>
                            <tbody id="idsTableBody">
                                <tr>
                                    <td colspan="8" style="text-align: center; padding: 40px; color: #888;">
                                        <p>Chưa có ID nào</p>
                                        <p>Nhấn "➕ Thêm ID" hoặc "🔍 Quét từ nhóm" để bắt đầu</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="card" style="margin-top: 20px; background: rgba(102, 126, 234, 0.05);">
                        <div class="card-header">📋 Hành động với ID đã chọn</div>
                        <div class="card-body">
                            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                                <button class="btn-primary" onclick="AdvancedFeatures.addFriendsSelected()">
                                    ➕ Kết bạn
                                </button>
                                <button class="btn-secondary" onclick="AdvancedFeatures.sendMessageSelected()">
                                    ✉️ Gửi tin nhắn
                                </button>
                                <button class="btn-success" onclick="AdvancedFeatures.inviteToGroupSelected()">
                                    👋 Mời vào nhóm
                                </button>
                                <button class="btn-warning" onclick="AdvancedFeatures.exportSelected()">
                                    📤 Xuất đã chọn
                                </button>
                                <button class="btn-secondary" onclick="AdvancedFeatures.deleteSelected()">
                                    🗑️ Xóa đã chọn
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Load data after rendering
        this.loadFacebookIDs();
    },

    // Quản lý IP thiết bị
    renderIPsPage: function(content) {
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    📡 Quản lý IP thiết bị
                    <div style="float: right;">
                        <button class="btn-primary" onclick="AdvancedFeatures.detectCurrentIP()">
                            🔍 Phát hiện IP hiện tại
                        </button>
                        <button class="btn-secondary" onclick="AdvancedFeatures.addIPManually()">
                            ➕ Thêm IP thủ công
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="info-box">
                        <h4>📌 Tại sao cần quản lý IP?</h4>
                        <p>Facebook theo dõi IP để phát hiện hành vi bất thường. Quản lý IP giúp:</p>
                        <ul style="margin-left: 20px; color: #888;">
                            <li>Tránh bị checkpoint do đổi IP đột ngột</li>
                            <li>Gán IP cố định cho từng tài khoản</li>
                            <li>Theo dõi lịch sử truy cập của tài khoản</li>
                            <li>Cảnh báo khi tài khoản truy cập từ IP lạ</li>
                        </ul>
                    </div>

                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value" id="totalIPs">0</div>
                            <div class="stat-label">Tổng số IP</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="activeIPs">0</div>
                            <div class="stat-label">IP đang dùng</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="blockedIPs">0</div>
                            <div class="stat-label">IP bị chặn</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="trustedIPs">0</div>
                            <div class="stat-label">IP tin cậy</div>
                        </div>
                    </div>

                    <div class="card" style="margin-top: 20px;">
                        <div class="card-header">🌍 Danh sách IP</div>
                        <div class="card-body">
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>STT</th>
                                        <th>Địa chỉ IP</th>
                                        <th>Vị trí</th>
                                        <th>Tài khoản sử dụng</th>
                                        <th>Trạng thái</th>
                                        <th>Lần dùng cuối</th>
                                        <th>Hành động</th>
                                    </tr>
                                </thead>
                                <tbody id="ipsTableBody">
                                    <tr>
                                        <td colspan="7" style="text-align: center; padding: 40px; color: #888;">
                                            <p>Chưa có IP nào được lưu</p>
                                            <p>Nhấn "🔍 Phát hiện IP hiện tại" để bắt đầu</p>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="card" style="margin-top: 20px; background: rgba(231, 76, 60, 0.1);">
                        <div class="card-header">⚠️ Cảnh báo IP</div>
                        <div class="card-body">
                            <div class="input-group">
                                <label>
                                    <input type="checkbox" id="alertNewIP" checked>
                                    Cảnh báo khi tài khoản truy cập từ IP mới
                                </label>
                            </div>
                            <div class="input-group">
                                <label>
                                    <input type="checkbox" id="blockUnknownIP">
                                    Chặn tài khoản truy cập từ IP không tin cậy
                                </label>
                            </div>
                            <div class="input-group">
                                <label>
                                    <input type="checkbox" id="autoTrustProxy" checked>
                                    Tự động tin cậy IP từ proxy
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // Quản lý Whitelist
    renderWhitelistPage: function(content) {
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    ✅ Quản lý tài khoản Whitelist
                    <div style="float: right;">
                        <button class="btn-primary" onclick="AdvancedFeatures.addToWhitelist()">
                            ➕ Thêm vào whitelist
                        </button>
                        <button class="btn-secondary" onclick="AdvancedFeatures.importWhitelist()">
                            📥 Import từ file
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="info-box">
                        <h4>💡 Whitelist là gì?</h4>
                        <p>Whitelist là danh sách các tài khoản Facebook được "bảo vệ", hệ thống sẽ:</p>
                        <ul style="margin-left: 20px; color: #888;">
                            <li><strong>KHÔNG</strong> unfriend tự động</li>
                            <li><strong>KHÔNG</strong> block hoặc report</li>
                            <li><strong>ƯU TIÊN</strong> tương tác (like, comment)</li>
                            <li><strong>TỰ ĐỘNG</strong> chấp nhận lời mời kết bạn</li>
                        </ul>
                        <p><strong>Sử dụng cho:</strong> Bạn bè thân, khách hàng VIP, đối tác, admin nhóm, v.v.</p>
                    </div>

                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value" id="totalWhitelist">0</div>
                            <div class="stat-label">Tổng whitelist</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="friendsWhitelist">0</div>
                            <div class="stat-label">Đã kết bạn</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="vipWhitelist">0</div>
                            <div class="stat-label">VIP</div>
                        </div>
                    </div>

                    <div class="card" style="margin-top: 20px;">
                        <div class="card-header">
                            🔍 Tìm kiếm & Lọc
                            <div style="float: right;">
                                <button class="btn-warning" onclick="AdvancedFeatures.syncWhitelist()">
                                    🔄 Đồng bộ trạng thái
                                </button>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="grid-3">
                                <div class="input-group">
                                    <label>Tìm kiếm</label>
                                    <input type="text" id="whitelistSearch" placeholder="Tên hoặc UID..." onkeyup="AdvancedFeatures.searchWhitelist()">
                                </div>
                                <div class="input-group">
                                    <label>Loại</label>
                                    <select id="whitelistType" onchange="AdvancedFeatures.filterWhitelist()">
                                        <option value="all">Tất cả</option>
                                        <option value="vip">VIP</option>
                                        <option value="customer">Khách hàng</option>
                                        <option value="partner">Đối tác</option>
                                        <option value="admin">Admin</option>
                                        <option value="friend">Bạn bè</option>
                                    </select>
                                </div>
                                <div class="input-group">
                                    <label>Trạng thái</label>
                                    <select id="whitelistStatus" onchange="AdvancedFeatures.filterWhitelist()">
                                        <option value="all">Tất cả</option>
                                        <option value="friend">Bạn bè</option>
                                        <option value="notfriend">Chưa kết bạn</option>
                                        <option value="pending">Đang chờ</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div id="whitelistTable" style="margin-top: 20px;">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th><input type="checkbox" onclick="AdvancedFeatures.selectAllWhitelist(this)"></th>
                                    <th>STT</th>
                                    <th>UID</th>
                                    <th>Tên</th>
                                    <th>Loại</th>
                                    <th>Trạng thái</th>
                                    <th>Ghi chú</th>
                                    <th>Hành động</th>
                                </tr>
                            </thead>
                            <tbody id="whitelistTableBody">
                                <tr>
                                    <td colspan="8" style="text-align: center; padding: 40px; color: #888;">
                                        <p>Chưa có tài khoản nào trong whitelist</p>
                                        <p>Nhấn "➕ Thêm vào whitelist" để bắt đầu</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="card" style="margin-top: 20px; background: rgba(46, 204, 113, 0.1);">
                        <div class="card-header">⚙️ Cài đặt Whitelist</div>
                        <div class="card-body">
                            <div class="grid-2">
                                <div class="input-group">
                                    <label>
                                        <input type="checkbox" id="autoAcceptWhitelist" checked>
                                        Tự động chấp nhận lời mời kết bạn từ whitelist
                                    </label>
                                </div>
                                <div class="input-group">
                                    <label>
                                        <input type="checkbox" id="autoLikeWhitelist" checked>
                                        Tự động like bài viết từ whitelist
                                    </label>
                                </div>
                                <div class="input-group">
                                    <label>
                                        <input type="checkbox" id="priorityMessageWhitelist" checked>
                                        Ưu tiên trả lời tin nhắn từ whitelist
                                    </label>
                                </div>
                                <div class="input-group">
                                    <label>
                                        <input type="checkbox" id="neverUnfriendWhitelist" checked>
                                        Không bao giờ unfriend whitelist
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // Quản lý bài viết đã đăng
    renderPostsPage: function(content) {
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    📝 Quản lý bài viết đã đăng
                    <div style="float: right;">
                        <button class="btn-primary" onclick="AdvancedFeatures.syncPosts()">
                            🔄 Đồng bộ bài viết
                        </button>
                        <button class="btn-secondary" onclick="AdvancedFeatures.exportPosts()">
                            📤 Xuất Excel
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value" id="totalPosts">0</div>
                            <div class="stat-label">Tổng bài viết</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="totalLikes">0</div>
                            <div class="stat-label">Tổng likes</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="totalComments">0</div>
                            <div class="stat-label">Tổng comments</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="totalShares">0</div>
                            <div class="stat-label">Tổng shares</div>
                        </div>
                    </div>

                    <div class="card" style="margin-top: 20px;">
                        <div class="card-header">🔍 Tìm kiếm & Lọc</div>
                        <div class="card-body">
                            <div class="grid-3">
                                <div class="input-group">
                                    <label>Tìm kiếm nội dung</label>
                                    <input type="text" id="postSearch" placeholder="Nhập từ khóa..." onkeyup="AdvancedFeatures.searchPosts()">
                                </div>
                                <div class="input-group">
                                    <label>Thời gian</label>
                                    <select id="postTimeFilter" onchange="AdvancedFeatures.filterPosts()">
                                        <option value="all">Tất cả</option>
                                        <option value="today">Hôm nay</option>
                                        <option value="week">Tuần này</option>
                                        <option value="month">Tháng này</option>
                                        <option value="custom">Tùy chỉnh</option>
                                    </select>
                                </div>
                                <div class="input-group">
                                    <label>Tài khoản</label>
                                    <select id="postAccountFilter" onchange="AdvancedFeatures.filterPosts()">
                                        <option value="all">Tất cả tài khoản</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div id="postsList" style="margin-top: 20px;">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th><input type="checkbox" onclick="AdvancedFeatures.selectAllPosts(this)"></th>
                                    <th>STT</th>
                                    <th>Nội dung</th>
                                    <th>Tài khoản</th>
                                    <th>Thời gian</th>
                                    <th>Like</th>
                                    <th>Comment</th>
                                    <th>Share</th>
                                    <th>Hành động</th>
                                </tr>
                            </thead>
                            <tbody id="postsTableBody">
                                <tr>
                                    <td colspan="9" style="text-align: center; padding: 40px; color: #888;">
                                        <p>Chưa có bài viết nào</p>
                                        <p>Nhấn "🔄 Đồng bộ bài viết" để tải dữ liệu</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="card" style="margin-top: 20px; background: rgba(102, 126, 234, 0.05);">
                        <div class="card-header">📊 Hành động với bài đã chọn</div>
                        <div class="card-body">
                            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                                <button class="btn-warning" onclick="AdvancedFeatures.editSelectedPosts()">
                                    ✏️ Chỉnh sửa
                                </button>
                                <button class="btn-secondary" onclick="AdvancedFeatures.hideSelectedPosts()">
                                    👁️ Ẩn bài viết
                                </button>
                                <button class="btn-success" onclick="AdvancedFeatures.boostSelectedPosts()">
                                    🚀 Tăng tương tác
                                </button>
                                <button class="btn-primary" onclick="AdvancedFeatures.shareSelectedPosts()">
                                    🔗 Chia sẻ lại
                                </button>
                                <button class="btn-secondary" onclick="AdvancedFeatures.deleteSelectedPosts()">
                                    🗑️ Xóa bài viết
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Load data after rendering
        this.loadPostAccountFilter();
        this.loadPostedContent();
    },

    // Quản lý tin nhắn
    renderMessagesPage: function(content) {
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    💬 Quản lý tin nhắn
                    <div style="float: right;">
                        <button class="btn-primary" onclick="AdvancedFeatures.composeNewMessage()">
                            ✉️ Soạn tin nhắn mới
                        </button>
                        <button class="btn-secondary" onclick="AdvancedFeatures.refreshMessages()">
                            🔄 Làm mới
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value" id="totalConversations">0</div>
                            <div class="stat-label">Cuộc trò chuyện</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="unreadMessages">0</div>
                            <div class="stat-label">Chưa đọc</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="sentMessages">0</div>
                            <div class="stat-label">Đã gửi</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="scheduledMessages">0</div>
                            <div class="stat-label">Đã lên lịch</div>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 300px 1fr; gap: 20px; margin-top: 20px;">
                        <!-- Conversation List -->
                        <div class="card" style="margin: 0;">
                            <div class="card-header">
                                💬 Danh sách hội thoại
                                <input type="text" id="conversationSearch" placeholder="🔍 Tìm kiếm..." 
                                       style="width: 100%; margin-top: 10px;" onkeyup="AdvancedFeatures.searchConversations()">
                            </div>
                            <div class="card-body" style="padding: 0; max-height: 500px; overflow-y: auto;">
                                <div id="conversationList">
                                    <div style="text-align: center; padding: 40px; color: #888;">
                                        <p>Chưa có tin nhắn</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Message Thread -->
                        <div class="card" style="margin: 0;">
                            <div class="card-header">
                                <span id="currentConversationName">Chọn cuộc trò chuyện</span>
                                <div style="float: right;">
                                    <button class="btn-primary" style="padding: 5px 10px; font-size: 12px;" 
                                            onclick="AdvancedFeatures.markAsRead()">
                                        ✓ Đánh dấu đã đọc
                                    </button>
                                    <button class="btn-secondary" style="padding: 5px 10px; font-size: 12px;" 
                                            onclick="AdvancedFeatures.archiveConversation()">
                                        📦 Lưu trữ
                                    </button>
                                </div>
                            </div>
                            <div class="card-body" style="padding: 0;">
                                <div id="messageThread" style="max-height: 400px; overflow-y: auto; padding: 20px; background: #0f0f1e;">
                                    <div style="text-align: center; padding: 40px; color: #888;">
                                        <p>Chọn một cuộc trò chuyện để xem tin nhắn</p>
                                    </div>
                                </div>
                                <div style="padding: 15px; background: #1a1a2e; border-top: 1px solid rgba(255,255,255,0.1);">
                                    <div style="display: flex; gap: 10px;">
                                        <input type="text" id="messageInput" placeholder="Nhập tin nhắn..." 
                                               style="flex: 1;" onkeypress="if(event.key==='Enter') AdvancedFeatures.sendMessage()">
                                        <button class="btn-primary" onclick="AdvancedFeatures.sendMessage()">
                                            📤 Gửi
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card" style="margin-top: 20px; background: rgba(102, 126, 234, 0.1);">
                        <div class="card-header">🤖 Tin nhắn tự động</div>
                        <div class="card-body">
                            <div class="grid-2">
                                <div class="input-group">
                                    <label>
                                        <input type="checkbox" id="autoReply" checked>
                                        Tự động trả lời tin nhắn
                                    </label>
                                </div>
                                <div class="input-group">
                                    <label>
                                        <input type="checkbox" id="autoGreeting">
                                        Gửi lời chào tự động cho bạn mới
                                    </label>
                                </div>
                            </div>
                            <div class="input-group">
                                <label>Tin nhắn tự động</label>
                                <textarea id="autoReplyMessage" rows="3" placeholder="Xin chào! Tôi đang bận, sẽ trả lời bạn sau..."></textarea>
                            </div>
                            <button class="btn-primary" onclick="AdvancedFeatures.saveAutoReplySettings()">
                                💾 Lưu cài đặt
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // ============================================
    // SUB ACCOUNTS IMPLEMENTATION
    // ============================================
    
    subAccounts: [],
    subAccountsStats: null,
    
    async loadSubAccounts() {
        try {
            const response = await fetch('http://localhost:8000/api/sub-accounts/');
            const data = await response.json();
            this.subAccounts = data;
            
            // Update table
            const tbody = document.getElementById('subAccountsTableBody');
            if (!tbody) return;
            
            if (data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align: center; padding: 40px; color: #888;">
                            <p>Chưa có tài khoản phụ nào</p>
                            <p>Nhấn "➕ Thêm tài khoản phụ" để bắt đầu</p>
                        </td>
                    </tr>
                `;
                return;
            }
            
            tbody.innerHTML = data.map((sub, index) => {
                const statusBadge = sub.status === 'active' 
                    ? '<span class="badge-success">Active</span>' 
                    : sub.status === 'inactive'
                    ? '<span class="badge-warning">Inactive</span>'
                    : '<span class="badge-danger">Banned</span>';
                
                const mainAccInfo = sub.main_account_info 
                    ? `${sub.main_account_info.name || sub.main_account_info.uid}`
                    : 'N/A';
                
                return `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${sub.uid}</td>
                        <td>${sub.name || 'N/A'}</td>
                        <td>${mainAccInfo}</td>
                        <td>${statusBadge}</td>
                        <td>
                            <button class="btn-sm btn-primary" onclick="AdvancedFeatures.editSubAccount(${sub.id})" title="Chỉnh sửa">
                                ✏️
                            </button>
                            <button class="btn-sm btn-danger" onclick="AdvancedFeatures.deleteSubAccount(${sub.id})" title="Xóa">
                                🗑️
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
            
            // Load stats
            await this.loadSubAccountsStats();
            
        } catch (error) {
            console.error('Error loading sub accounts:', error);
            app.addLog('error', `Lỗi tải tài khoản phụ: ${error.message}`);
        }
    },
    
    async loadSubAccountsStats() {
        try {
            const response = await fetch('http://localhost:8000/api/sub-accounts/stats');
            const stats = await response.json();
            this.subAccountsStats = stats;
            
            // Update UI if stats display exists
            // Can add stats display in the UI later
            console.log('Sub Accounts Stats:', stats);
            
        } catch (error) {
            console.error('Error loading sub accounts stats:', error);
        }
    },
    
    async showAddSubAccountModal() {
        // Get list of main accounts
        try {
            const response = await fetch('http://localhost:8000/api/accounts?limit=1000');
            const accounts = await response.json();
            
            if (accounts.length === 0) {
                app.addLog('warning', 'Vui lòng thêm tài khoản chính trước');
                return;
            }
            
            const accountOptions = accounts.map(acc => 
                `<option value="${acc.id}">${acc.name || acc.username || acc.uid}</option>`
            ).join('');
            
            ModalConfirmation.showInput({
                title: '➕ Thêm tài khoản phụ',
                html: `
                    <div class="input-group">
                        <label>Tài khoản chính</label>
                        <select id="modalMainAccountId" style="width: 100%; padding: 8px; background: #1a1a2e; border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; color: white;">
                            ${accountOptions}
                        </select>
                    </div>
                    <div class="input-group">
                        <label>Facebook UID (bắt buộc)</label>
                        <input type="text" id="modalSubUid" placeholder="100012345678" style="width: 100%;">
                    </div>
                    <div class="input-group">
                        <label>Tên hiển thị</label>
                        <input type="text" id="modalSubName" placeholder="Nguyễn Văn A" style="width: 100%;">
                    </div>
                    <div class="input-group">
                        <label>Username</label>
                        <input type="text" id="modalSubUsername" placeholder="nguyenvana" style="width: 100%;">
                    </div>
                    <div class="input-group">
                        <label>
                            <input type="checkbox" id="modalAutoLike" checked>
                            Tự động like bài viết
                        </label>
                    </div>
                    <div class="input-group">
                        <label>
                            <input type="checkbox" id="modalAutoComment">
                            Tự động comment
                        </label>
                    </div>
                `,
                confirmText: 'Tạo',
                onConfirm: async () => {
                    const mainAccountId = document.getElementById('modalMainAccountId').value;
                    const uid = document.getElementById('modalSubUid').value.trim();
                    const name = document.getElementById('modalSubName').value.trim();
                    const username = document.getElementById('modalSubUsername').value.trim();
                    const autoLike = document.getElementById('modalAutoLike').checked;
                    const autoComment = document.getElementById('modalAutoComment').checked;
                    
                    if (!uid) {
                        app.addLog('warning', 'Vui lòng nhập UID');
                        return;
                    }
                    
                    await this.createSubAccount({
                        main_account_id: parseInt(mainAccountId),
                        uid: uid,
                        name: name || null,
                        username: username || null,
                        auto_like: autoLike,
                        auto_comment: autoComment,
                        status: 'active'
                    });
                }
            });
            
        } catch (error) {
            app.addLog('error', `Lỗi: ${error.message}`);
        }
    },
    
    async createSubAccount(data) {
        try {
            const response = await fetch('http://localhost:8000/api/sub-accounts/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                app.addLog('success', result.message);
                await this.loadSubAccounts();
            } else {
                app.addLog('error', result.detail || 'Lỗi tạo sub account');
            }
            
        } catch (error) {
            app.addLog('error', `Lỗi tạo sub account: ${error.message}`);
        }
    },
    
    async editSubAccount(subAccountId) {
        try {
            // Get current sub account data
            const response = await fetch(`http://localhost:8000/api/sub-accounts/${subAccountId}`);
            const subAcc = await response.json();
            
            ModalConfirmation.showInput({
                title: '✏️ Chỉnh sửa tài khoản phụ',
                html: `
                    <div class="input-group">
                        <label>UID: ${subAcc.uid}</label>
                    </div>
                    <div class="input-group">
                        <label>Tên hiển thị</label>
                        <input type="text" id="modalEditName" value="${subAcc.name || ''}" style="width: 100%;">
                    </div>
                    <div class="input-group">
                        <label>Username</label>
                        <input type="text" id="modalEditUsername" value="${subAcc.username || ''}" style="width: 100%;">
                    </div>
                    <div class="input-group">
                        <label>Trạng thái</label>
                        <select id="modalEditStatus" style="width: 100%; padding: 8px; background: #1a1a2e; border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; color: white;">
                            <option value="active" ${subAcc.status === 'active' ? 'selected' : ''}>Active</option>
                            <option value="inactive" ${subAcc.status === 'inactive' ? 'selected' : ''}>Inactive</option>
                            <option value="banned" ${subAcc.status === 'banned' ? 'selected' : ''}>Banned</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label>
                            <input type="checkbox" id="modalEditAutoLike" ${subAcc.auto_like ? 'checked' : ''}>
                            Tự động like
                        </label>
                    </div>
                    <div class="input-group">
                        <label>
                            <input type="checkbox" id="modalEditAutoComment" ${subAcc.auto_comment ? 'checked' : ''}>
                            Tự động comment
                        </label>
                    </div>
                    <div class="input-group">
                        <label>
                            <input type="checkbox" id="modalEditAutoShare" ${subAcc.auto_share ? 'checked' : ''}>
                            Tự động share
                        </label>
                    </div>
                `,
                confirmText: 'Cập nhật',
                onConfirm: async () => {
                    const updateData = {
                        name: document.getElementById('modalEditName').value.trim() || null,
                        username: document.getElementById('modalEditUsername').value.trim() || null,
                        status: document.getElementById('modalEditStatus').value,
                        auto_like: document.getElementById('modalEditAutoLike').checked,
                        auto_comment: document.getElementById('modalEditAutoComment').checked,
                        auto_share: document.getElementById('modalEditAutoShare').checked
                    };
                    
                    await this.updateSubAccount(subAccountId, updateData);
                }
            });
            
        } catch (error) {
            app.addLog('error', `Lỗi: ${error.message}`);
        }
    },
    
    async updateSubAccount(subAccountId, data) {
        try {
            const response = await fetch(`http://localhost:8000/api/sub-accounts/${subAccountId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                app.addLog('success', result.message);
                await this.loadSubAccounts();
            } else {
                app.addLog('error', result.detail || 'Lỗi cập nhật sub account');
            }
            
        } catch (error) {
            app.addLog('error', `Lỗi cập nhật sub account: ${error.message}`);
        }
    },
    
    async deleteSubAccount(subAccountId) {
        ModalConfirmation.showDanger({
            title: '🗑️ Xóa tài khoản phụ?',
            message: 'Bạn có chắc chắn muốn xóa tài khoản phụ này?',
            details: 'Hành động này không thể hoàn tác.',
            confirmText: 'Xóa ngay',
            onConfirm: async () => {
                try {
                    const response = await fetch(`http://localhost:8000/api/sub-accounts/${subAccountId}`, {
                        method: 'DELETE'
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok && result.success) {
                        app.addLog('success', result.message);
                        await this.loadSubAccounts();
                    } else {
                        app.addLog('error', result.detail || 'Lỗi xóa sub account');
                    }
                    
                } catch (error) {
                    app.addLog('error', `Lỗi xóa sub account: ${error.message}`);
                }
            }
        });
    },
    
    async importSubAccounts() {
        ModalConfirmation.showInput({
            title: '📥 Import tài khoản phụ',
            html: `
                <div class="info-box" style="margin-bottom: 15px;">
                    <p><strong>Format file:</strong></p>
                    <p style="font-family: monospace; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 4px;">
                        main_account_uid|sub_uid|name|username
                    </p>
                    <p><strong>Ví dụ:</strong></p>
                    <p style="font-family: monospace; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 4px;">
                        100012345678|100087654321|Nguyen Van A|nguyenvana<br>
                        100012345678|100087654322|Tran Thi B
                    </p>
                </div>
                <div class="input-group">
                    <label>Chọn file</label>
                    <input type="file" id="modalImportFile" accept=".txt" style="width: 100%;">
                </div>
            `,
            confirmText: 'Import',
            onConfirm: async () => {
                const fileInput = document.getElementById('modalImportFile');
                const file = fileInput.files[0];
                
                if (!file) {
                    app.addLog('warning', 'Vui lòng chọn file');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    app.addLog('info', 'Đang import...');
                    
                    const response = await fetch('http://localhost:8000/api/sub-accounts/bulk/import', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok && result.success) {
                        app.addLog('success', result.message);
                        if (result.errors && result.errors.length > 0) {
                            console.log('Import errors:', result.errors);
                        }
                        await this.loadSubAccounts();
                    } else {
                        app.addLog('error', result.detail || 'Lỗi import');
                    }
                    
                } catch (error) {
                    app.addLog('error', `Lỗi import: ${error.message}`);
                }
            }
        });
    },
    
    // Placeholder functions for actions
    // showAddSubAccountModal: () => app.addLog('info', 'Chức năng thêm tài khoản phụ'),
    // importSubAccounts: () => app.addLog('info', 'Import tài khoản phụ'),
    // ============================================
    // FACEBOOK IDS IMPLEMENTATION
    // ============================================
    
    facebookIDs: [],
    facebookIDsStats: null,
    
    async loadFacebookIDs() {
        try {
            const response = await fetch('http://localhost:8000/api/facebook-ids/');
            const data = await response.json();
            this.facebookIDs = data;
            
            // Update table
            const tbody = document.getElementById('idsTableBody');
            if (!tbody) return;
            
            if (data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" style="text-align: center; padding: 40px; color: #888;">
                            <p>Chưa có ID nào</p>
                            <p>Nhấn "➕ Thêm ID" hoặc "🔍 Quét từ nhóm" để bắt đầu</p>
                        </td>
                    </tr>
                `;
                return;
            }
            
            tbody.innerHTML = data.map((fb_id, index) => {
                const statusBadge = fb_id.status === 'valid' 
                    ? '<span class="badge-success">Hợp lệ</span>' 
                    : fb_id.status === 'invalid'
                    ? '<span class="badge-danger">Không hợp lệ</span>'
                    : '<span class="badge-warning">Đã dùng</span>';
                
                return `
                    <tr>
                        <td><input type="checkbox" class="id-checkbox" data-id="${fb_id.id}"></td>
                        <td>${index + 1}</td>
                        <td>${fb_id.uid}</td>
                        <td>${fb_id.name || 'N/A'}</td>
                        <td>${statusBadge}</td>
                        <td>${fb_id.source || 'manual'}</td>
                        <td>${new Date(fb_id.created_at).toLocaleDateString('vi-VN')}</td>
                        <td>
                            <button class="btn-sm btn-danger" onclick="AdvancedFeatures.deleteFacebookID(${fb_id.id})" title="Xóa">
                                🗑️
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
            
            // Load stats
            await this.loadFacebookIDsStats();
            
        } catch (error) {
            console.error('Error loading Facebook IDs:', error);
            BiAds.showToast('error', 'Lỗi tải Facebook IDs', error.message);
        }
    },
    
    async loadFacebookIDsStats() {
        try {
            const response = await fetch('http://localhost:8000/api/facebook-ids/stats');
            const stats = await response.json();
            this.facebookIDsStats = stats;
            
            // Update stats display
            const totalElem = document.getElementById('totalIDs');
            const validElem = document.getElementById('validIDs');
            const usedElem = document.getElementById('usedIDs');
            
            if (totalElem) totalElem.textContent = stats.total_count;
            if (validElem) validElem.textContent = stats.valid_count;
            if (usedElem) usedElem.textContent = stats.used_count;
            
        } catch (error) {
            console.error('Error loading Facebook IDs stats:', error);
        }
    },
    
    addIDsManually: () => {
        ModalConfirmation.showInput({
            title: '➕ Thêm Facebook ID',
            html: `
                <div class="input-group">
                    <label>Facebook UID (bắt buộc)</label>
                    <input type="text" id="modalIDUid" placeholder="100012345678" style="width: 100%;">
                </div>
                <div class="input-group">
                    <label>Tên hiển thị</label>
                    <input type="text" id="modalIDName" placeholder="Nguyễn Văn A" style="width: 100%;">
                </div>
                <div class="input-group">
                    <label>Username</label>
                    <input type="text" id="modalIDUsername" placeholder="nguyenvana" style="width: 100%;">
                </div>
            `,
            confirmText: 'Thêm',
            onConfirm: async () => {
                const uid = document.getElementById('modalIDUid').value.trim();
                const name = document.getElementById('modalIDName').value.trim();
                const username = document.getElementById('modalIDUsername').value.trim();
                
                if (!uid) {
                    BiAds.showToast('warning', 'Thiếu thông tin', 'Vui lòng nhập UID');
                    return;
                }
                
                try {
                    const response = await fetch('http://localhost:8000/api/facebook-ids/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ uid, name, username, source: 'manual' })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok && result.success) {
                        BiAds.showToast('success', 'Thành công', result.message);
                        await AdvancedFeatures.loadFacebookIDs();
                    } else {
                        BiAds.showToast('error', 'Lỗi', result.detail || 'Không thể thêm ID');
                    }
                } catch (error) {
                    BiAds.showToast('error', 'Lỗi', error.message);
                }
            }
        });
    },
    
    importIDsFromFile: () => {
        ModalConfirmation.showInput({
            title: '📥 Import Facebook IDs',
            html: `
                <div class="info-box" style="margin-bottom: 15px;">
                    <p><strong>Format hỗ trợ:</strong></p>
                    <p style="font-family: monospace; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 4px;">
                        100012345678<br>
                        facebook.com/profile.php?id=100012345678<br>
                        100012345678|Nguyen Van A|nguyenvana
                    </p>
                </div>
                <div class="input-group">
                    <label>Chọn file</label>
                    <input type="file" id="modalImportIDFile" accept=".txt" style="width: 100%;">
                </div>
            `,
            confirmText: 'Import',
            onConfirm: async () => {
                const fileInput = document.getElementById('modalImportIDFile');
                const file = fileInput.files[0];
                
                if (!file) {
                    BiAds.showToast('warning', 'Thiếu file', 'Vui lòng chọn file');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    BiAds.showToast('info', 'Đang import...', 'Vui lòng đợi');
                    
                    const response = await fetch('http://localhost:8000/api/facebook-ids/bulk/import?source=import', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok && result.success) {
                        BiAds.showToast('success', 'Thành công', result.message);
                        await AdvancedFeatures.loadFacebookIDs();
                    } else {
                        BiAds.showToast('error', 'Lỗi', result.detail || 'Không thể import');
                    }
                } catch (error) {
                    BiAds.showToast('error', 'Lỗi', error.message);
                }
            }
        });
    },
    
    deleteFacebookID: async (id) => {
        ModalConfirmation.showDanger({
            title: '🗑️ Xóa Facebook ID?',
            message: 'Bạn có chắc chắn muốn xóa ID này?',
            confirmText: 'Xóa',
            onConfirm: async () => {
                try {
                    const response = await fetch(`http://localhost:8000/api/facebook-ids/${id}`, {
                        method: 'DELETE'
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok && result.success) {
                        BiAds.showToast('success', 'Thành công', result.message);
                        await AdvancedFeatures.loadFacebookIDs();
                    } else {
                        BiAds.showToast('error', 'Lỗi', result.detail || 'Không thể xóa');
                    }
                } catch (error) {
                    BiAds.showToast('error', 'Lỗi', error.message);
                }
            }
        });
    },
    
    scanIDsFromGroup: () => BiAds.showToast('info', 'Chức năng đang phát triển', 'Quét ID từ nhóm sẽ được thêm sau'),
    validateAllIDs: () => BiAds.showToast('info', 'Chức năng đang phát triển', 'Kiểm tra tất cả ID sẽ được thêm sau'),
    exportIDs: () => BiAds.showToast('info', 'Chức năng đang phát triển', 'Xuất danh sách ID sẽ được thêm sau'),
    filterIDs: () => AdvancedFeatures.loadFacebookIDs(),
    searchIDs: () => AdvancedFeatures.loadFacebookIDs(),
    selectAllIDs: (checkbox) => {
        const checkboxes = document.querySelectorAll('.id-checkbox');
        checkboxes.forEach(cb => cb.checked = checkbox.checked);
    },
    detectCurrentIP: () => app.addLog('info', 'Phát hiện IP hiện tại'),
    addIPManually: () => app.addLog('info', 'Thêm IP thủ công'),
    addToWhitelist: () => app.addLog('info', 'Thêm vào whitelist'),
    importWhitelist: () => app.addLog('info', 'Import whitelist'),
    syncWhitelist: () => app.addLog('info', 'Đồng bộ whitelist'),
    searchWhitelist: () => app.addLog('info', 'Tìm kiếm whitelist'),
    filterWhitelist: () => app.addLog('info', 'Lọc whitelist'),
    selectAllWhitelist: (checkbox) => app.addLog('info', checkbox.checked ? 'Chọn tất cả' : 'Bỏ chọn tất cả'),
    // Posted Content Management Functions
    loadPostedContent: async function() {
        try {
            // Build query params from filters
            let queryParams = new URLSearchParams();
            
            const accountFilter = document.getElementById('postAccountFilter')?.value;
            if (accountFilter && accountFilter !== 'all') {
                queryParams.append('account_id', accountFilter);
            }
            
            const searchQuery = document.getElementById('postSearch')?.value.trim();
            if (searchQuery) {
                // Use search endpoint instead
                const response = await fetch(`http://localhost:8000/api/posted-content/search?query=${encodeURIComponent(searchQuery)}&limit=100`);
                const data = await response.json();
                this.renderPostedContentTable(data, searchQuery);
                await this.loadPostedContentStats();
                return;
            }
            
            const response = await fetch(`http://localhost:8000/api/posted-content/?${queryParams.toString()}&limit=100`);
            const data = await response.json();
            
            this.renderPostedContentTable(data);
            await this.loadPostedContentStats();
            
        } catch (error) {
            BiAds.showToast('error', 'Lỗi', `Không thể tải bài viết: ${error.message}`);
        }
    },
    
    renderPostedContentTable: function(posts, searchQuery = null) {
        const tbody = document.getElementById('postsTableBody');
        
        if (!posts || posts.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" style="text-align: center; padding: 40px; color: #888;">
                        <p>Chưa có bài viết nào</p>
                        <p>Nhấn "🔄 Đồng bộ bài viết" để tải dữ liệu</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = posts.map((post, index) => {
            // Display content with highlighting if search query exists
            const displayContent = searchQuery && post.highlighted_content 
                ? post.highlighted_content 
                : (post.content ? post.content.substring(0, 100) + (post.content.length > 100 ? '...' : '') : 'N/A');
            
            const accountName = post.account_info 
                ? (post.account_info.name || post.account_info.uid)
                : 'N/A';
            
            const postDate = new Date(post.posted_at || post.created_at);
            const dateStr = postDate.toLocaleDateString('vi-VN');
            const timeStr = postDate.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
            
            return `
                <tr>
                    <td><input type="checkbox" class="post-checkbox" data-id="${post.id}"></td>
                    <td>${index + 1}</td>
                    <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;" title="${post.content || ''}">
                        ${displayContent}
                    </td>
                    <td>${accountName}</td>
                    <td>
                        <div>${dateStr}</div>
                        <div style="font-size: 0.85em; color: #888;">${timeStr}</div>
                    </td>
                    <td>❤️ ${post.like_count || 0}</td>
                    <td>💬 ${post.comment_count || 0}</td>
                    <td>🔗 ${post.share_count || 0}</td>
                    <td>
                        <button class="btn-icon" onclick="AdvancedFeatures.editPost(${post.id})" title="Chỉnh sửa">✏️</button>
                        <button class="btn-icon" onclick="AdvancedFeatures.deletePost(${post.id})" title="Xóa">🗑️</button>
                    </td>
                </tr>
            `;
        }).join('');
    },
    
    loadPostedContentStats: async function() {
        try {
            const response = await fetch('http://localhost:8000/api/posted-content/stats');
            const stats = await response.json();
            
            document.getElementById('totalPosts').textContent = stats.total_posts || 0;
            document.getElementById('totalLikes').textContent = stats.total_likes?.toLocaleString() || 0;
            document.getElementById('totalComments').textContent = stats.total_comments?.toLocaleString() || 0;
            document.getElementById('totalShares').textContent = stats.total_shares?.toLocaleString() || 0;
            
        } catch (error) {
            console.error('Error loading posted content stats:', error);
        }
    },
    
    loadPostAccountFilter: async function() {
        try {
            const response = await fetch('http://localhost:8000/api/accounts?limit=1000');
            const accounts = await response.json();
            
            const filterSelect = document.getElementById('postAccountFilter');
            if (filterSelect) {
                filterSelect.innerHTML = '<option value="all">Tất cả tài khoản</option>' +
                    accounts.map(acc => 
                        `<option value="${acc.id}">${acc.name || acc.uid}</option>`
                    ).join('');
            }
        } catch (error) {
            console.error('Error loading accounts for filter:', error);
        }
    },
    
    editPost: async function(postId) {
        try {
            const response = await fetch(`http://localhost:8000/api/posted-content/${postId}`);
            const post = await response.json();
            
            ModalConfirmation.showInput({
                title: '✏️ Chỉnh sửa bài viết',
                html: `
                    <div class="input-group">
                        <label>Nội dung bài viết</label>
                        <textarea id="modalEditContent" rows="5" style="width: 100%; padding: 10px; background: #1a1a2e; border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; color: white;">${post.content || ''}</textarea>
                    </div>
                    <div class="input-group">
                        <label>Facebook Post ID</label>
                        <input type="text" id="modalEditPostId" value="${post.post_id || ''}" style="width: 100%;">
                    </div>
                    <div class="grid-3">
                        <div class="input-group">
                            <label>Likes</label>
                            <input type="number" id="modalEditLikes" value="${post.like_count || 0}" min="0">
                        </div>
                        <div class="input-group">
                            <label>Comments</label>
                            <input type="number" id="modalEditComments" value="${post.comment_count || 0}" min="0">
                        </div>
                        <div class="input-group">
                            <label>Shares</label>
                            <input type="number" id="modalEditShares" value="${post.share_count || 0}" min="0">
                        </div>
                    </div>
                `,
                confirmText: 'Cập nhật',
                onConfirm: async () => {
                    const updateData = {
                        content: document.getElementById('modalEditContent').value.trim() || null,
                        post_id: document.getElementById('modalEditPostId').value.trim() || null,
                        like_count: parseInt(document.getElementById('modalEditLikes').value) || 0,
                        comment_count: parseInt(document.getElementById('modalEditComments').value) || 0,
                        share_count: parseInt(document.getElementById('modalEditShares').value) || 0
                    };
                    
                    await this.updatePost(postId, updateData);
                }
            });
            
        } catch (error) {
            BiAds.showToast('error', 'Lỗi', error.message);
        }
    },
    
    updatePost: async function(postId, data) {
        try {
            const response = await fetch(`http://localhost:8000/api/posted-content/${postId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                BiAds.showToast('success', 'Thành công', result.message);
                await this.loadPostedContent();
            } else {
                BiAds.showToast('error', 'Lỗi', result.detail || 'Không thể cập nhật bài viết');
            }
            
        } catch (error) {
            BiAds.showToast('error', 'Lỗi', error.message);
        }
    },
    
    deletePost: async function(postId) {
        ModalConfirmation.showDanger({
            title: '🗑️ Xóa bài viết?',
            message: 'Bạn có chắc chắn muốn xóa bài viết này?',
            details: 'Hành động này không thể hoàn tác.',
            confirmText: 'Xóa',
            onConfirm: async () => {
                try {
                    const response = await fetch(`http://localhost:8000/api/posted-content/${postId}`, {
                        method: 'DELETE'
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok && result.success) {
                        BiAds.showToast('success', 'Thành công', result.message);
                        await this.loadPostedContent();
                    } else {
                        BiAds.showToast('error', 'Lỗi', result.detail || 'Không thể xóa bài viết');
                    }
                } catch (error) {
                    BiAds.showToast('error', 'Lỗi', error.message);
                }
            }
        });
    },
    
    syncPosts: () => BiAds.showToast('info', 'Chức năng đang phát triển', 'Đồng bộ bài viết từ Facebook sẽ được thêm sau'),
    exportPosts: () => BiAds.showToast('info', 'Chức năng đang phát triển', 'Xuất danh sách bài viết sẽ được thêm sau'),
    searchPosts: function() {
        this.loadPostedContent();
    },
    filterPosts: function() {
        this.loadPostedContent();
    },
    selectAllPosts: (checkbox) => {
        const checkboxes = document.querySelectorAll('.post-checkbox');
        checkboxes.forEach(cb => cb.checked = checkbox.checked);
    },
    
    // Bulk actions for posts (placeholders for future implementation)
    editSelectedPosts: () => BiAds.showToast('info', 'Chức năng đang phát triển', 'Chỉnh sửa hàng loạt sẽ được thêm sau'),
    hideSelectedPosts: () => BiAds.showToast('info', 'Chức năng đang phát triển', 'Ẩn bài viết hàng loạt sẽ được thêm sau'),
    boostSelectedPosts: () => BiAds.showToast('info', 'Chức năng đang phát triển', 'Tăng tương tác sẽ được thêm sau'),
    shareSelectedPosts: () => BiAds.showToast('info', 'Chức năng đang phát triển', 'Chia sẻ lại hàng loạt sẽ được thêm sau'),
    deleteSelectedPosts: () => {
        const selectedCheckboxes = document.querySelectorAll('.post-checkbox:checked');
        if (selectedCheckboxes.length === 0) {
            BiAds.showToast('warning', 'Chưa chọn', 'Vui lòng chọn ít nhất 1 bài viết');
            return;
        }
        
        const postIds = Array.from(selectedCheckboxes).map(cb => parseInt(cb.dataset.id));
        
        ModalConfirmation.showDanger({
            title: '🗑️ Xóa nhiều bài viết?',
            message: `Bạn có chắc chắn muốn xóa ${postIds.length} bài viết đã chọn?`,
            details: 'Hành động này không thể hoàn tác.',
            confirmText: 'Xóa tất cả',
            onConfirm: async () => {
                let successCount = 0;
                let errorCount = 0;
                
                for (const postId of postIds) {
                    try {
                        const response = await fetch(`http://localhost:8000/api/posted-content/${postId}`, {
                            method: 'DELETE'
                        });
                        
                        if (response.ok) {
                            successCount++;
                        } else {
                            errorCount++;
                        }
                    } catch (error) {
                        errorCount++;
                    }
                }
                
                if (successCount > 0) {
                    BiAds.showToast('success', 'Hoàn thành', `Đã xóa ${successCount} bài viết`);
                }
                if (errorCount > 0) {
                    BiAds.showToast('warning', 'Có lỗi', `${errorCount} bài viết không thể xóa`);
                }
                
                await AdvancedFeatures.loadPostedContent();
            }
        });
    },
    composeNewMessage: () => app.addLog('info', 'Soạn tin nhắn mới'),
    refreshMessages: () => app.addLog('info', 'Làm mới tin nhắn'),
    searchConversations: () => app.addLog('info', 'Tìm kiếm hội thoại'),
    sendMessage: () => app.addLog('info', 'Gửi tin nhắn'),
    saveAutoReplySettings: () => app.addLog('success', 'Đã lưu cài đặt tự động trả lời'),
    
    // ============================================
    // IP MANAGEMENT
    // ============================================
    
    renderIPManagementPage: async function(content) {
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    🌐 Quản lý IP thiết bị
                    <div style="float: right;">
                        <button class="btn-primary" onclick="AdvancedFeatures.detectCurrentIP()">
                            🔍 Phát hiện IP hiện tại
                        </button>
                        <button class="btn-secondary" onclick="AdvancedFeatures.showAddIPModal()">
                            ➕ Thêm IP
                        </button>
                        <button class="btn-success" onclick="AdvancedFeatures.refreshIPs()">
                            🔄 Làm mới
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="info-box">
                        <h4>ℹ️ Quản lý IP thiết bị</h4>
                        <p>Theo dõi và quản lý các địa chỉ IP đã sử dụng để truy cập tài khoản Facebook.</p>
                        <p><strong>Công dụng:</strong></p>
                        <ul style="margin-left: 20px; color: #888;">
                            <li>Phát hiện IP bất thường</li>
                            <li>Quản lý danh sách IP tin cậy/chặn</li>
                            <li>Theo dõi vị trí địa lý</li>
                            <li>Liên kết IP với tài khoản</li>
                        </ul>
                    </div>
                    
                    <div class="grid-3" style="margin-bottom: 20px;">
                        <div class="stat-card">
                            <h4 id="totalIPsCount">0</h4>
                            <p>Tổng IP</p>
                        </div>
                        <div class="stat-card">
                            <h4 id="trustedIPsCount">0</h4>
                            <p>IP tin cậy</p>
                        </div>
                        <div class="stat-card">
                            <h4 id="blockedIPsCount">0</h4>
                            <p>IP bị chặn</p>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <input type="text" 
                               id="searchIPInput" 
                               placeholder="Tìm kiếm theo IP, vị trí..." 
                               style="width: 300px; margin-right: 10px;"
                               onkeyup="if(event.key==='Enter') AdvancedFeatures.searchIPs()">
                        <button class="btn-secondary" onclick="AdvancedFeatures.searchIPs()">🔍 Tìm</button>
                        <select id="filterIPStatus" onchange="AdvancedFeatures.filterIPs()" style="margin-left: 10px;">
                            <option value="">Tất cả trạng thái</option>
                            <option value="trusted">Tin cậy</option>
                            <option value="blocked">Bị chặn</option>
                        </select>
                    </div>

                    <div id="ipsList">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>STT</th>
                                    <th>Địa chỉ IP</th>
                                    <th>Vị trí</th>
                                    <th>ISP</th>
                                    <th>Tài khoản</th>
                                    <th>Trạng thái</th>
                                    <th>Lần truy cập</th>
                                    <th>Hành động</th>
                                </tr>
                            </thead>
                            <tbody id="ipsTableBody">
                                <tr>
                                    <td colspan="8" style="text-align: center; padding: 40px; color: #888;">
                                        <p>Đang tải danh sách IP...</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        // Load data
        await this.loadIPManagement();
    },
    
    loadIPManagement: async function() {
        try {
            // Load stats
            const statsResponse = await fetch('http://localhost:8000/api/device-ips/stats');
            if (statsResponse.ok) {
                const stats = await statsResponse.json();
                document.getElementById('totalIPsCount').textContent = stats.total_ips;
                document.getElementById('trustedIPsCount').textContent = stats.trusted_ips;
                document.getElementById('blockedIPsCount').textContent = stats.blocked_ips;
            }
            
            // Load IPs list
            const searchValue = document.getElementById('searchIPInput')?.value || '';
            const statusFilter = document.getElementById('filterIPStatus')?.value || '';
            
            let url = 'http://localhost:8000/api/device-ips/?limit=100';
            if (searchValue) url += `&search=${encodeURIComponent(searchValue)}`;
            if (statusFilter === 'trusted') url += '&is_trusted=true';
            if (statusFilter === 'blocked') url += '&is_blocked=true';
            
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to load IPs');
            
            const ips = await response.json();
            this.renderIPsTable(ips);
            
        } catch (error) {
            console.error('Error loading IPs:', error);
            BiAds.showToast('error', 'Lỗi', 'Không thể tải danh sách IP');
        }
    },
    
    renderIPsTable: function(ips) {
        const tbody = document.getElementById('ipsTableBody');
        
        if (!ips || ips.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 40px; color: #888;">
                        <p>Chưa có IP nào được theo dõi</p>
                        <p>Nhấn "🔍 Phát hiện IP hiện tại" để bắt đầu</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = ips.map((ip, index) => {
            const statusBadge = ip.is_blocked 
                ? '<span class="badge badge-danger">Chặn</span>'
                : ip.is_trusted 
                    ? '<span class="badge badge-success">Tin cậy</span>'
                    : '<span class="badge badge-warning">Bình thường</span>';
            
            const accountInfo = ip.account_info 
                ? `${ip.account_info.name || ip.account_info.uid}`
                : '<span style="color: #888;">Chưa liên kết</span>';
            
            return `
                <tr>
                    <td>${index + 1}</td>
                    <td><strong>${ip.ip_address}</strong></td>
                    <td>${ip.location || 'N/A'}</td>
                    <td>${ip.isp || 'N/A'}</td>
                    <td>${accountInfo}</td>
                    <td>${statusBadge}</td>
                    <td>${ip.access_count} lần<br><small>${ip.last_used_at ? new Date(ip.last_used_at).toLocaleString('vi-VN') : 'N/A'}</small></td>
                    <td>
                        <button class="btn-sm btn-primary" onclick="AdvancedFeatures.editIP(${ip.id})">✏️</button>
                        <button class="btn-sm btn-danger" onclick="AdvancedFeatures.deleteIP(${ip.id})">🗑️</button>
                    </td>
                </tr>
            `;
        }).join('');
    },
    
    detectCurrentIP: async function() {
        try {
            BiAds.showToast('info', 'Đang phát hiện', 'Đang phát hiện IP hiện tại...');
            
            const response = await fetch('http://localhost:8000/api/device-ips/detect');
            if (!response.ok) throw new Error('Failed to detect IP');
            
            const result = await response.json();
            
            if (result.already_exists) {
                BiAds.showToast('info', 'IP đã tồn tại', `IP ${result.ip_address} đã có trong hệ thống`);
            } else {
                BiAds.showToast('success', 'Đã thêm', `IP ${result.ip_address} (${result.location}) đã được thêm vào hệ thống`);
            }
            
            await this.loadIPManagement();
            
        } catch (error) {
            console.error('Error detecting IP:', error);
            BiAds.showToast('error', 'Lỗi', 'Không thể phát hiện IP hiện tại');
        }
    },
    
    showAddIPModal: function() {
        ModalConfirmation.showInput({
            title: '➕ Thêm IP mới',
            message: 'Nhập thông tin địa chỉ IP muốn theo dõi:',
            inputs: [
                { id: 'ipAddress', label: 'Địa chỉ IP *', type: 'text', placeholder: '192.168.1.1', required: true },
                { id: 'location', label: 'Vị trí', type: 'text', placeholder: 'Hanoi, Vietnam' },
                { id: 'isp', label: 'Nhà cung cấp', type: 'text', placeholder: 'Viettel' },
                { id: 'notes', label: 'Ghi chú', type: 'textarea', placeholder: 'Ghi chú về IP này...' }
            ],
            confirmText: 'Thêm IP',
            onConfirm: async (values) => {
                try {
                    const response = await fetch('http://localhost:8000/api/device-ips/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            ip_address: values.ipAddress,
                            location: values.location || null,
                            isp: values.isp || null,
                            notes: values.notes || null,
                            is_trusted: true
                        })
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Failed to add IP');
                    }
                    
                    BiAds.showToast('success', 'Thành công', 'Đã thêm IP mới');
                    await AdvancedFeatures.loadIPManagement();
                    
                } catch (error) {
                    console.error('Error adding IP:', error);
                    BiAds.showToast('error', 'Lỗi', error.message);
                }
            }
        });
    },
    
    editIP: async function(ipId) {
        try {
            // Get IP details
            const response = await fetch(`http://localhost:8000/api/device-ips/${ipId}`);
            if (!response.ok) throw new Error('Failed to get IP details');
            
            const ip = await response.json();
            
            ModalConfirmation.showInput({
                title: '✏️ Chỉnh sửa IP',
                message: `Chỉnh sửa thông tin IP ${ip.ip_address}:`,
                inputs: [
                    { id: 'location', label: 'Vị trí', type: 'text', value: ip.location || '' },
                    { id: 'isp', label: 'Nhà cung cấp', type: 'text', value: ip.isp || '' },
                    { id: 'isTrusted', label: 'IP tin cậy', type: 'checkbox', checked: ip.is_trusted },
                    { id: 'isBlocked', label: 'Chặn IP', type: 'checkbox', checked: ip.is_blocked },
                    { id: 'notes', label: 'Ghi chú', type: 'textarea', value: ip.notes || '' }
                ],
                confirmText: 'Cập nhật',
                onConfirm: async (values) => {
                    try {
                        const updateResponse = await fetch(`http://localhost:8000/api/device-ips/${ipId}`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                location: values.location || null,
                                isp: values.isp || null,
                                is_trusted: values.isTrusted,
                                is_blocked: values.isBlocked,
                                notes: values.notes || null
                            })
                        });
                        
                        if (!updateResponse.ok) throw new Error('Failed to update IP');
                        
                        BiAds.showToast('success', 'Cập nhật', 'Đã cập nhật thông tin IP');
                        await AdvancedFeatures.loadIPManagement();
                        
                    } catch (error) {
                        console.error('Error updating IP:', error);
                        BiAds.showToast('error', 'Lỗi', 'Không thể cập nhật IP');
                    }
                }
            });
            
        } catch (error) {
            console.error('Error loading IP details:', error);
            BiAds.showToast('error', 'Lỗi', 'Không thể tải thông tin IP');
        }
    },
    
    deleteIP: function(ipId) {
        ModalConfirmation.showDanger({
            title: '🗑️ Xóa IP?',
            message: 'Bạn có chắc chắn muốn xóa IP này?',
            details: 'Hành động này không thể hoàn tác.',
            confirmText: 'Xóa',
            onConfirm: async () => {
                try {
                    const response = await fetch(`http://localhost:8000/api/device-ips/${ipId}`, {
                        method: 'DELETE'
                    });
                    
                    if (!response.ok) throw new Error('Failed to delete IP');
                    
                    BiAds.showToast('success', 'Đã xóa', 'IP đã được xóa khỏi hệ thống');
                    await AdvancedFeatures.loadIPManagement();
                    
                } catch (error) {
                    console.error('Error deleting IP:', error);
                    BiAds.showToast('error', 'Lỗi', 'Không thể xóa IP');
                }
            }
        });
    },
    
    refreshIPs: function() {
        this.loadIPManagement();
        BiAds.showToast('info', 'Làm mới', 'Đang tải lại danh sách IP...');
    },
    
    searchIPs: function() {
        this.loadIPManagement();
    },
    
    filterIPs: function() {
        this.loadIPManagement();
    },
    
    // ============================================
    // WHITELIST MANAGEMENT
    // ============================================
    
    renderWhitelistPage: async function(content) {
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    🛡️ Quản lý Whitelist
                    <div style="float: right;">
                        <button class="btn-primary" onclick="AdvancedFeatures.showAddWhitelistModal()">
                            ➕ Thêm vào Whitelist
                        </button>
                        <button class="btn-secondary" onclick="AdvancedFeatures.importWhitelist()">
                            📥 Import từ file
                        </button>
                        <button class="btn-success" onclick="AdvancedFeatures.refreshWhitelist()">
                            🔄 Làm mới
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="info-box">
                        <h4>ℹ️ Whitelist là gì?</h4>
                        <p>Whitelist là danh sách tài khoản được bảo vệ đặc biệt, không bị tương tác tiêu cực.</p>
                        <p><strong>Công dụng:</strong></p>
                        <ul style="margin-left: 20px; color: #888;">
                            <li>Bảo vệ tài khoản VIP, khách hàng quan trọng</li>
                            <li>Tự động chấp nhận kết bạn</li>
                            <li>Ưu tiên tương tác (like, comment)</li>
                            <li>Không bao giờ unfriend</li>
                        </ul>
                    </div>
                    
                    <div class="grid-3" style="margin-bottom: 20px;">
                        <div class="stat-card">
                            <h4 id="totalWhitelistCount">0</h4>
                            <p>Tổng whitelist</p>
                        </div>
                        <div class="stat-card">
                            <h4 id="activeWhitelistCount">0</h4>
                            <p>Đang hoạt động</p>
                        </div>
                        <div class="stat-card">
                            <h4 id="inactiveWhitelistCount">0</h4>
                            <p>Không hoạt động</p>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <input type="text" 
                               id="searchWhitelistInput" 
                               placeholder="Tìm kiếm theo UID, tên..." 
                               style="width: 300px; margin-right: 10px;"
                               onkeyup="if(event.key==='Enter') AdvancedFeatures.searchWhitelist()">
                        <button class="btn-secondary" onclick="AdvancedFeatures.searchWhitelist()">🔍 Tìm</button>
                        <select id="filterWhitelistStatus" onchange="AdvancedFeatures.filterWhitelist()" style="margin-left: 10px;">
                            <option value="">Tất cả trạng thái</option>
                            <option value="active">Hoạt động</option>
                            <option value="inactive">Không hoạt động</option>
                        </select>
                    </div>

                    <div id="whitelistList">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>STT</th>
                                    <th>UID</th>
                                    <th>Tên</th>
                                    <th>Tên người dùng</th>
                                    <th>Trạng thái</th>
                                    <th>Lý do</th>
                                    <th>Ngày thêm</th>
                                    <th>Hành động</th>
                                </tr>
                            </thead>
                            <tbody id="whitelistTableBody">
                                <tr>
                                    <td colspan="8" style="text-align: center; padding: 40px; color: #888;">
                                        <p>Đang tải danh sách whitelist...</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        // Load data
        await this.loadWhitelist();
    },
    
    loadWhitelist: async function() {
        try {
            // Load stats
            const statsResponse = await fetch('http://localhost:8000/api/whitelist/stats');
            if (statsResponse.ok) {
                const stats = await statsResponse.json();
                document.getElementById('totalWhitelistCount').textContent = stats.total_accounts;
                document.getElementById('activeWhitelistCount').textContent = stats.active_accounts;
                document.getElementById('inactiveWhitelistCount').textContent = stats.inactive_accounts;
            }
            
            // Load whitelist
            const searchValue = document.getElementById('searchWhitelistInput')?.value || '';
            const statusFilter = document.getElementById('filterWhitelistStatus')?.value || '';
            
            let url = 'http://localhost:8000/api/whitelist/?limit=100';
            if (searchValue) url += `&search=${encodeURIComponent(searchValue)}`;
            if (statusFilter) url += `&is_active=${statusFilter === 'active'}`;
            
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to load whitelist');
            
            const whitelist = await response.json();
            this.renderWhitelistTable(whitelist);
            
        } catch (error) {
            console.error('Error loading whitelist:', error);
            BiAds.showToast('error', 'Lỗi', 'Không thể tải danh sách whitelist');
        }
    },
    
    renderWhitelistTable: function(whitelist) {
        const tbody = document.getElementById('whitelistTableBody');
        
        if (!whitelist || whitelist.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 40px; color: #888;">
                        <p>Chưa có tài khoản nào trong whitelist</p>
                        <p>Nhấn "➕ Thêm vào Whitelist" để bắt đầu</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = whitelist.map((item, index) => {
            const statusBadge = item.is_active 
                ? '<span class="badge badge-success">Hoạt động</span>'
                : '<span class="badge badge-secondary">Không hoạt động</span>';
            
            return `
                <tr>
                    <td>${index + 1}</td>
                    <td><strong>${item.uid}</strong></td>
                    <td>${item.name || '<span style="color: #888;">N/A</span>'}</td>
                    <td>${item.username || '<span style="color: #888;">N/A</span>'}</td>
                    <td>${statusBadge}</td>
                    <td><small>${item.reason || '<span style="color: #888;">Không có</span>'}</small></td>
                    <td><small>${new Date(item.created_at).toLocaleDateString('vi-VN')}</small></td>
                    <td>
                        <button class="btn-sm btn-primary" onclick="AdvancedFeatures.editWhitelist(${item.id})">✏️</button>
                        <button class="btn-sm btn-danger" onclick="AdvancedFeatures.deleteWhitelist(${item.id})">🗑️</button>
                    </td>
                </tr>
            `;
        }).join('');
    },
    
    showAddWhitelistModal: function() {
        ModalConfirmation.showInput({
            title: '➕ Thêm vào Whitelist',
            message: 'Nhập thông tin tài khoản muốn bảo vệ:',
            inputs: [
                { id: 'uid', label: 'UID *', type: 'text', placeholder: '100012345678901', required: true },
                { id: 'name', label: 'Tên', type: 'text', placeholder: 'Nguyễn Văn A' },
                { id: 'username', label: 'Username', type: 'text', placeholder: 'nguyenvana' },
                { id: 'reason', label: 'Lý do', type: 'textarea', placeholder: 'VIP, Khách hàng quan trọng...' }
            ],
            confirmText: 'Thêm vào Whitelist',
            onConfirm: async (values) => {
                try {
                    const response = await fetch('http://localhost:8000/api/whitelist/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            uid: values.uid,
                            name: values.name || null,
                            username: values.username || null,
                            reason: values.reason || null,
                            is_active: true
                        })
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Failed to add to whitelist');
                    }
                    
                    BiAds.showToast('success', 'Thành công', 'Đã thêm vào whitelist');
                    await AdvancedFeatures.loadWhitelist();
                    
                } catch (error) {
                    console.error('Error adding to whitelist:', error);
                    BiAds.showToast('error', 'Lỗi', error.message);
                }
            }
        });
    },
    
    importWhitelist: function() {
        ModalConfirmation.showInput({
            title: '📥 Import Whitelist',
            message: 'Chọn file chứa danh sách UID (mỗi UID một dòng):',
            inputs: [
                { id: 'file', label: 'Chọn file', type: 'file', accept: '.txt' },
                { id: 'reason', label: 'Lý do chung', type: 'textarea', placeholder: 'Lý do thêm vào whitelist...' }
            ],
            confirmText: 'Import',
            onConfirm: async (values) => {
                try {
                    const fileInput = document.querySelector('input[type="file"]');
                    if (!fileInput.files.length) {
                        throw new Error('Vui lòng chọn file');
                    }
                    
                    const formData = new FormData();
                    formData.append('file', fileInput.files[0]);
                    if (values.reason) {
                        formData.append('reason', values.reason);
                    }
                    
                    const response = await fetch('http://localhost:8000/api/whitelist/import', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Failed to import');
                    }
                    
                    const result = await response.json();
                    BiAds.showToast('success', 'Hoàn thành', 
                        `Đã import ${result.imported} UID, bỏ qua ${result.skipped} trùng lặp`);
                    await AdvancedFeatures.loadWhitelist();
                    
                } catch (error) {
                    console.error('Error importing whitelist:', error);
                    BiAds.showToast('error', 'Lỗi', error.message);
                }
            }
        });
    },
    
    editWhitelist: async function(whitelistId) {
        try {
            // Get whitelist details (need to implement GET endpoint)
            const response = await fetch(`http://localhost:8000/api/whitelist/${whitelistId}`);
            if (!response.ok) throw new Error('Failed to get whitelist details');
            
            const item = await response.json();
            
            ModalConfirmation.showInput({
                title: '✏️ Chỉnh sửa Whitelist',
                message: `Chỉnh sửa thông tin ${item.uid}:`,
                inputs: [
                    { id: 'name', label: 'Tên', type: 'text', value: item.name || '' },
                    { id: 'username', label: 'Username', type: 'text', value: item.username || '' },
                    { id: 'reason', label: 'Lý do', type: 'textarea', value: item.reason || '' },
                    { id: 'isActive', label: 'Hoạt động', type: 'checkbox', checked: item.is_active }
                ],
                confirmText: 'Cập nhật',
                onConfirm: async (values) => {
                    try {
                        const updateResponse = await fetch(`http://localhost:8000/api/whitelist/${whitelistId}`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                name: values.name || null,
                                username: values.username || null,
                                reason: values.reason || null,
                                is_active: values.isActive
                            })
                        });
                        
                        if (!updateResponse.ok) throw new Error('Failed to update whitelist');
                        
                        BiAds.showToast('success', 'Cập nhật', 'Đã cập nhật thông tin whitelist');
                        await AdvancedFeatures.loadWhitelist();
                        
                    } catch (error) {
                        console.error('Error updating whitelist:', error);
                        BiAds.showToast('error', 'Lỗi', 'Không thể cập nhật whitelist');
                    }
                }
            });
            
        } catch (error) {
            console.error('Error loading whitelist details:', error);
            BiAds.showToast('error', 'Lỗi', 'Không thể tải thông tin whitelist');
        }
    },
    
    deleteWhitelist: function(whitelistId) {
        ModalConfirmation.showDanger({
            title: '🗑️ Xóa khỏi Whitelist?',
            message: 'Bạn có chắc chắn muốn xóa tài khoản này khỏi whitelist?',
            details: 'Tài khoản sẽ không còn được bảo vệ đặc biệt.',
            confirmText: 'Xóa',
            onConfirm: async () => {
                try {
                    const response = await fetch(`http://localhost:8000/api/whitelist/${whitelistId}`, {
                        method: 'DELETE'
                    });
                    
                    if (!response.ok) throw new Error('Failed to delete from whitelist');
                    
                    BiAds.showToast('success', 'Đã xóa', 'Tài khoản đã được xóa khỏi whitelist');
                    await AdvancedFeatures.loadWhitelist();
                    
                } catch (error) {
                    console.error('Error deleting from whitelist:', error);
                    BiAds.showToast('error', 'Lỗi', 'Không thể xóa khỏi whitelist');
                }
            }
        });
    },
    
    refreshWhitelist: function() {
        this.loadWhitelist();
        BiAds.showToast('info', 'Làm mới', 'Đang tải lại danh sách whitelist...');
    },
    
    searchWhitelist: function() {
        this.loadWhitelist();
    },
    
    filterWhitelist: function() {
        this.loadWhitelist();
    }
};

// Expose to global scope
window.AdvancedFeatures = AdvancedFeatures;
