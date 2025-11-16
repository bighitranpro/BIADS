// Bi Ads - API Client v2.0
// This file handles all communication with backend API

const API_URL = 'http://localhost:8000';

const apiClient = {
    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${API_URL}${endpoint}`;
        const config = {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // Health check
    async healthCheck() {
        return await this.request('/health');
    },

    // Group operations
    async joinGroups(accountId, groupList, options = {}) {
        return await this.request('/api/groups/join', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                group_list: groupList,
                delay: options.delay || 10,
                max_groups: options.maxGroups || 20
            })
        });
    },

    async leaveGroups(accountId, groupList) {
        return await this.request('/api/groups/leave', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                group_list: groupList
            })
        });
    },

    async scanGroups(accountId, keyword, options = {}) {
        return await this.request('/api/groups/scan', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                keyword: keyword,
                limit: options.limit || 50
            })
        });
    },

    // Friend operations
    async addFriends(accountId, uidList, options = {}) {
        return await this.request('/api/friends/add', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                uid_list: uidList,
                delay: options.delay || 15,
                max_requests: options.maxRequests || 50
            })
        });
    },

    async acceptFriends(accountId, options = {}) {
        return await this.request('/api/friends/accept', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                max_requests: options.maxRequests || 50
            })
        });
    },

    async unfriend(accountId, uidList) {
        return await this.request('/api/friends/unfriend', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                uid_list: uidList
            })
        });
    },

    // Post operations
    async createPost(accountId, content, options = {}) {
        return await this.request('/api/posts/create', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                content: content,
                images: options.images || [],
                post_to_groups: options.postToGroups || false
            })
        });
    },

    async commentPost(accountId, postId, comment) {
        return await this.request('/api/posts/comment', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                post_id: postId,
                comment: comment
            })
        });
    },

    async likePost(accountId, postId) {
        return await this.request('/api/posts/like', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                post_id: postId
            })
        });
    },

    async sharePost(accountId, postId, options = {}) {
        return await this.request('/api/posts/share', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                post_id: postId,
                message: options.message || ''
            })
        });
    },

    // Fanpage operations
    async fanpagePost(accountId, pageId, content, options = {}) {
        return await this.request('/api/fanpage/post', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                page_id: pageId,
                content: content,
                images: options.images || []
            })
        });
    },

    async fanpageInteract(accountId, pageId, action) {
        return await this.request('/api/fanpage/interact', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                page_id: pageId,
                action: action
            })
        });
    },

    // Get task status
    async getTaskStatus(taskId) {
        return await this.request(`/api/task/${taskId}`);
    },

    // Account operations
    async getAccounts(skip = 0, limit = 100, status = null) {
        let endpoint = `/api/accounts?skip=${skip}&limit=${limit}`;
        if (status) {
            endpoint += `&status=${status}`;
        }
        return await this.request(endpoint);
    },

    async getAccountById(accountId) {
        return await this.request(`/api/accounts/${accountId}`);
    },

    async createAccount(accountData) {
        return await this.request('/api/accounts', {
            method: 'POST',
            body: JSON.stringify(accountData)
        });
    },

    async updateAccount(accountId, accountData) {
        return await this.request(`/api/accounts/${accountId}`, {
            method: 'PUT',
            body: JSON.stringify(accountData)
        });
    },

    async deleteAccount(accountId) {
        return await this.request(`/api/accounts/${accountId}`, {
            method: 'DELETE'
        });
    },

    async checkAccountStatus(accountId) {
        return await this.request(`/api/accounts/${accountId}/check-status`, {
            method: 'POST'
        });
    },

    async checkAccountsStatusBulk(accountIds = null) {
        return await this.request('/api/accounts/check-status-bulk', {
            method: 'POST',
            body: JSON.stringify(accountIds)
        });
    },

    async assignProxyToAccount(accountId, proxyId) {
        const url = proxyId 
            ? `/api/accounts/${accountId}/assign-proxy?proxy_id=${proxyId}`
            : `/api/accounts/${accountId}/assign-proxy`;
        return await this.request(url, {
            method: 'PUT'
        });
    },

    // Proxy operations
    async getProxies(skip = 0, limit = 100) {
        return await this.request(`/api/proxies?skip=${skip}&limit=${limit}`);
    },

    async createProxy(proxyData) {
        return await this.request('/api/proxies', {
            method: 'POST',
            body: JSON.stringify(proxyData)
        });
    },

    async deleteProxy(proxyId) {
        return await this.request(`/api/proxies/${proxyId}`, {
            method: 'DELETE'
        });
    },

    // ========== SETTINGS API ==========
    
    // Get all settings
    async getSettings() {
        return await this.request('/api/settings');
    },

    // Get settings by category
    async getSettingsByCategory(category) {
        return await this.request(`/api/settings/category/${category}`);
    },

    // Update all settings
    async updateSettings(settings) {
        return await this.request('/api/settings', {
            method: 'PUT',
            body: JSON.stringify(settings)
        });
    },

    // Update single setting
    async updateSetting(key, value, category = null) {
        return await this.request('/api/settings/update', {
            method: 'PUT',
            body: JSON.stringify({ key, value, category })
        });
    },

    // Test Telegram connection
    async testTelegram() {
        return await this.request('/api/settings/telegram/test', {
            method: 'POST'
        });
    },

    // Get system info
    async getSystemInfo() {
        return await this.request('/api/settings/system/info');
    },

    // Export settings
    async exportSettings() {
        return await this.request('/api/settings/export');
    },

    // Import settings
    async importSettings(settings) {
        return await this.request('/api/settings/import', {
            method: 'POST',
            body: JSON.stringify(settings)
        });
    },

    // ========== FACEBOOK TASKS API ==========
    
    // Group Tasks
    async scanGroupsByKeyword(accountId, keyword, limit = 50) {
        return await this.request('/api/facebook/groups/scan', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                keyword: keyword,
                limit: limit
            })
        });
    },

    async joinGroupsBulk(accountIds, groupIds, delay = 10, maxGroupsPerAccount = 20) {
        return await this.request('/api/facebook/groups/join', {
            method: 'POST',
            body: JSON.stringify({
                account_ids: accountIds,
                group_ids: groupIds,
                delay_between_actions: delay,
                max_groups_per_account: maxGroupsPerAccount
            })
        });
    },

    async leaveGroupsBulk(accountId, groupIds) {
        return await this.request('/api/facebook/groups/leave', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                group_ids: groupIds
            })
        });
    },

    async getJoinedGroups(accountId) {
        return await this.request(`/api/facebook/groups/joined/${accountId}`);
    },

    // Post Tasks
    async createFacebookPost(accountId, content, targetType = 'timeline', targetId = null, imageUrls = []) {
        return await this.request('/api/facebook/posts/create', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                content: content,
                target_type: targetType,
                target_id: targetId,
                image_urls: imageUrls
            })
        });
    },

    async commentOnPost(postId, accountIds, comments, delay = 5) {
        return await this.request('/api/facebook/posts/comment', {
            method: 'POST',
            body: JSON.stringify({
                post_id: postId,
                account_ids: accountIds,
                comments: comments,
                delay_between_comments: delay
            })
        });
    },

    async reactToPost(postId, accountIds, reactionType = 'LIKE', delay = 3) {
        return await this.request('/api/facebook/posts/react', {
            method: 'POST',
            body: JSON.stringify({
                post_id: postId,
                account_ids: accountIds,
                reaction_type: reactionType,
                delay_between_reactions: delay
            })
        });
    },

    // Friend Tasks
    async sendFriendRequests(accountId, userIds, delay = 10, maxRequests = 50) {
        return await this.request('/api/facebook/friends/add', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                user_ids: userIds,
                delay_between_requests: delay,
                max_requests_per_account: maxRequests
            })
        });
    },

    async sendMessages(accountId, userIds, messages, delay = 5) {
        return await this.request('/api/facebook/messages/send', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                user_ids: userIds,
                messages: messages,
                delay_between_messages: delay
            })
        });
    },

    // Page Tasks
    async createPagePost(accountId, pageId, content, imageUrls = []) {
        return await this.request('/api/facebook/pages/post', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                page_id: pageId,
                content: content,
                image_urls: imageUrls
            })
        });
    },

    // Task Management
    async getFacebookTaskStatus(taskId) {
        return await this.request(`/api/facebook/tasks/${taskId}`);
    },

    async cancelFacebookTask(taskId) {
        return await this.request(`/api/facebook/tasks/${taskId}`, {
            method: 'DELETE'
        });
    },

    // Statistics
    async getStatistics() {
        return await this.request('/api/stats');
    },

    // Logs
    async getLogs(accountId = null, level = null, skip = 0, limit = 100) {
        let endpoint = `/api/logs?skip=${skip}&limit=${limit}`;
        if (accountId) endpoint += `&account_id=${accountId}`;
        if (level) endpoint += `&level=${level}`;
        return await this.request(endpoint);
    },

    // ========== ACCOUNT INTERACTIONS API ==========

    // Post Status
    async postStatus(accountIds, content, targetType = 'timeline', targetId = null, imageUrls = [], delay = 10, privacy = 'public') {
        return await this.request('/api/interactions/post-status', {
            method: 'POST',
            body: JSON.stringify({
                account_ids: accountIds,
                content: content,
                target_type: targetType,
                target_id: targetId,
                image_urls: imageUrls,
                delay_between_posts: delay,
                privacy: privacy
            })
        });
    },

    // Share Post
    async sharePost(accountIds, postUrl, message = null, targetType = 'timeline', targetId = null, delay = 10) {
        return await this.request('/api/interactions/share-post', {
            method: 'POST',
            body: JSON.stringify({
                account_ids: accountIds,
                post_url: postUrl,
                message: message,
                target_type: targetType,
                target_id: targetId,
                delay_between_shares: delay
            })
        });
    },

    // Comment on Post
    async commentPost(accountIds, postUrls, comments, delay = 5, randomComments = true) {
        return await this.request('/api/interactions/comment-post', {
            method: 'POST',
            body: JSON.stringify({
                account_ids: accountIds,
                post_urls: postUrls,
                comments: comments,
                delay_between_comments: delay,
                random_comments: randomComments
            })
        });
    },

    // Auto Like
    async autoLike(accountIds, targetUrls, reactionType = 'LIKE', delay = 3) {
        return await this.request('/api/interactions/auto-like', {
            method: 'POST',
            body: JSON.stringify({
                account_ids: accountIds,
                target_urls: targetUrls,
                reaction_type: reactionType,
                delay_between_reactions: delay
            })
        });
    },

    // Update Bio
    async updateBio(accountIds, bioText, bioType = 'description') {
        return await this.request('/api/interactions/update-bio', {
            method: 'POST',
            body: JSON.stringify({
                account_ids: accountIds,
                bio_text: bioText,
                bio_type: bioType
            })
        });
    },

    // Hide Notifications
    async hideNotifications(accountIds, notificationType = 'all') {
        return await this.request('/api/interactions/hide-notifications', {
            method: 'POST',
            body: JSON.stringify({
                account_ids: accountIds,
                notification_type: notificationType
            })
        });
    },

    // Auto View Newsfeed
    async autoViewNews(accountIds, durationMinutes = 10, scrollCount = 20, interactProbability = 0.3) {
        return await this.request('/api/interactions/auto-view-news', {
            method: 'POST',
            body: JSON.stringify({
                account_ids: accountIds,
                duration_minutes: durationMinutes,
                scroll_count: scrollCount,
                interact_probability: interactProbability
            })
        });
    },

    // Auto Watch Video
    async autoWatchVideo(accountIds, videoUrls = [], watchDuration = 30, videosCount = 10) {
        return await this.request('/api/interactions/auto-watch-video', {
            method: 'POST',
            body: JSON.stringify({
                account_ids: accountIds,
                video_urls: videoUrls,
                watch_duration_seconds: watchDuration,
                videos_count: videosCount
            })
        });
    },

    // Delete Posts
    async deletePosts(accountId, postIds) {
        return await this.request('/api/interactions/delete-posts', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                post_ids: postIds
            })
        });
    },

    // Poke Friends
    async pokeFriends(accountIds, friendIds, delay = 5) {
        return await this.request('/api/interactions/poke-friends', {
            method: 'POST',
            body: JSON.stringify({
                account_ids: accountIds,
                friend_ids: friendIds,
                delay_between_pokes: delay
            })
        });
    },

    // Get Interaction Task Status
    async getInteractionTaskStatus(taskId) {
        return await this.request(`/api/interactions/tasks/${taskId}`);
    }
};

// Make API client available globally
window.apiClient = apiClient;
