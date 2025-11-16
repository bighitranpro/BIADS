// Tasks Module
const Tasks = {
    data: { tasks: [] },
    
    async init() {
        await this.loadData();
        this.render();
    },
    
    async loadData() {
        try {
            this.data.tasks = await apiClient.getTasks();
        } catch (error) {
            utils.showToast('Không thể tải danh sách tác vụ', 'error');
        }
    },
    
    render() {
        const content = document.getElementById('contentBody');
        const actions = document.getElementById('contentActions');
        
        actions.innerHTML = components.createActionBar([
            { id: 'btnAddTask', label: 'Tạo tác vụ', icon: '➕', class: 'btn-primary' },
            { id: 'btnRefreshTasks', label: 'Làm mới', icon: '↻', class: 'btn-secondary' }
        ]);
        
        content.innerHTML = `
            <div class="card">
                <div class="card-header">📋 Danh sách tác vụ (${this.data.tasks.length})</div>
                <div class="card-body">${this.renderTable()}</div>
            </div>
        `;
        
        this.setupEventListeners();
    },
    
    renderTable() {
        const columns = [
            { field: 'id', label: 'ID' },
            { field: 'task_type', label: 'Loại tác vụ' },
            { field: 'account_id', label: 'Account ID' },
            { 
                field: 'status', 
                label: 'Trạng thái',
                render: (value) => utils.getStatusBadge(value, 'task')
            },
            { field: 'progress', label: 'Tiến độ', render: (v) => `${v || 0}%` },
            { field: 'created_at', label: 'Ngày tạo', render: (v) => utils.formatDate(v) }
        ];
        
        const actions = [
            { name: 'view', label: 'Chi tiết', icon: '👁️', class: 'btn-info' },
            { name: 'delete', label: 'Xóa', icon: '🗑️', class: 'btn-danger' }
        ];
        
        return components.createTable(columns, this.data.tasks, actions);
    },
    
    setupEventListeners() {
        document.getElementById('btnAddTask')?.addEventListener('click', () => {
            utils.showToast('Tính năng đang phát triển', 'info');
        });
        document.getElementById('btnRefreshTasks')?.addEventListener('click', () => this.init());
        
        document.querySelectorAll('[data-action="delete"]').forEach(btn => {
            btn.addEventListener('click', async () => {
                if (await utils.confirm('Xóa tác vụ này?')) {
                    await apiClient.deleteTask(parseInt(btn.dataset.id));
                    utils.showToast('Đã xóa tác vụ', 'success');
                    await this.init();
                }
            });
        });
    }
};

window.Tasks = Tasks;
