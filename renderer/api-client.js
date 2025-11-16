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
    }
};

// Make API client available globally
window.apiClient = apiClient;
