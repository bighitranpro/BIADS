/**
 * Bi Ads - Advanced Features API Client
 * Author: Bi Ads Team
 * Version: 3.0.0
 */

const AdvancedAPIClient = {
    baseURL: 'http://localhost:8000/api/advanced',

    // Helper function for API calls
    async request(method, endpoint, data = null) {
        const url = `${this.baseURL}${endpoint}`;
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    // ============================================
    // SUB ACCOUNTS
    // ============================================

    async getSubAccounts(mainAccountId = null, status = null) {
        let endpoint = '/sub-accounts?';
        if (mainAccountId) endpoint += `main_account_id=${mainAccountId}&`;
        if (status) endpoint += `status=${status}&`;
        return await this.request('GET', endpoint);
    },

    async getSubAccountsStats(mainAccountId = null) {
        let endpoint = '/sub-accounts/stats';
        if (mainAccountId) endpoint += `?main_account_id=${mainAccountId}`;
        return await this.request('GET', endpoint);
    },

    async createSubAccount(data) {
        return await this.request('POST', '/sub-accounts', data);
    },

    async updateSubAccount(subAccountId, data) {
        return await this.request('PUT', `/sub-accounts/${subAccountId}`, data);
    },

    async deleteSubAccount(subAccountId) {
        return await this.request('DELETE', `/sub-accounts/${subAccountId}`);
    },

    async bulkCreateSubAccounts(subAccountsData) {
        return await this.request('POST', '/sub-accounts/bulk', subAccountsData);
    },

    // ============================================
    // FACEBOOK IDS
    // ============================================

    async getFacebookIDs(status = null, source = null) {
        let endpoint = '/facebook-ids?';
        if (status) endpoint += `status=${status}&`;
        if (source) endpoint += `source=${source}&`;
        return await this.request('GET', endpoint);
    },

    async getFacebookIDsStats() {
        return await this.request('GET', '/facebook-ids/stats');
    },

    async createFacebookID(data) {
        return await this.request('POST', '/facebook-ids', data);
    },

    async deleteFacebookID(fbId) {
        return await this.request('DELETE', `/facebook-ids/${fbId}`);
    },

    async bulkCreateFacebookIDs(idsData) {
        return await this.request('POST', '/facebook-ids/bulk', idsData);
    },

    // ============================================
    // IP ADDRESSES
    // ============================================

    async getIPAddresses(status = null) {
        let endpoint = '/ip-addresses?';
        if (status) endpoint += `status=${status}&`;
        return await this.request('GET', endpoint);
    },

    async getIPAddressesStats() {
        return await this.request('GET', '/ip-addresses/stats');
    },

    async createIPAddress(data) {
        return await this.request('POST', '/ip-addresses', data);
    },

    async updateIPAddress(ipId, data) {
        return await this.request('PUT', `/ip-addresses/${ipId}`, data);
    },

    // ============================================
    // WHITELIST ACCOUNTS
    // ============================================

    async getWhitelistAccounts(type = null, status = null) {
        let endpoint = '/whitelist?';
        if (type) endpoint += `type=${type}&`;
        if (status) endpoint += `status=${status}&`;
        return await this.request('GET', endpoint);
    },

    async getWhitelistStats() {
        return await this.request('GET', '/whitelist/stats');
    },

    async createWhitelistAccount(data) {
        return await this.request('POST', '/whitelist', data);
    },

    async deleteWhitelistAccount(whitelistId) {
        return await this.request('DELETE', `/whitelist/${whitelistId}`);
    },

    async bulkCreateWhitelistAccounts(whitelistData) {
        return await this.request('POST', '/whitelist/bulk', whitelistData);
    },

    // ============================================
    // POSTED CONTENT
    // ============================================

    async getPostedContent(accountId = null, status = null) {
        let endpoint = '/posts?';
        if (accountId) endpoint += `account_id=${accountId}&`;
        if (status) endpoint += `status=${status}&`;
        return await this.request('GET', endpoint);
    },

    async getPostsStats(accountId = null) {
        let endpoint = '/posts/stats';
        if (accountId) endpoint += `?account_id=${accountId}`;
        return await this.request('GET', endpoint);
    },

    async createPostedContent(data) {
        return await this.request('POST', '/posts', data);
    },

    async updatePostedContent(postId, data) {
        return await this.request('PUT', `/posts/${postId}`, data);
    },

    // ============================================
    // MESSAGES
    // ============================================

    async getMessages(accountId = null, conversationId = null) {
        let endpoint = '/messages?';
        if (accountId) endpoint += `account_id=${accountId}&`;
        if (conversationId) endpoint += `conversation_id=${conversationId}&`;
        return await this.request('GET', endpoint);
    },

    async getConversations(accountId) {
        return await this.request('GET', `/conversations?account_id=${accountId}`);
    },

    async getMessagesStats(accountId = null) {
        let endpoint = '/messages/stats';
        if (accountId) endpoint += `?account_id=${accountId}`;
        return await this.request('GET', endpoint);
    },

    async createMessage(data) {
        return await this.request('POST', '/messages', data);
    }
};

// Make it available globally
window.AdvancedAPIClient = AdvancedAPIClient;
