// API Client for Bi Ads Multi Tool PRO v3.0

const apiClient = {
    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${window.API_URL}${endpoint}`;
        const config = {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Remove body for GET requests
        if (config.method === 'GET') {
            delete config.body;
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            // Handle empty responses
            const text = await response.text();
            return text ? JSON.parse(text) : {};
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // Health check
    async healthCheck() {
        return await this.request('/health');
    },

    // Account operations
    async getAccounts() {
        return await this.request('/api/accounts');
    },

    async getAccount(id) {
        return await this.request(`/api/accounts/${id}`);
    },

    async createAccount(accountData) {
        return await this.request('/api/accounts', {
            method: 'POST',
            body: JSON.stringify(accountData)
        });
    },

    async updateAccount(id, accountData) {
        return await this.request(`/api/accounts/${id}`, {
            method: 'PUT',
            body: JSON.stringify(accountData)
        });
    },

    async deleteAccount(id) {
        return await this.request(`/api/accounts/${id}`, {
            method: 'DELETE'
        });
    },

    async assignProxy(accountId, proxyId) {
        return await this.request(`/api/accounts/${accountId}/assign-proxy?proxy_id=${proxyId}`, {
            method: 'PUT'
        });
    },

    async removeProxy(accountId) {
        return await this.request(`/api/accounts/${accountId}/remove-proxy`, {
            method: 'PUT'
        });
    },

    // Proxy operations
    async getProxies() {
        return await this.request('/api/proxies');
    },

    async getProxy(id) {
        return await this.request(`/api/proxies/${id}`);
    },

    async createProxy(proxyData) {
        return await this.request('/api/proxies', {
            method: 'POST',
            body: JSON.stringify(proxyData)
        });
    },

    async updateProxy(id, proxyData) {
        return await this.request(`/api/proxies/${id}`, {
            method: 'PUT',
            body: JSON.stringify(proxyData)
        });
    },

    async deleteProxy(id) {
        return await this.request(`/api/proxies/${id}`, {
            method: 'DELETE'
        });
    },

    async importProxies(proxies) {
        return await this.request('/api/proxies/import', {
            method: 'POST',
            body: JSON.stringify({ proxies })
        });
    },

    // Task operations
    async getTasks() {
        return await this.request('/api/tasks');
    },

    async getTask(id) {
        return await this.request(`/api/tasks/${id}`);
    },

    async createTask(taskData) {
        return await this.request('/api/tasks', {
            method: 'POST',
            body: JSON.stringify(taskData)
        });
    },

    async deleteTask(id) {
        return await this.request(`/api/tasks/${id}`, {
            method: 'DELETE'
        });
    },

    // Log operations
    async getLogs(limit = 100) {
        return await this.request(`/api/logs?limit=${limit}`);
    },

    async clearLogs() {
        return await this.request('/api/logs', {
            method: 'DELETE'
        });
    },

    // Statistics
    async getStats() {
        return await this.request('/api/stats');
    },

    // File import/export
    async importAccounts(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        return await fetch(`${window.API_URL}/api/accounts/import`, {
            method: 'POST',
            body: formData
        }).then(res => res.json());
    },

    async exportAccounts() {
        window.open(`${window.API_URL}/api/accounts/export`, '_blank');
    },

    async exportProxies() {
        window.open(`${window.API_URL}/api/proxies/export`, '_blank');
    }
};

// Make apiClient available globally
window.apiClient = apiClient;
