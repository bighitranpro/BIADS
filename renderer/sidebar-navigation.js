// Sidebar Task Navigation Handler
// Connects sidebar task buttons to actual page navigation

document.addEventListener('DOMContentLoaded', function() {
    // Get all task items
    const taskItems = document.querySelectorAll('.task-item[data-task]');
    
    taskItems.forEach(item => {
        item.addEventListener('click', function() {
            const task = this.dataset.task;
            handleTaskNavigation(task);
        });
    });
});

function handleTaskNavigation(task) {
    const content = document.getElementById('main-content');
    if (!content) return;
    
    // Map tasks to page render functions
    const taskMapping = {
        // ===== GROUP TASKS =====
        'join-groups': () => navigateToPage('groups', 'join'),
        'leave-groups': () => navigateToPage('groups', 'leave'),
        'scan-groups': () => navigateToPage('groups', 'scan'),
        'groups-joined': () => navigateToPage('groups', 'list'),
        'invite-to-group': () => navigateToPage('misc', 'invite-to-group'),
        
        // ===== FRIEND TASKS =====
        'add-friend': () => navigateToPage('friends', 'add'),
        'unfriend': () => navigateToPage('friends', 'unfriend'),
        'accept-friend': () => navigateToPage('friends', 'accept'),
        'reject-friend': () => navigateToPage('friends', 'reject'),
        'cancel-request': () => navigateToPage('misc', 'cancel-request'),
        'poke-friends': () => navigateToPage('misc', 'poke-friends'),
        
        // ===== INTERACTION TASKS =====
        'post-status': () => navigateToPage('interactions', 'post'),
        'comment-post': () => navigateToPage('interactions', 'comment'),
        'auto-like': () => navigateToPage('interactions', 'autolike'),
        'share-post': () => navigateToPage('interactions', 'share'),
        'share-post-2': () => navigateToPage('misc', 'share-post-2'),
        'delete-post': () => navigateToPage('misc', 'delete-post'),
        
        // ===== SCANNING TASKS =====
        'scanned-uids': () => navigateToPage('facebook-ids'),
        'scan-posts-action': () => navigateToPage('scanning', 'scan-posts'),
        'scanned-posts': () => navigateToPage('scanning', 'scanned-posts'),
        'scanned-group-members': () => navigateToPage('scanning', 'group-members'),
        'scanned-followers': () => navigateToPage('scanning', 'followers'),
        'scanned-recent-friends': () => navigateToPage('scanning', 'recent-friends'),
        'scanned-friend-suggestions': () => navigateToPage('scanning', 'friend-suggestions'),
        
        // ===== FANPAGE TASKS =====
        'manage-fanpage': () => navigateToPage('fanpage', 'manage'),
        'post-fanpage': () => navigateToPage('fanpage', 'post'),
        'like-fanpage-auto': () => navigateToPage('fanpage', 'auto-like'),
        'invite-like-fanpage': () => navigateToPage('fanpage', 'invite-likes'),
        'interact-fanpage': () => navigateToPage('fanpage', 'interact'),
        'send-inbox-fanpage': () => navigateToPage('fanpage', 'send-inbox'),
        'message-fanpage': () => navigateToPage('fanpage', 'send-message'),
        'share-fanpage': () => navigateToPage('fanpage', 'share'),
        'delete-fanpage-post': () => navigateToPage('fanpage', 'delete-post'),
        'edit-fanpage': () => navigateToPage('fanpage', 'edit'),
        
        // ===== AUTO ACTIONS =====
        'auto-view-news': () => navigateToPage('auto-actions', 'view-news'),
        'auto-watch-video': () => navigateToPage('auto-actions', 'watch-video'),
        'hide-notif': () => navigateToPage('auto-actions', 'hide-notifications'),
        'approve-tag': () => navigateToPage('auto-actions', 'approve-tags'),
        
        // ===== MISC TASKS =====
        'update-bio': () => navigateToPage('misc', 'update-bio'),
        'join-via-uid': () => navigateToPage('misc', 'join-via-uid'),
        'send-message': () => navigateToPage('messages'),
    };
    
    if (taskMapping[task]) {
        taskMapping[task]();
    } else {
        console.log('Task not yet implemented:', task);
        BiAds.showToast('info', 'Coming Soon', `Feature "${task}" is under development`);
    }
}

function navigateToPage(page, subAction = null) {
    const content = document.getElementById('main-content');
    const title = document.getElementById('page-title');
    
    // Update active state
    document.querySelectorAll('.top-nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Render appropriate page
    switch(page) {
        case 'friends':
            if (title) title.textContent = '👥 Quản lý bạn bè';
            if (window.AdvancedFeatures && window.AdvancedFeatures.renderFriendManagementPage) {
                window.AdvancedFeatures.renderFriendManagementPage(content);
                // Auto-open specific action if provided
                if (subAction === 'add') {
                    setTimeout(() => AdvancedFeatures.showAddFriendModal(), 300);
                } else if (subAction === 'unfriend') {
                    BiAds.showToast('info', 'Tip', 'Select a friend from the list to unfriend');
                }
            }
            break;
            
        case 'interactions':
            if (title) title.textContent = '💬 Tương tác tài khoản';
            if (window.AdvancedFeatures && window.AdvancedFeatures.renderInteractionsPage) {
                window.AdvancedFeatures.renderInteractionsPage(content);
                // Auto-open specific action if provided
                if (subAction === 'autolike') {
                    setTimeout(() => AdvancedFeatures.showConfigAutoLike(), 300);
                } else if (subAction === 'comment') {
                    setTimeout(() => AdvancedFeatures.quickCommentPost(), 300);
                }
            }
            break;
            
        case 'groups':
            if (title) title.textContent = '🏘️ Quản lý nhóm';
            if (window.AdvancedFeatures && window.AdvancedFeatures.renderGroupManagementPage) {
                window.AdvancedFeatures.renderGroupManagementPage(content);
                // Auto-open specific action if provided
                if (subAction === 'join') {
                    setTimeout(() => AdvancedFeatures.showJoinGroupModal(), 300);
                } else if (subAction === 'leave') {
                    BiAds.showToast('info', 'Tip', 'Enter Group ID to leave');
                } else if (subAction === 'list') {
                    BiAds.showToast('info', 'Groups Joined', 'Viewing all joined groups');
                }
            }
            break;
            
        case 'messages':
            if (title) title.textContent = '💬 Quản lý tin nhắn';
            // Navigate using existing top nav
            const messagesBtn = document.querySelector('[data-page="messages"]');
            if (messagesBtn) messagesBtn.click();
            break;
            
        case 'facebook-ids':
            if (title) title.textContent = '🆔 Facebook IDs';
            const idsBtn = document.querySelector('[data-page="facebook-ids"]');
            if (idsBtn) idsBtn.click();
            break;
            
        case 'scanning':
            if (title) title.textContent = '🔍 Advanced Scanning';
            if (window.SidebarFeatures && window.SidebarFeatures.renderScanningPage) {
                window.SidebarFeatures.renderScanningPage(content, subAction);
            }
            break;
            
        case 'fanpage':
            if (title) title.textContent = '📄 Fanpage Management';
            if (window.SidebarFeatures && window.SidebarFeatures.renderFanpagePage) {
                window.SidebarFeatures.renderFanpagePage(content, subAction);
            }
            break;
            
        case 'auto-actions':
            if (title) title.textContent = '⚡ Auto Actions';
            if (window.SidebarFeatures && window.SidebarFeatures.renderAutoActionsPage) {
                window.SidebarFeatures.renderAutoActionsPage(content, subAction);
            }
            break;
            
        case 'misc':
            if (title) title.textContent = '🔧 Misc Features';
            if (window.SidebarFeatures && window.SidebarFeatures.renderMiscPage) {
                window.SidebarFeatures.renderMiscPage(content, subAction);
            }
            break;
            
        default:
            console.log('Page not found:', page);
    }
}

console.log('✅ Sidebar navigation loaded');
