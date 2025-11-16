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
        // Group tasks
        'join-groups': () => navigateToPage('groups', 'join'),
        'leave-groups': () => navigateToPage('groups', 'leave'),
        'scan-groups': () => navigateToPage('groups', 'scan'),
        'invite-to-group': () => navigateToPage('groups', 'invite'),
        
        // Friend tasks
        'add-friend': () => navigateToPage('friends', 'add'),
        'unfriend': () => navigateToPage('friends', 'unfriend'),
        'accept-friend': () => navigateToPage('friends', 'accept'),
        'reject-friend': () => navigateToPage('friends', 'reject'),
        'cancel-request': () => navigateToPage('friends', 'cancel'),
        'send-message': () => navigateToPage('messages'),
        
        // Interaction tasks
        'post-status': () => navigateToPage('interactions', 'post'),
        'comment-post': () => navigateToPage('interactions', 'comment'),
        'auto-like': () => navigateToPage('interactions', 'autolike'),
        'share-post': () => navigateToPage('interactions', 'share'),
        'share-post-2': () => navigateToPage('interactions', 'share'),
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
                }
            }
            break;
            
        case 'messages':
            if (title) title.textContent = '💬 Quản lý tin nhắn';
            // Navigate using existing top nav
            const messagesBtn = document.querySelector('[data-page="messages"]');
            if (messagesBtn) messagesBtn.click();
            break;
            
        default:
            console.log('Page not found:', page);
    }
}

console.log('✅ Sidebar navigation loaded');
