// Sidebar Features Frontend
// Handles Fanpage, Scanning, Auto Actions, and Misc Features

window.SidebarFeatures = window.SidebarFeatures || {};

// ============================================
// FANPAGE MANAGEMENT
// ============================================

SidebarFeatures.renderFanpagePage = function(content, subAction) {
    content.innerHTML = `
        <div class="card">
            <div class="card-header">
                📄 Fanpage Management
                <div style="float: right;">
                    <button class="btn-primary" onclick="SidebarFeatures.showAddFanpageModal()">➕ Add Fanpage</button>
                    <button class="btn-success" onclick="SidebarFeatures.loadFanpages()">🔄 Refresh</button>
                </div>
            </div>
            <div class="card-body">
                <div class="grid-4" style="margin: 20px 0;">
                    <div class="stat-card"><h4 id="totalFanpagesCount">0</h4><p>Total Fanpages</p></div>
                    <div class="stat-card"><h4 id="activeFanpagesCount">0</h4><p>Active</p></div>
                    <div class="stat-card"><h4 id="fanpagePostsTodayCount">0</h4><p>Posts Today</p></div>
                    <div class="stat-card"><h4 id="fanpageInteractionsCount">0</h4><p>Interactions</p></div>
                </div>
                
                <div class="action-buttons" style="margin: 20px 0; display: flex; gap: 10px; flex-wrap: wrap;">
                    <button class="btn-primary" onclick="SidebarFeatures.showPostToFanpage()">📝 Post to Fanpage</button>
                    <button class="btn-secondary" onclick="SidebarFeatures.showAutoLikeFanpage()">👍 Auto-Like Config</button>
                    <button class="btn-success" onclick="SidebarFeatures.showInviteLikes()">📩 Invite Friends</button>
                    <button class="btn-info" onclick="SidebarFeatures.showInteractFanpage()">💬 Interact</button>
                    <button class="btn-warning" onclick="SidebarFeatures.showEditFanpage()">✏️ Edit Fanpage</button>
                </div>
                
                <div id="fanpageContent">Loading...</div>
            </div>
        </div>
    `;
    
    this.loadFanpages();
    
    // Auto-open specific action if provided
    if (subAction) {
        setTimeout(() => {
            switch(subAction) {
                case 'post': SidebarFeatures.showPostToFanpage(); break;
                case 'auto-like': SidebarFeatures.showAutoLikeFanpage(); break;
                case 'invite-likes': SidebarFeatures.showInviteLikes(); break;
                case 'interact': SidebarFeatures.showInteractFanpage(); break;
                case 'edit': SidebarFeatures.showEditFanpage(); break;
            }
        }, 300);
    }
};

SidebarFeatures.loadFanpages = async function() {
    try {
        const response = await fetch('http://localhost:8000/api/fanpages/stats');
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('totalFanpagesCount').textContent = stats.total_pages || 0;
            document.getElementById('activeFanpagesCount').textContent = stats.active_pages || 0;
            document.getElementById('fanpagePostsTodayCount').textContent = stats.total_posts_today || 0;
            document.getElementById('fanpageInteractionsCount').textContent = stats.total_interactions_today || 0;
        }
        
        document.getElementById('fanpageContent').innerHTML = '<p style="text-align: center; padding: 40px;">No fanpages added yet. Click "Add Fanpage" to get started.</p>';
    } catch (error) {
        console.error('Error:', error);
        BiAds.showToast('error', 'Error', 'Failed to load fanpages');
    }
};

SidebarFeatures.showAddFanpageModal = function() {
    ModalConfirmation.showInput({
        title: '➕ Add Fanpage to Management',
        message: 'Enter fanpage details:',
        inputs: [
            { id: 'pageId', label: 'Page ID *', type: 'text', required: true },
            { id: 'pageName', label: 'Page Name *', type: 'text', required: true },
            { id: 'pageUrl', label: 'Page URL', type: 'text' },
            { id: 'category', label: 'Category', type: 'text', value: 'business' }
        ],
        confirmText: 'Add Fanpage',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/fanpages/manage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        page_id: values.pageId,
                        page_name: values.pageName,
                        page_url: values.pageUrl,
                        account_id: list[0].id,
                        category: values.category || 'business'
                    })
                });
                
                if (!response.ok) throw new Error('Failed to add fanpage');
                BiAds.showToast('success', 'Success', 'Fanpage added successfully');
                SidebarFeatures.loadFanpages();
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showPostToFanpage = function() {
    ModalConfirmation.showInput({
        title: '📝 Post to Fanpage',
        message: 'Create a post:',
        inputs: [
            { id: 'pageId', label: 'Page ID *', type: 'text', required: true },
            { id: 'content', label: 'Content *', type: 'textarea', required: true },
            { id: 'images', label: 'Image URLs (comma-separated)', type: 'textarea' }
        ],
        confirmText: 'Post',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/fanpages/post', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        page_id: values.pageId,
                        content: values.content,
                        images: values.images ? values.images.split(',').map(i => i.trim()) : []
                    })
                });
                
                if (!response.ok) throw new Error('Failed to post');
                BiAds.showToast('success', 'Success', 'Post created successfully');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showAutoLikeFanpage = function() {
    ModalConfirmation.showInput({
        title: '👍 Auto-Like Config',
        message: 'Configure auto-like for fanpage:',
        inputs: [
            { id: 'pageId', label: 'Page ID *', type: 'text', required: true },
            { id: 'autoLike', label: 'Auto-Like', type: 'checkbox', value: true },
            { id: 'autoComment', label: 'Auto-Comment', type: 'checkbox' },
            { id: 'autoShare', label: 'Auto-Share', type: 'checkbox' },
            { id: 'interval', label: 'Interval (minutes)', type: 'number', value: 60 }
        ],
        confirmText: 'Save Config',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/fanpages/auto-like', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        page_id: values.pageId,
                        auto_like: values.autoLike === 'on',
                        auto_comment: values.autoComment === 'on',
                        auto_share: values.autoShare === 'on',
                        interaction_interval: parseInt(values.interval || 60) * 60
                    })
                });
                
                if (!response.ok) throw new Error('Failed to configure');
                BiAds.showToast('success', 'Success', 'Auto-like configured');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showInviteLikes = function() {
    ModalConfirmation.showInput({
        title: '📩 Invite Friends to Like',
        message: 'Invite friends:',
        inputs: [
            { id: 'pageId', label: 'Page ID *', type: 'text', required: true },
            { id: 'friendUids', label: 'Friend UIDs (one per line) *', type: 'textarea', required: true },
            { id: 'delay', label: 'Delay between invites (seconds)', type: 'number', value: 10 }
        ],
        confirmText: 'Send Invites',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const uids = values.friendUids.split('\n').map(u => u.trim()).filter(u => u);
                
                const response = await fetch('http://localhost:8000/api/fanpages/invite-likes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        page_id: values.pageId,
                        friend_uids: uids,
                        delay_between: parseInt(values.delay || 10)
                    })
                });
                
                if (!response.ok) throw new Error('Failed to send invites');
                BiAds.showToast('success', 'Success', `Inviting ${uids.length} friends`);
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showInteractFanpage = function() {
    ModalConfirmation.showInput({
        title: '💬 Interact with Fanpage',
        message: 'Configure interactions:',
        inputs: [
            { id: 'pageId', label: 'Page ID *', type: 'text', required: true },
            { id: 'autoLike', label: 'Auto-Like Posts', type: 'checkbox', value: true },
            { id: 'autoComment', label: 'Auto-Comment', type: 'checkbox' },
            { id: 'autoShare', label: 'Auto-Share', type: 'checkbox' }
        ],
        confirmText: 'Configure',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/fanpages/interact', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        page_id: values.pageId,
                        auto_like: values.autoLike === 'on',
                        auto_comment: values.autoComment === 'on',
                        auto_share: values.autoShare === 'on',
                        interaction_interval: 300
                    })
                });
                
                if (!response.ok) throw new Error('Failed to configure');
                BiAds.showToast('success', 'Success', 'Interactions configured');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showEditFanpage = function() {
    ModalConfirmation.showInput({
        title: '✏️ Edit Fanpage',
        message: 'Edit fanpage information:',
        inputs: [
            { id: 'pageId', label: 'Page ID *', type: 'text', required: true },
            { id: 'pageName', label: 'New Page Name', type: 'text' },
            { id: 'description', label: 'Description', type: 'textarea' },
            { id: 'category', label: 'Category', type: 'text' }
        ],
        confirmText: 'Update',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/fanpages/edit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        page_id: values.pageId,
                        page_name: values.pageName,
                        description: values.description,
                        category: values.category
                    })
                });
                
                if (!response.ok) throw new Error('Failed to update');
                BiAds.showToast('success', 'Success', 'Fanpage updated');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

// ============================================
// ADVANCED SCANNING
// ============================================

SidebarFeatures.renderScanningPage = function(content, subAction) {
    content.innerHTML = `
        <div class="card">
            <div class="card-header">
                🔍 Advanced Scanning
                <div style="float: right;">
                    <button class="btn-success" onclick="SidebarFeatures.loadScanningStats()">🔄 Refresh</button>
                </div>
            </div>
            <div class="card-body">
                <div class="grid-4" style="margin: 20px 0;">
                    <div class="stat-card"><h4 id="totalScansCount">0</h4><p>Total Scans Today</p></div>
                    <div class="stat-card"><h4 id="postsScannedCount">0</h4><p>Posts Scanned</p></div>
                    <div class="stat-card"><h4 id="membersScannedCount">0</h4><p>Members Scanned</p></div>
                    <div class="stat-card"><h4 id="uidsCollectedCount">0</h4><p>UIDs Collected</p></div>
                </div>
                
                <div class="action-buttons" style="margin: 20px 0; display: flex; gap: 10px; flex-wrap: wrap;">
                    <button class="btn-primary" onclick="SidebarFeatures.showScanPosts()">📝 Scan Posts</button>
                    <button class="btn-secondary" onclick="SidebarFeatures.showScanGroupMembers()">👥 Scan Group Members</button>
                    <button class="btn-success" onclick="SidebarFeatures.showScanFollowers()">👤 Scan Followers</button>
                    <button class="btn-info" onclick="SidebarFeatures.showScanRecentFriends()">🆕 Recent Friends</button>
                    <button class="btn-warning" onclick="SidebarFeatures.showScanFriendSuggestions()">💡 Friend Suggestions</button>
                </div>
                
                <div id="scanningResults">No recent scans</div>
            </div>
        </div>
    `;
    
    this.loadScanningStats();
    
    // Auto-open specific action if provided
    if (subAction) {
        setTimeout(() => {
            switch(subAction) {
                case 'scan-posts': SidebarFeatures.showScanPosts(); break;
                case 'group-members': SidebarFeatures.showScanGroupMembers(); break;
                case 'followers': SidebarFeatures.showScanFollowers(); break;
                case 'recent-friends': SidebarFeatures.showScanRecentFriends(); break;
                case 'friend-suggestions': SidebarFeatures.showScanFriendSuggestions(); break;
            }
        }, 300);
    }
};

SidebarFeatures.loadScanningStats = async function() {
    try {
        const response = await fetch('http://localhost:8000/api/scanning/stats');
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('totalScansCount').textContent = stats.total_scans_today || 0;
            document.getElementById('postsScannedCount').textContent = stats.posts_scanned_today || 0;
            document.getElementById('membersScannedCount').textContent = stats.members_scanned_today || 0;
            document.getElementById('uidsCollectedCount').textContent = stats.total_uids_collected || 0;
        }
    } catch (error) {
        console.error('Error:', error);
        BiAds.showToast('error', 'Error', 'Failed to load stats');
    }
};

SidebarFeatures.showScanPosts = function() {
    ModalConfirmation.showInput({
        title: '📝 Scan Posts',
        message: 'Scan posts from profile/group/page:',
        inputs: [
            { id: 'sourceType', label: 'Source Type *', type: 'select', options: ['profile', 'group', 'page'], required: true },
            { id: 'sourceId', label: 'Source ID (UID/Group ID/Page ID) *', type: 'text', required: true },
            { id: 'maxPosts', label: 'Max Posts', type: 'number', value: 50 },
            { id: 'collectUids', label: 'Collect UIDs', type: 'checkbox', value: true }
        ],
        confirmText: 'Start Scan',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/scanning/scan-posts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        source_type: values.sourceType,
                        source_id: values.sourceId,
                        max_posts: parseInt(values.maxPosts || 50),
                        collect_uids: values.collectUids === 'on'
                    })
                });
                
                if (!response.ok) throw new Error('Failed to start scan');
                BiAds.showToast('success', 'Success', 'Post scanning started');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showScanGroupMembers = function() {
    ModalConfirmation.showInput({
        title: '👥 Scan Group Members',
        message: 'Scan members from a group:',
        inputs: [
            { id: 'groupId', label: 'Group ID *', type: 'text', required: true },
            { id: 'maxMembers', label: 'Max Members', type: 'number', value: 100 },
            { id: 'memberType', label: 'Member Type', type: 'select', options: ['all', 'admins', 'moderators', 'new'], value: 'all' }
        ],
        confirmText: 'Start Scan',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/scanning/scan-group-members', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        group_id: values.groupId,
                        max_members: parseInt(values.maxMembers || 100),
                        member_type: values.memberType || 'all',
                        collect_profile_info: true
                    })
                });
                
                if (!response.ok) throw new Error('Failed to start scan');
                BiAds.showToast('success', 'Success', 'Member scanning started');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showScanFollowers = function() {
    ModalConfirmation.showInput({
        title: '👤 Scan Followers',
        message: 'Scan followers from a profile:',
        inputs: [
            { id: 'targetUid', label: 'Target UID *', type: 'text', required: true },
            { id: 'maxFollowers', label: 'Max Followers', type: 'number', value: 100 },
            { id: 'scanDepth', label: 'Scan Depth', type: 'select', options: ['basic', 'detailed'], value: 'basic' }
        ],
        confirmText: 'Start Scan',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/scanning/scan-followers', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        target_uid: values.targetUid,
                        max_followers: parseInt(values.maxFollowers || 100),
                        scan_depth: values.scanDepth || 'basic'
                    })
                });
                
                if (!response.ok) throw new Error('Failed to start scan');
                BiAds.showToast('success', 'Success', 'Follower scanning started');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showScanRecentFriends = function() {
    ModalConfirmation.showInput({
        title: '🆕 Scan Recent Friends',
        message: 'Scan recently added friends:',
        inputs: [
            { id: 'daysBack', label: 'Days Back', type: 'number', value: 30 },
            { id: 'maxFriends', label: 'Max Friends', type: 'number', value: 100 }
        ],
        confirmText: 'Start Scan',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/scanning/scan-recent-friends', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        days_back: parseInt(values.daysBack || 30),
                        max_friends: parseInt(values.maxFriends || 100)
                    })
                });
                
                if (!response.ok) throw new Error('Failed to start scan');
                BiAds.showToast('success', 'Success', 'Recent friends scanning started');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showScanFriendSuggestions = function() {
    ModalConfirmation.showInput({
        title: '💡 Scan Friend Suggestions',
        message: 'Scan friend suggestions:',
        inputs: [
            { id: 'maxSuggestions', label: 'Max Suggestions', type: 'number', value: 50 },
            { id: 'filterMutual', label: 'Only with mutual friends', type: 'checkbox' },
            { id: 'minMutual', label: 'Min Mutual Friends', type: 'number', value: 0 }
        ],
        confirmText: 'Start Scan',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/scanning/scan-friend-suggestions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        max_suggestions: parseInt(values.maxSuggestions || 50),
                        filter_mutual_friends: values.filterMutual === 'on',
                        min_mutual_friends: parseInt(values.minMutual || 0)
                    })
                });
                
                if (!response.ok) throw new Error('Failed to start scan');
                BiAds.showToast('success', 'Success', 'Friend suggestions scanning started');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

// ============================================
// AUTO ACTIONS
// ============================================

SidebarFeatures.renderAutoActionsPage = function(content, subAction) {
    content.innerHTML = `
        <div class="card">
            <div class="card-header">
                ⚡ Auto Actions
                <div style="float: right;">
                    <button class="btn-success" onclick="SidebarFeatures.loadAutoActionsStats()">🔄 Refresh</button>
                </div>
            </div>
            <div class="card-body">
                <div class="grid-4" style="margin: 20px 0;">
                    <div class="stat-card"><h4 id="newsViewsTodayCount">0</h4><p>News Views</p></div>
                    <div class="stat-card"><h4 id="videosWatchedCount">0</h4><p>Videos Watched</p></div>
                    <div class="stat-card"><h4 id="notifsHiddenCount">0</h4><p>Notifs Hidden</p></div>
                    <div class="stat-card"><h4 id="tagsApprovedCount">0</h4><p>Tags Approved</p></div>
                </div>
                
                <div class="action-buttons" style="margin: 20px 0; display: flex; gap: 10px; flex-wrap: wrap;">
                    <button class="btn-primary" onclick="SidebarFeatures.showAutoViewNews()">📰 Auto-View News</button>
                    <button class="btn-secondary" onclick="SidebarFeatures.showAutoWatchVideo()">🎥 Auto-Watch Video</button>
                    <button class="btn-warning" onclick="SidebarFeatures.showHideNotifications()">🔕 Hide Notifications</button>
                    <button class="btn-success" onclick="SidebarFeatures.showApproveTagsConfig()">✅ Approve Tags</button>
                </div>
                
                <div id="autoActionsStatus">No active auto actions</div>
            </div>
        </div>
    `;
    
    this.loadAutoActionsStats();
    
    // Auto-open specific action if provided
    if (subAction) {
        setTimeout(() => {
            switch(subAction) {
                case 'view-news': SidebarFeatures.showAutoViewNews(); break;
                case 'watch-video': SidebarFeatures.showAutoWatchVideo(); break;
                case 'hide-notifications': SidebarFeatures.showHideNotifications(); break;
                case 'approve-tags': SidebarFeatures.showApproveTagsConfig(); break;
            }
        }, 300);
    }
};

SidebarFeatures.loadAutoActionsStats = async function() {
    try {
        const response = await fetch('http://localhost:8000/api/auto-actions/stats');
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('newsViewsTodayCount').textContent = stats.news_views_today || 0;
            document.getElementById('videosWatchedCount').textContent = stats.videos_watched_today || 0;
            document.getElementById('notifsHiddenCount').textContent = stats.notifications_hidden_today || 0;
            document.getElementById('tagsApprovedCount').textContent = stats.tags_approved_today || 0;
        }
    } catch (error) {
        console.error('Error:', error);
        BiAds.showToast('error', 'Error', 'Failed to load stats');
    }
};

SidebarFeatures.showAutoViewNews = function() {
    ModalConfirmation.showInput({
        title: '📰 Auto-View News',
        message: 'Configure auto news viewing:',
        inputs: [
            { id: 'enabled', label: 'Enable Auto-View', type: 'checkbox', value: true },
            { id: 'viewCount', label: 'Posts to View', type: 'number', value: 20 },
            { id: 'viewDuration', label: 'Seconds per Post', type: 'number', value: 5 },
            { id: 'autoLike', label: 'Auto-Like while viewing', type: 'checkbox' },
            { id: 'interval', label: 'Run Interval (minutes)', type: 'number', value: 60 }
        ],
        confirmText: 'Save Config',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/auto-actions/auto-view-news', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        enabled: values.enabled === 'on',
                        view_count: parseInt(values.viewCount || 20),
                        view_duration: parseInt(values.viewDuration || 5),
                        scroll_behavior: 'natural',
                        interaction_rate: 0.3,
                        auto_like_enabled: values.autoLike === 'on',
                        auto_react_enabled: false,
                        interval_minutes: parseInt(values.interval || 60)
                    })
                });
                
                if (!response.ok) throw new Error('Failed to configure');
                BiAds.showToast('success', 'Success', 'Auto-view news configured');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showAutoWatchVideo = function() {
    ModalConfirmation.showInput({
        title: '🎥 Auto-Watch Video',
        message: 'Configure auto video watching:',
        inputs: [
            { id: 'enabled', label: 'Enable Auto-Watch', type: 'checkbox', value: true },
            { id: 'maxVideos', label: 'Max Videos', type: 'number', value: 10 },
            { id: 'watchDuration', label: 'Seconds per Video', type: 'number', value: 30 },
            { id: 'autoLike', label: 'Auto-Like Videos', type: 'checkbox' },
            { id: 'interval', label: 'Run Interval (minutes)', type: 'number', value: 120 }
        ],
        confirmText: 'Save Config',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/auto-actions/auto-watch-video', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        enabled: values.enabled === 'on',
                        max_videos: parseInt(values.maxVideos || 10),
                        watch_duration: parseInt(values.watchDuration || 30),
                        video_source: 'feed',
                        auto_like: values.autoLike === 'on',
                        auto_comment: false,
                        skip_ads: true,
                        interval_minutes: parseInt(values.interval || 120)
                    })
                });
                
                if (!response.ok) throw new Error('Failed to configure');
                BiAds.showToast('success', 'Success', 'Auto-watch video configured');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showHideNotifications = function() {
    ModalConfirmation.showInput({
        title: '🔕 Hide Notifications',
        message: 'Configure notification hiding:',
        inputs: [
            { id: 'notifTypes', label: 'Types to Hide (comma-separated) *', type: 'text', value: 'likes,comments,shares', required: true },
            { id: 'interval', label: 'Check Interval (minutes)', type: 'number', value: 30 },
            { id: 'keepImportant', label: 'Keep Important', type: 'checkbox', value: true }
        ],
        confirmText: 'Configure',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const types = values.notifTypes.split(',').map(t => t.trim());
                
                const response = await fetch('http://localhost:8000/api/auto-actions/hide-notifications', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        notification_types: types,
                        auto_hide_interval: parseInt(values.interval || 30),
                        keep_important: values.keepImportant === 'on',
                        mark_as_read: true
                    })
                });
                
                if (!response.ok) throw new Error('Failed to configure');
                BiAds.showToast('success', 'Success', 'Hide notifications configured');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showApproveTagsConfig = function() {
    ModalConfirmation.showInput({
        title: '✅ Approve Tags Config',
        message: 'Configure tag approval:',
        inputs: [
            { id: 'autoApprove', label: 'Auto-Approve All', type: 'checkbox' },
            { id: 'friendsOnly', label: 'Friends Only', type: 'checkbox', value: true },
            { id: 'inPosts', label: 'Approve in Posts', type: 'checkbox', value: true },
            { id: 'inPhotos', label: 'Approve in Photos', type: 'checkbox', value: true },
            { id: 'interval', label: 'Check Interval (minutes)', type: 'number', value: 15 }
        ],
        confirmText: 'Configure',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/auto-actions/approve-tags', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        auto_approve: values.autoApprove === 'on',
                        auto_approve_from_friends: values.friendsOnly === 'on',
                        approve_in_posts: values.inPosts === 'on',
                        approve_in_photos: values.inPhotos === 'on',
                        approve_in_videos: true,
                        check_interval: parseInt(values.interval || 15)
                    })
                });
                
                if (!response.ok) throw new Error('Failed to configure');
                BiAds.showToast('success', 'Success', 'Tag approval configured');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

// ============================================
// MISC FEATURES
// ============================================

SidebarFeatures.renderMiscPage = function(content, subAction) {
    content.innerHTML = `
        <div class="card">
            <div class="card-header">🔧 Miscellaneous Features</div>
            <div class="card-body">
                <div class="action-buttons" style="margin: 20px 0; display: flex; gap: 10px; flex-wrap: wrap;">
                    <button class="btn-primary" onclick="SidebarFeatures.showPokeFriends()">👆 Poke Friends</button>
                    <button class="btn-warning" onclick="SidebarFeatures.showCancelRequests()">❌ Cancel Requests</button>
                    <button class="btn-secondary" onclick="SidebarFeatures.showInviteToGroup()">📨 Invite to Group</button>
                    <button class="btn-info" onclick="SidebarFeatures.showJoinViaUID()">🔗 Join via UID</button>
                    <button class="btn-danger" onclick="SidebarFeatures.showDeletePost()">🗑️ Delete Post</button>
                    <button class="btn-success" onclick="SidebarFeatures.showSharePost()">📤 Share Post</button>
                    <button class="btn-primary" onclick="SidebarFeatures.showUpdateBio()">✏️ Update Bio</button>
                </div>
                <div id="miscFeaturesContent">Select an action above</div>
            </div>
        </div>
    `;
    
    // Auto-open specific action if provided
    if (subAction) {
        setTimeout(() => {
            switch(subAction) {
                case 'poke-friends': SidebarFeatures.showPokeFriends(); break;
                case 'cancel-request': SidebarFeatures.showCancelRequests(); break;
                case 'invite-to-group': SidebarFeatures.showInviteToGroup(); break;
                case 'join-via-uid': SidebarFeatures.showJoinViaUID(); break;
                case 'delete-post': SidebarFeatures.showDeletePost(); break;
                case 'share-post-2': SidebarFeatures.showSharePost(); break;
                case 'update-bio': SidebarFeatures.showUpdateBio(); break;
            }
        }, 300);
    }
};

SidebarFeatures.showPokeFriends = function() {
    ModalConfirmation.showInput({
        title: '👆 Poke Friends',
        message: 'Poke friends:',
        inputs: [
            { id: 'friendUids', label: 'Friend UIDs (one per line) *', type: 'textarea', required: true },
            { id: 'delay', label: 'Delay between pokes (seconds)', type: 'number', value: 10 }
        ],
        confirmText: 'Start Poking',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const uids = values.friendUids.split('\n').map(u => u.trim()).filter(u => u);
                
                const response = await fetch('http://localhost:8000/api/misc/poke-friends', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        friend_uids: uids,
                        delay_between: parseInt(values.delay || 10)
                    })
                });
                
                if (!response.ok) throw new Error('Failed to poke');
                BiAds.showToast('success', 'Success', `Poking ${uids.length} friends`);
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showCancelRequests = function() {
    ModalConfirmation.showInput({
        title: '❌ Cancel Friend Requests',
        message: 'Cancel sent friend requests:',
        inputs: [
            { id: 'targetUids', label: 'Target UIDs (one per line) *', type: 'textarea', required: true }
        ],
        confirmText: 'Cancel Requests',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const uids = values.targetUids.split('\n').map(u => u.trim()).filter(u => u);
                
                const response = await fetch('http://localhost:8000/api/misc/cancel-friend-request', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        target_uids: uids
                    })
                });
                
                if (!response.ok) throw new Error('Failed to cancel');
                BiAds.showToast('success', 'Success', `Cancelling ${uids.length} requests`);
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showInviteToGroup = function() {
    ModalConfirmation.showInput({
        title: '📨 Invite Friends to Group',
        message: 'Invite friends:',
        inputs: [
            { id: 'groupId', label: 'Group ID *', type: 'text', required: true },
            { id: 'friendUids', label: 'Friend UIDs (one per line) *', type: 'textarea', required: true },
            { id: 'delay', label: 'Delay (seconds)', type: 'number', value: 5 }
        ],
        confirmText: 'Send Invites',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const uids = values.friendUids.split('\n').map(u => u.trim()).filter(u => u);
                
                const response = await fetch('http://localhost:8000/api/misc/invite-to-group', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        group_id: values.groupId,
                        friend_uids: uids,
                        delay_between: parseInt(values.delay || 5)
                    })
                });
                
                if (!response.ok) throw new Error('Failed to invite');
                BiAds.showToast('success', 'Success', `Inviting ${uids.length} friends`);
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showJoinViaUID = function() {
    ModalConfirmation.showInput({
        title: '🔗 Join Groups via UID',
        message: 'Join groups:',
        inputs: [
            { id: 'groupUids', label: 'Group UIDs (one per line) *', type: 'textarea', required: true },
            { id: 'delay', label: 'Delay (seconds)', type: 'number', value: 10 }
        ],
        confirmText: 'Join Groups',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const uids = values.groupUids.split('\n').map(u => u.trim()).filter(u => u);
                
                const response = await fetch('http://localhost:8000/api/misc/join-via-uid', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        group_uids: uids,
                        delay_between: parseInt(values.delay || 10)
                    })
                });
                
                if (!response.ok) throw new Error('Failed to join');
                BiAds.showToast('success', 'Success', `Joining ${uids.length} groups`);
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showDeletePost = function() {
    ModalConfirmation.showDanger({
        title: '🗑️ Delete Posts',
        message: 'WARNING: This will permanently delete the posts. Enter Post IDs (one per line):',
        inputs: [
            { id: 'postIds', label: 'Post IDs *', type: 'textarea', required: true }
        ],
        confirmText: 'Delete',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const ids = values.postIds.split('\n').map(i => i.trim()).filter(i => i);
                
                const response = await fetch('http://localhost:8000/api/misc/delete-post', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        post_ids: ids,
                        confirm_delete: true
                    })
                });
                
                if (!response.ok) throw new Error('Failed to delete');
                BiAds.showToast('success', 'Success', `Deleting ${ids.length} posts`);
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showSharePost = function() {
    ModalConfirmation.showInput({
        title: '📤 Share Post',
        message: 'Share a post:',
        inputs: [
            { id: 'postUrl', label: 'Post URL *', type: 'text', required: true },
            { id: 'shareTo', label: 'Share To', type: 'select', options: ['timeline', 'group', 'story'], value: 'timeline' },
            { id: 'message', label: 'Share Message', type: 'textarea' },
            { id: 'groupId', label: 'Group ID (if sharing to group)', type: 'text' }
        ],
        confirmText: 'Share',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/misc/share-post-2', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        post_url: values.postUrl,
                        share_to: values.shareTo,
                        message: values.message,
                        target_group_id: values.groupId
                    })
                });
                
                if (!response.ok) throw new Error('Failed to share');
                BiAds.showToast('success', 'Success', 'Post shared successfully');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

SidebarFeatures.showUpdateBio = function() {
    ModalConfirmation.showInput({
        title: '✏️ Update Profile Bio',
        message: 'Update your profile information:',
        inputs: [
            { id: 'bioText', label: 'Bio Text (max 101 chars) *', type: 'textarea', required: true },
            { id: 'workInfo', label: 'Work', type: 'text' },
            { id: 'educationInfo', label: 'Education', type: 'text' },
            { id: 'location', label: 'Location', type: 'text' },
            { id: 'hometown', label: 'Hometown', type: 'text' }
        ],
        confirmText: 'Update',
        onConfirm: async (values) => {
            try {
                const accounts = await fetch('http://localhost:8000/api/accounts?limit=1');
                const list = await accounts.json();
                if (list.length === 0) throw new Error('No accounts available');
                
                const response = await fetch('http://localhost:8000/api/misc/update-bio', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        account_id: list[0].id,
                        bio_text: values.bioText.substring(0, 101),
                        work_info: values.workInfo,
                        education_info: values.educationInfo,
                        location: values.location,
                        hometown: values.hometown
                    })
                });
                
                if (!response.ok) throw new Error('Failed to update');
                BiAds.showToast('success', 'Success', 'Profile bio updated');
            } catch (error) {
                BiAds.showToast('error', 'Error', error.message);
            }
        }
    });
};

console.log('✅ Sidebar features loaded (Fanpage, Scanning, Auto Actions, Misc)');
