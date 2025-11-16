// Utility functions for Bi Ads Multi Tool PRO v3.0

const utils = {
    // Format date to readable format
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Format relative time (e.g., "2 hours ago")
    formatRelativeTime(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffSecs < 60) return 'Vừa xong';
        if (diffMins < 60) return `${diffMins} phút trước`;
        if (diffHours < 24) return `${diffHours} giờ trước`;
        if (diffDays < 30) return `${diffDays} ngày trước`;
        return this.formatDate(dateString);
    },

    // Escape HTML to prevent XSS
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Copy to clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            utils.showToast('Đã sao chép vào clipboard', 'success');
            return true;
        } catch (error) {
            console.error('Copy failed:', error);
            utils.showToast('Không thể sao chép', 'error');
            return false;
        }
    },

    // Download file
    downloadFile(content, filename, mimeType = 'text/plain') {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    },

    // Parse CSV
    parseCSV(text) {
        const lines = text.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        const data = [];
        
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim());
            const obj = {};
            headers.forEach((header, index) => {
                obj[header] = values[index] || '';
            });
            data.push(obj);
        }
        
        return data;
    },

    // Generate CSV
    generateCSV(data, headers) {
        if (!data || data.length === 0) return '';
        
        const csvHeaders = headers || Object.keys(data[0]);
        const csvRows = [csvHeaders.join(',')];
        
        data.forEach(row => {
            const values = csvHeaders.map(header => {
                const value = row[header] || '';
                // Escape commas and quotes
                return `"${String(value).replace(/"/g, '""')}"`;
            });
            csvRows.push(values.join(','));
        });
        
        return csvRows.join('\n');
    },

    // Show toast notification
    showToast(message, type = 'info', title = '') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        const titles = {
            success: 'Thành công',
            error: 'Lỗi',
            warning: 'Cảnh báo',
            info: 'Thông báo'
        };

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-icon">${icons[type]}</div>
            <div class="toast-content">
                <div class="toast-title">${title || titles[type]}</div>
                <div class="toast-message">${utils.escapeHtml(message)}</div>
            </div>
        `;

        container.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, CONFIG.TOAST_DURATION);
    },

    // Show loading spinner
    showLoading(element) {
        if (!element) return;
        element.innerHTML = `
            <div style="text-align: center; padding: 40px;">
                <div class="spinner" style="width: 40px; height: 40px;"></div>
                <p style="margin-top: 15px; color: #888;">Đang tải...</p>
            </div>
        `;
    },

    // Show empty state
    showEmptyState(element, icon, title, message, action = null) {
        if (!element) return;
        element.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">${icon}</div>
                <div class="empty-state-title">${title}</div>
                <div class="empty-state-message">${message}</div>
                ${action ? `<div style="margin-top: 20px;">${action}</div>` : ''}
            </div>
        `;
    },

    // Confirm dialog
    async confirm(message, title = 'Xác nhận') {
        return new Promise((resolve) => {
            const modal = components.createModal(
                title,
                `<p>${utils.escapeHtml(message)}</p>`,
                [
                    {
                        text: 'Hủy',
                        class: 'btn-secondary',
                        onClick: () => {
                            modal.close();
                            resolve(false);
                        }
                    },
                    {
                        text: 'Xác nhận',
                        class: 'btn-primary',
                        onClick: () => {
                            modal.close();
                            resolve(true);
                        }
                    }
                ]
            );
        });
    },

    // Get badge HTML for status
    getStatusBadge(status, type = 'account') {
        const colorMap = CONFIG[`${type.toUpperCase()}_STATUS_COLORS`] || {};
        const color = colorMap[status] || 'info';
        return `<span class="badge badge-${color}">${status}</span>`;
    },

    // Parse proxy string (ip:port:username:password)
    parseProxyString(proxyStr) {
        const parts = proxyStr.split(':');
        if (parts.length < 2) return null;
        
        return {
            ip: parts[0].trim(),
            port: parseInt(parts[1]),
            username: parts[2]?.trim() || '',
            password: parts[3]?.trim() || '',
            protocol: 'http'
        };
    },

    // Format proxy string
    formatProxyString(proxy) {
        if (!proxy) return 'N/A';
        let str = `${proxy.ip}:${proxy.port}`;
        if (proxy.username) {
            str += `:${proxy.username}`;
            if (proxy.password) {
                str += `:${proxy.password}`;
            }
        }
        return str;
    }
};

// Make utils available globally
window.utils = utils;
