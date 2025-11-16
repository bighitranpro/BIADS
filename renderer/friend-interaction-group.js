// Friend, Interaction, and Group Management Frontend
// Extends AdvancedFeatures with additional functionality

// Friend Management Functions
AdvancedFeatures.renderFriendManagementPage = async function(content) {
    content.innerHTML = `
        <div class="card">
            <div class="card-header">
                👥 Quản lý bạn bè
                <div style="float: right;">
                    <button class="btn-primary" onclick="AdvancedFeatures.showAddFriendModal()">➕ Kết bạn</button>
                    <button class="btn-secondary" onclick="AdvancedFeatures.showBulkAddFriendsModal()">📥 Hàng loạt</button>
                    <button class="btn-success" onclick="AdvancedFeatures.refreshFriends()">🔄 Làm mới</button>
                </div>
            </div>
            <div class="card-body">
                <div class="grid-4" style="margin: 20px 0;">
                    <div class="stat-card"><h4 id="totalFriendsCount">0</h4><p>Tổng bạn bè</p></div>
                    <div class="stat-card"><h4 id="friendsAddedTodayCount">0</h4><p>Kết bạn hôm nay</p></div>
                    <div class="stat-card"><h4 id="friendsAddedWeekCount">0</h4><p>Tuần này</p></div>
                    <div class="stat-card"><h4 id="pendingRequestsCount">0</h4><p>Chờ xử lý</p></div>
                </div>
                <table class="data-table">
                    <thead><tr><th>STT</th><th>UID</th><th>Tên</th><th>Trạng thái</th><th>Hành động</th></tr></thead>
                    <tbody id="friendsTableBody"><tr><td colspan="5" style="text-align: center; padding: 40px;">Đang tải...</td></tr></tbody>
                </table>
            </div>
        </div>
    `;
    await this.loadFriends();
};

AdvancedFeatures.loadFriends = async function() {
    try {
        const statsResponse = await fetch('http://localhost:8000/api/friends/stats');
        if (statsResponse.ok) {
            const stats = await statsResponse.json();
            document.getElementById('totalFriendsCount').textContent = stats.total_friends;
            document.getElementById('friendsAddedTodayCount').textContent = stats.friends_added_today;
            document.getElementById('friendsAddedWeekCount').textContent = stats.friends_added_this_week;
            document.getElementById('pendingRequestsCount').textContent = stats.pending_requests_sent;
        }
        
        const response = await fetch('http://localhost:8000/api/friends/list?limit=100');
        if (!response.ok) throw new Error('Failed');
        
        const friends = await response.json();
        const tbody = document.getElementById('friendsTableBody');
        if (!friends || friends.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px;">Chưa có dữ liệu</td></tr>';
            return;
        }
        
        tbody.innerHTML = friends.map((f, i) => `
            <tr>
                <td>${i + 1}</td>
                <td><strong>${f.uid}</strong></td>
                <td>${f.name || 'N/A'}</td>
                <td>${f.is_friend ? '<span class="badge badge-success">Bạn bè</span>' : '<span class="badge badge-secondary">Chưa kết bạn</span>'}</td>
                <td>
                    ${!f.is_friend ? `<button class="btn-sm btn-primary" onclick="AdvancedFeatures.quickAddFriend('${f.uid}')">➕</button>` : ''}
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
        BiAds.showToast('error', 'Lỗi', 'Không thể tải danh sách');
    }
};

AdvancedFeatures.showAddFriendModal = function() {
    ModalConfirmation.showInput({
        title: '➕ Kết bạn',
        message: 'Nhập UID:',
        inputs: [{ id: 'targetUid', label: 'UID *', type: 'text', placeholder: '100012345678901', required: true }],
        confirmText: 'Kết bạn',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('Không có tài khoản');
                
                const response = await fetch('http://localhost:8000/api/friends/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ account_id: list[0].id, target_uid: values.targetUid })
                });
                
                if (!response.ok) throw new Error('Failed');
                BiAds.showToast('success', 'Thành công', 'Đã gửi lời mời');
                await AdvancedFeatures.loadFriends();
            } catch (error) {
                BiAds.showToast('error', 'Lỗi', error.message);
            }
        }
    });
};

AdvancedFeatures.showBulkAddFriendsModal = function() {
    ModalConfirmation.showInput({
        title: '📥 Kết bạn hàng loạt',
        message: 'Nhập danh sách UID (mỗi dòng một UID):',
        inputs: [{ id: 'uidList', label: 'UIDs', type: 'textarea', placeholder: '100012345678901\n100012345678902', required: true }],
        confirmText: 'Bắt đầu',
        onConfirm: async (values) => {
            try {
                const uids = values.uidList.split('\n').map(u => u.trim()).filter(u => u);
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('Không có tài khoản');
                
                const response = await fetch('http://localhost:8000/api/friends/add-bulk', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ account_id: list[0].id, target_uids: uids, delay_min: 5, delay_max: 15 })
                });
                
                if (!response.ok) throw new Error('Failed');
                BiAds.showToast('success', 'Thành công', `Task kết bạn ${uids.length} người`);
            } catch (error) {
                BiAds.showToast('error', 'Lỗi', error.message);
            }
        }
    });
};

AdvancedFeatures.quickAddFriend = async function(uid) {
    try {
        const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
        const list = await accounts.json();
        const response = await fetch('http://localhost:8000/api/friends/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ account_id: list[0].id, target_uid: uid })
        });
        if (!response.ok) throw new Error('Failed');
        BiAds.showToast('success', 'Thành công', 'Đã gửi lời mời');
        await this.loadFriends();
    } catch (error) {
        BiAds.showToast('error', 'Lỗi', error.message);
    }
};

AdvancedFeatures.refreshFriends = function() {
    this.loadFriends();
    BiAds.showToast('info', 'Làm mới', 'Đang tải lại...');
};

// Account Interactions Functions
AdvancedFeatures.renderInteractionsPage = async function(content) {
    content.innerHTML = `
        <div class="card">
            <div class="card-header">
                💬 Tương tác tài khoản
                <div style="float: right;">
                    <button class="btn-primary" onclick="AdvancedFeatures.showConfigAutoLike()">⚙️ Auto-Like</button>
                    <button class="btn-secondary" onclick="AdvancedFeatures.showConfigAutoComment()">⚙️ Auto-Comment</button>
                    <button class="btn-success" onclick="AdvancedFeatures.refreshInteractions()">🔄 Làm mới</button>
                </div>
            </div>
            <div class="card-body">
                <div class="grid-4" style="margin: 20px 0;">
                    <div class="stat-card"><h4 id="totalLikesCount">0</h4><p>Likes đã cho</p></div>
                    <div class="stat-card"><h4 id="totalCommentsCount">0</h4><p>Comments đã cho</p></div>
                    <div class="stat-card"><h4 id="totalSharesCount">0</h4><p>Shares đã cho</p></div>
                    <div class="stat-card"><h4 id="engagementRateValue">0%</h4><p>Tỷ lệ tương tác</p></div>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <div class="card-header">🎯 Thao tác nhanh</div>
                    <div class="card-body">
                        <div class="input-group">
                            <label>URL bài viết</label>
                            <input type="text" id="postUrlInput" placeholder="https://facebook.com/...">
                        </div>
                        <div style="display: flex; gap: 10px; margin-top: 10px;">
                            <button class="btn-primary" onclick="AdvancedFeatures.quickLikePost()">👍 Like</button>
                            <button class="btn-secondary" onclick="AdvancedFeatures.quickCommentPost()">💬 Comment</button>
                            <button class="btn-success" onclick="AdvancedFeatures.quickSharePost()">🔄 Share</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    await this.loadInteractions();
};

AdvancedFeatures.loadInteractions = async function() {
    try {
        const response = await fetch('http://localhost:8000/api/interactions/stats');
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('totalLikesCount').textContent = stats.total_likes_given;
            document.getElementById('totalCommentsCount').textContent = stats.total_comments_given;
            document.getElementById('totalSharesCount').textContent = stats.total_shares_given;
            document.getElementById('engagementRateValue').textContent = stats.engagement_rate.toFixed(1) + '%';
        }
    } catch (error) {
        console.error('Error:', error);
    }
};

AdvancedFeatures.quickLikePost = async function() {
    const url = document.getElementById('postUrlInput').value;
    if (!url) { BiAds.showToast('warning', 'Thiếu URL', 'Vui lòng nhập URL bài viết'); return; }
    try {
        const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
        const list = await accounts.json();
        const response = await fetch('http://localhost:8000/api/interactions/like', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ account_id: list[0].id, action_type: 'like', target_post_id: url })
        });
        if (!response.ok) throw new Error('Failed');
        BiAds.showToast('success', 'Thành công', 'Đã like bài viết');
    } catch (error) {
        BiAds.showToast('error', 'Lỗi', error.message);
    }
};

AdvancedFeatures.quickCommentPost = function() {
    ModalConfirmation.showInput({
        title: '💬 Comment',
        message: 'Nhập nội dung comment:',
        inputs: [{ id: 'commentText', label: 'Comment', type: 'textarea', placeholder: 'Nội dung comment...', required: true }],
        confirmText: 'Gửi',
        onConfirm: async (values) => {
            try {
                const url = document.getElementById('postUrlInput').value;
                if (!url) throw new Error('Thiếu URL');
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                const response = await fetch('http://localhost:8000/api/interactions/comment', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ account_id: list[0].id, action_type: 'comment', target_post_id: url, content: values.commentText })
                });
                if (!response.ok) throw new Error('Failed');
                BiAds.showToast('success', 'Thành công', 'Đã comment');
            } catch (error) {
                BiAds.showToast('error', 'Lỗi', error.message);
            }
        }
    });
};

AdvancedFeatures.quickSharePost = async function() {
    const url = document.getElementById('postUrlInput').value;
    if (!url) { BiAds.showToast('warning', 'Thiếu URL', 'Vui lòng nhập URL'); return; }
    try {
        const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
        const list = await accounts.json();
        const response = await fetch('http://localhost:8000/api/interactions/share', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ account_id: list[0].id, action_type: 'share', target_post_id: url })
        });
        if (!response.ok) throw new Error('Failed');
        BiAds.showToast('success', 'Thành công', 'Đã share');
    } catch (error) {
        BiAds.showToast('error', 'Lỗi', error.message);
    }
};

AdvancedFeatures.showConfigAutoLike = function() {
    ModalConfirmation.showInput({
        title: '⚙️ Cấu hình Auto-Like',
        message: 'Thiết lập tự động like bài viết:',
        inputs: [
            { id: 'enabled', label: 'Bật Auto-Like', type: 'checkbox', checked: true },
            { id: 'targetPerDay', label: 'Số bài/ngày', type: 'number', value: '50' }
        ],
        confirmText: 'Lưu',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                const response = await fetch('http://localhost:8000/api/interactions/auto-like/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        enabled: values.enabled,
                        target_posts_per_day: parseInt(values.targetPerDay) || 50
                    })
                });
                if (!response.ok) throw new Error('Failed');
                BiAds.showToast('success', 'Đã lưu', 'Cấu hình auto-like đã được lưu');
            } catch (error) {
                BiAds.showToast('error', 'Lỗi', error.message);
            }
        }
    });
};

AdvancedFeatures.showConfigAutoComment = function() {
    BiAds.showToast('info', 'Chức năng', 'Auto-comment đang được phát triển');
};

AdvancedFeatures.refreshInteractions = function() {
    this.loadInteractions();
    BiAds.showToast('info', 'Làm mới', 'Đang tải lại...');
};

// Group Management Functions
AdvancedFeatures.renderGroupManagementPage = async function(content) {
    content.innerHTML = `
        <div class="card">
            <div class="card-header">
                🏘️ Quản lý nhóm
                <div style="float: right;">
                    <button class="btn-primary" onclick="AdvancedFeatures.showJoinGroupModal()">➕ Tham gia nhóm</button>
                    <button class="btn-secondary" onclick="AdvancedFeatures.showPostToGroupModal()">📝 Đăng bài</button>
                    <button class="btn-success" onclick="AdvancedFeatures.refreshGroups()">🔄 Làm mới</button>
                </div>
            </div>
            <div class="card-body">
                <div class="grid-4" style="margin: 20px 0;">
                    <div class="stat-card"><h4 id="totalGroupsCount">0</h4><p>Nhóm đã tham gia</p></div>
                    <div class="stat-card"><h4 id="groupPostsTodayCount">0</h4><p>Bài đăng hôm nay</p></div>
                    <div class="stat-card"><h4 id="membersScannedCount">0</h4><p>Thành viên quét</p></div>
                    <div class="stat-card"><h4 id="activeGroupTasksCount">0</h4><p>Tasks đang chạy</p></div>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <div class="card-header">🎯 Thao tác nhanh</div>
                    <div class="card-body">
                        <div class="input-group">
                            <label>Group ID</label>
                            <input type="text" id="groupIdInput" placeholder="123456789">
                        </div>
                        <div style="display: flex; gap: 10px; margin-top: 10px;">
                            <button class="btn-primary" onclick="AdvancedFeatures.quickJoinGroup()">➕ Tham gia</button>
                            <button class="btn-secondary" onclick="AdvancedFeatures.quickLeaveGroup()">❌ Rời nhóm</button>
                            <button class="btn-success" onclick="AdvancedFeatures.quickScanMembers()">🔍 Quét thành viên</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    await this.loadGroups();
};

AdvancedFeatures.loadGroups = async function() {
    try {
        const response = await fetch('http://localhost:8000/api/groups/stats');
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('totalGroupsCount').textContent = stats.total_groups_joined;
            document.getElementById('groupPostsTodayCount').textContent = stats.posts_in_groups_today;
            document.getElementById('membersScannedCount').textContent = stats.members_scanned;
            document.getElementById('activeGroupTasksCount').textContent = stats.active_group_tasks;
        }
    } catch (error) {
        console.error('Error:', error);
    }
};

AdvancedFeatures.showJoinGroupModal = function() {
    ModalConfirmation.showInput({
        title: '➕ Tham gia nhóm',
        message: 'Nhập Group ID:',
        inputs: [{ id: 'groupId', label: 'Group ID *', type: 'text', placeholder: '123456789', required: true }],
        confirmText: 'Tham gia',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                const response = await fetch('http://localhost:8000/api/groups/join', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ account_id: list[0].id, group_id: values.groupId })
                });
                if (!response.ok) throw new Error('Failed');
                BiAds.showToast('success', 'Thành công', 'Đã tạo task tham gia nhóm');
            } catch (error) {
                BiAds.showToast('error', 'Lỗi', error.message);
            }
        }
    });
};

AdvancedFeatures.showPostToGroupModal = function() {
    ModalConfirmation.showInput({
        title: '📝 Đăng bài vào nhóm',
        message: 'Nhập thông tin:',
        inputs: [
            { id: 'groupId', label: 'Group ID *', type: 'text', placeholder: '123456789', required: true },
            { id: 'content', label: 'Nội dung *', type: 'textarea', placeholder: 'Nội dung bài viết...', required: true }
        ],
        confirmText: 'Đăng bài',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                const response = await fetch('http://localhost:8000/api/groups/post', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        group_id: values.groupId,
                        content: values.content,
                        image_urls: []
                    })
                });
                if (!response.ok) throw new Error('Failed');
                BiAds.showToast('success', 'Thành công', 'Đã tạo task đăng bài');
            } catch (error) {
                BiAds.showToast('error', 'Lỗi', error.message);
            }
        }
    });
};

AdvancedFeatures.quickJoinGroup = async function() {
    const groupId = document.getElementById('groupIdInput').value;
    if (!groupId) { BiAds.showToast('warning', 'Thiếu Group ID', 'Vui lòng nhập Group ID'); return; }
    try {
        const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
        const list = await accounts.json();
        const response = await fetch('http://localhost:8000/api/groups/join', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ account_id: list[0].id, group_id: groupId })
        });
        if (!response.ok) throw new Error('Failed');
        BiAds.showToast('success', 'Thành công', 'Đã tạo task tham gia');
    } catch (error) {
        BiAds.showToast('error', 'Lỗi', error.message);
    }
};

AdvancedFeatures.quickLeaveGroup = async function() {
    const groupId = document.getElementById('groupIdInput').value;
    if (!groupId) { BiAds.showToast('warning', 'Thiếu Group ID', 'Vui lòng nhập Group ID'); return; }
    ModalConfirmation.showDanger({
        title: '❌ Rời nhóm?',
        message: 'Bạn có chắc muốn rời khỏi nhóm này?',
        confirmText: 'Rời nhóm',
        onConfirm: async () => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                const response = await fetch('http://localhost:8000/api/groups/leave', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ account_id: list[0].id, group_id: groupId })
                });
                if (!response.ok) throw new Error('Failed');
                BiAds.showToast('success', 'Thành công', 'Đã rời nhóm');
            } catch (error) {
                BiAds.showToast('error', 'Lỗi', error.message);
            }
        }
    });
};

AdvancedFeatures.quickScanMembers = async function() {
    const groupId = document.getElementById('groupIdInput').value;
    if (!groupId) { BiAds.showToast('warning', 'Thiếu Group ID', 'Vui lòng nhập Group ID'); return; }
    try {
        const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
        const list = await accounts.json();
        const response = await fetch('http://localhost:8000/api/groups/scan-members', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ account_id: list[0].id, group_id: groupId, limit: 100, save_to_db: true })
        });
        if (!response.ok) throw new Error('Failed');
        BiAds.showToast('success', 'Thành công', 'Đã tạo task quét thành viên');
    } catch (error) {
        BiAds.showToast('error', 'Lỗi', error.message);
    }
};

AdvancedFeatures.refreshGroups = function() {
    this.loadGroups();
    BiAds.showToast('info', 'Làm mới', 'Đang tải lại...');
};

console.log('✅ Friend, Interaction, Group Management loaded');
