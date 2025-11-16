// UI Components for Bi Ads Multi Tool PRO v3.0

const components = {
    // Create modal
    createModal(title, bodyHtml, buttons = []) {
        const modalContainer = document.getElementById('modalContainer');
        if (!modalContainer) return null;

        const modalId = `modal_${Date.now()}`;
        
        const buttonsHtml = buttons.map(btn => `
            <button class="btn ${btn.class || 'btn-primary'}" data-action="${btn.action || 'close'}">
                ${btn.text || 'OK'}
            </button>
        `).join('');

        modalContainer.innerHTML = `
            <div class="modal-overlay" id="${modalId}">
                <div class="modal">
                    <div class="modal-header">${title}</div>
                    <div class="modal-body">${bodyHtml}</div>
                    <div class="modal-footer">
                        ${buttonsHtml}
                    </div>
                </div>
            </div>
        `;

        const modalEl = document.getElementById(modalId);
        
        // Setup button handlers
        buttons.forEach((btn, index) => {
            const btnEl = modalEl.querySelectorAll('.modal-footer button')[index];
            if (btnEl && btn.onClick) {
                btnEl.addEventListener('click', btn.onClick);
            }
        });

        // Close on overlay click
        modalEl.addEventListener('click', (e) => {
            if (e.target === modalEl) {
                modal.close();
            }
        });

        const modal = {
            element: modalEl,
            close: () => {
                modalEl.style.animation = 'fadeIn 0.3s ease reverse';
                setTimeout(() => modalContainer.innerHTML = '', 300);
            }
        };

        return modal;
    },

    // Create form field
    createFormField(config) {
        const {
            type = 'text',
            label,
            name,
            value = '',
            placeholder = '',
            required = false,
            options = []
        } = config;

        let inputHtml = '';

        switch (type) {
            case 'textarea':
                inputHtml = `<textarea class="form-textarea" name="${name}" placeholder="${placeholder}" ${required ? 'required' : ''}>${value}</textarea>`;
                break;
            case 'select':
                inputHtml = `
                    <select class="form-select" name="${name}" ${required ? 'required' : ''}>
                        ${options.map(opt => `<option value="${opt.value}" ${opt.value === value ? 'selected' : ''}>${opt.label}</option>`).join('')}
                    </select>
                `;
                break;
            default:
                inputHtml = `<input type="${type}" class="form-input" name="${name}" value="${value}" placeholder="${placeholder}" ${required ? 'required' : ''}>`;
        }

        return `
            <div class="form-group">
                <label class="form-label">${label}${required ? ' <span style="color: #e74c3c;">*</span>' : ''}</label>
                ${inputHtml}
            </div>
        `;
    },

    // Create data table
    createTable(columns, data, actions = []) {
        if (!data || data.length === 0) {
            return '<p style="text-align: center; color: #888; padding: 20px;">Không có dữ liệu</p>';
        }

        const headerHtml = columns.map(col => `<th>${col.label}</th>`).join('');
        const actionsHeader = actions.length > 0 ? '<th style="width: 150px;">Thao tác</th>' : '';

        const rowsHtml = data.map(row => {
            const cellsHtml = columns.map(col => {
                let value = row[col.field];
                if (col.render) {
                    value = col.render(value, row);
                }
                return `<td>${value || ''}</td>`;
            }).join('');

            const actionsHtml = actions.length > 0 ? `
                <td>
                    <div class="action-buttons">
                        ${actions.map(action => `
                            <button class="btn btn-small ${action.class || 'btn-primary'}" 
                                    data-action="${action.name}" 
                                    data-id="${row.id}">
                                ${action.icon || ''} ${action.label}
                            </button>
                        `).join('')}
                    </div>
                </td>
            ` : '';

            return `<tr>${cellsHtml}${actionsHtml}</tr>`;
        }).join('');

        return `
            <table class="data-table">
                <thead>
                    <tr>${headerHtml}${actionsHeader}</tr>
                </thead>
                <tbody>
                    ${rowsHtml}
                </tbody>
            </table>
        `;
    },

    // Create stats card
    createStatsCard(value, label, icon = '📊') {
        return `
            <div class="stat-card">
                <div class="stat-value">${icon} ${value}</div>
                <div class="stat-label">${label}</div>
            </div>
        `;
    },

    // Create card
    createCard(title, bodyHtml, actions = '') {
        return `
            <div class="card">
                <div class="card-header">
                    ${title}
                    ${actions ? `<div style="float: right;">${actions}</div>` : ''}
                </div>
                <div class="card-body">${bodyHtml}</div>
            </div>
        `;
    },

    // Create filter form
    createFilterForm(filters) {
        const fieldsHtml = filters.map(filter => 
            this.createFormField(filter)
        ).join('');

        return `
            <form id="filterForm" class="card" style="margin-bottom: 20px;">
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        ${fieldsHtml}
                    </div>
                    <div style="margin-top: 15px; display: flex; gap: 10px;">
                        <button type="submit" class="btn btn-primary">🔍 Tìm kiếm</button>
                        <button type="button" class="btn btn-secondary" id="btnResetFilter">↺ Đặt lại</button>
                    </div>
                </div>
            </form>
        `;
    },

    // Create action bar
    createActionBar(actions) {
        return actions.map(action => `
            <button class="btn ${action.class || 'btn-primary'}" id="${action.id}">
                ${action.icon || ''} ${action.label}
            </button>
        `).join('');
    },

    // Create pagination (simple)
    createPagination(currentPage, totalPages, onPageChange) {
        if (totalPages <= 1) return '';

        const pages = [];
        for (let i = 1; i <= totalPages; i++) {
            pages.push(`
                <button class="btn btn-small ${i === currentPage ? 'btn-primary' : 'btn-secondary'}" 
                        data-page="${i}">
                    ${i}
                </button>
            `);
        }

        return `
            <div style="display: flex; justify-content: center; gap: 5px; margin-top: 20px;">
                <button class="btn btn-small btn-secondary" data-page="${currentPage - 1}" ${currentPage === 1 ? 'disabled' : ''}>
                    ← Trước
                </button>
                ${pages.join('')}
                <button class="btn btn-small btn-secondary" data-page="${currentPage + 1}" ${currentPage === totalPages ? 'disabled' : ''}>
                    Sau →
                </button>
            </div>
        `;
    },

    // Create progress bar
    createProgressBar(percentage, label = '') {
        return `
            <div style="margin: 15px 0;">
                ${label ? `<div style="margin-bottom: 5px; color: #888;">${label}</div>` : ''}
                <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 20px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; width: ${percentage}%; transition: width 0.3s ease;"></div>
                </div>
                <div style="text-align: right; margin-top: 5px; color: #888; font-size: 12px;">${percentage}%</div>
            </div>
        `;
    }
};

// Make components available globally
window.components = components;
