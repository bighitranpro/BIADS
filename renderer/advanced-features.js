// Bi Ads Multi Tool PRO v3.0 - Advanced Features
// Nâng cấp các chức năng quản lý

const AdvancedFeatures = {
    // Quản lý tài khoản phụ
    renderSubAccountsPage: function(content) {
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

    // Placeholder functions for actions
    showAddSubAccountModal: () => app.addLog('info', 'Chức năng thêm tài khoản phụ'),
    importSubAccounts: () => app.addLog('info', 'Import tài khoản phụ'),
    addIDsManually: () => app.addLog('info', 'Thêm ID thủ công'),
    importIDsFromFile: () => app.addLog('info', 'Import ID từ file'),
    scanIDsFromGroup: () => app.addLog('info', 'Quét ID từ nhóm'),
    validateAllIDs: () => app.addLog('info', 'Kiểm tra tất cả ID'),
    exportIDs: () => app.addLog('info', 'Xuất danh sách ID'),
    filterIDs: () => app.addLog('info', 'Lọc ID'),
    searchIDs: () => app.addLog('info', 'Tìm kiếm ID'),
    selectAllIDs: (checkbox) => app.addLog('info', checkbox.checked ? 'Chọn tất cả' : 'Bỏ chọn tất cả'),
    detectCurrentIP: () => app.addLog('info', 'Phát hiện IP hiện tại'),
    addIPManually: () => app.addLog('info', 'Thêm IP thủ công'),
    addToWhitelist: () => app.addLog('info', 'Thêm vào whitelist'),
    importWhitelist: () => app.addLog('info', 'Import whitelist'),
    syncWhitelist: () => app.addLog('info', 'Đồng bộ whitelist'),
    searchWhitelist: () => app.addLog('info', 'Tìm kiếm whitelist'),
    filterWhitelist: () => app.addLog('info', 'Lọc whitelist'),
    selectAllWhitelist: (checkbox) => app.addLog('info', checkbox.checked ? 'Chọn tất cả' : 'Bỏ chọn tất cả'),
    syncPosts: () => app.addLog('info', 'Đồng bộ bài viết'),
    exportPosts: () => app.addLog('info', 'Xuất bài viết'),
    searchPosts: () => app.addLog('info', 'Tìm kiếm bài viết'),
    filterPosts: () => app.addLog('info', 'Lọc bài viết'),
    selectAllPosts: (checkbox) => app.addLog('info', checkbox.checked ? 'Chọn tất cả' : 'Bỏ chọn tất cả'),
    composeNewMessage: () => app.addLog('info', 'Soạn tin nhắn mới'),
    refreshMessages: () => app.addLog('info', 'Làm mới tin nhắn'),
    searchConversations: () => app.addLog('info', 'Tìm kiếm hội thoại'),
    sendMessage: () => app.addLog('info', 'Gửi tin nhắn'),
    saveAutoReplySettings: () => app.addLog('success', 'Đã lưu cài đặt tự động trả lời')
};

// Expose to global scope
window.AdvancedFeatures = AdvancedFeatures;
