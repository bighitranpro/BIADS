/**
 * Modal Confirmation Component
 * Reusable modal dialogs for user confirmations
 */

const ModalConfirmation = {
    activeModal: null,
    
    /**
     * Show confirmation modal
     * @param {Object} options - Modal configuration
     * @param {string} options.title - Modal title
     * @param {string} options.message - Modal message
     * @param {string} options.type - Modal type (danger, warning, info, success)
     * @param {string} options.confirmText - Confirm button text
     * @param {string} options.cancelText - Cancel button text
     * @param {Function} options.onConfirm - Callback when confirmed
     * @param {Function} options.onCancel - Callback when cancelled
     */
    show(options) {
        const {
            title = 'Xác nhận',
            message = 'Bạn có chắc chắn muốn thực hiện hành động này?',
            type = 'warning', // danger, warning, info, success
            confirmText = 'Xác nhận',
            cancelText = 'Hủy',
            onConfirm = () => {},
            onCancel = () => {},
            details = null // Optional detailed info
        } = options;
        
        // Remove existing modal if any
        this.close();
        
        // Create modal element
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-container modal-${type}">
                <div class="modal-header">
                    <div class="modal-icon">${this.getIcon(type)}</div>
                    <h3 class="modal-title">${title}</h3>
                </div>
                <div class="modal-body">
                    <p class="modal-message">${message}</p>
                    ${details ? `<div class="modal-details">${details}</div>` : ''}
                </div>
                <div class="modal-footer">
                    <button class="modal-btn modal-btn-cancel">${cancelText}</button>
                    <button class="modal-btn modal-btn-confirm modal-btn-${type}">${confirmText}</button>
                </div>
            </div>
        `;
        
        // Add event listeners
        const cancelBtn = modal.querySelector('.modal-btn-cancel');
        const confirmBtn = modal.querySelector('.modal-btn-confirm');
        
        cancelBtn.addEventListener('click', () => {
            this.close();
            onCancel();
        });
        
        confirmBtn.addEventListener('click', () => {
            this.close();
            onConfirm();
        });
        
        // Close on overlay click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.close();
                onCancel();
            }
        });
        
        // Close on ESC key
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                this.close();
                onCancel();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
        
        // Add to DOM
        document.body.appendChild(modal);
        this.activeModal = modal;
        
        // Trigger animation
        setTimeout(() => modal.classList.add('active'), 10);
    },
    
    /**
     * Show danger confirmation (for destructive actions)
     */
    showDanger(options) {
        return this.show({
            ...options,
            type: 'danger',
            confirmText: options.confirmText || 'Xóa'
        });
    },
    
    /**
     * Show warning confirmation
     */
    showWarning(options) {
        return this.show({
            ...options,
            type: 'warning',
            confirmText: options.confirmText || 'Tiếp tục'
        });
    },
    
    /**
     * Show info confirmation
     */
    showInfo(options) {
        return this.show({
            ...options,
            type: 'info',
            confirmText: options.confirmText || 'OK'
        });
    },
    
    /**
     * Show success confirmation
     */
    showSuccess(options) {
        return this.show({
            ...options,
            type: 'success',
            confirmText: options.confirmText || 'Đồng ý'
        });
    },
    
    /**
     * Show input modal
     */
    showInput(options) {
        const {
            title = 'Nhập thông tin',
            message = '',
            placeholder = '',
            defaultValue = '',
            type = 'text',
            required = true,
            onConfirm = () => {},
            onCancel = () => {}
        } = options;
        
        this.close();
        
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-container modal-input">
                <div class="modal-header">
                    <div class="modal-icon">✏️</div>
                    <h3 class="modal-title">${title}</h3>
                </div>
                <div class="modal-body">
                    ${message ? `<p class="modal-message">${message}</p>` : ''}
                    <input 
                        type="${type}" 
                        class="modal-input" 
                        placeholder="${placeholder}"
                        value="${defaultValue}"
                        ${required ? 'required' : ''}
                    />
                </div>
                <div class="modal-footer">
                    <button class="modal-btn modal-btn-cancel">Hủy</button>
                    <button class="modal-btn modal-btn-confirm modal-btn-info">Xác nhận</button>
                </div>
            </div>
        `;
        
        const input = modal.querySelector('.modal-input');
        const cancelBtn = modal.querySelector('.modal-btn-cancel');
        const confirmBtn = modal.querySelector('.modal-btn-confirm');
        
        cancelBtn.addEventListener('click', () => {
            this.close();
            onCancel();
        });
        
        confirmBtn.addEventListener('click', () => {
            const value = input.value.trim();
            if (required && !value) {
                input.classList.add('error');
                input.focus();
                return;
            }
            this.close();
            onConfirm(value);
        });
        
        // Submit on Enter
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                confirmBtn.click();
            }
        });
        
        // Close on ESC
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                this.close();
                onCancel();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
        
        document.body.appendChild(modal);
        this.activeModal = modal;
        setTimeout(() => {
            modal.classList.add('active');
            input.focus();
        }, 10);
    },
    
    /**
     * Close active modal
     */
    close() {
        if (this.activeModal) {
            this.activeModal.classList.remove('active');
            setTimeout(() => {
                this.activeModal.remove();
                this.activeModal = null;
            }, 300);
        }
    },
    
    /**
     * Get icon for modal type
     */
    getIcon(type) {
        const icons = {
            danger: '⚠️',
            warning: '⚡',
            info: 'ℹ️',
            success: '✅'
        };
        return icons[type] || icons.info;
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModalConfirmation;
}
