/**
 * Bi Ads - File Import Module
 * Author: Bi Ads Team
 * Version: 2.0.0
 * 
 * Handles importing accounts from via.txt and proxies from proxy.txt
 */

const FileImport = {
    apiUrl: 'http://localhost:8000',

    /**
     * Show import accounts modal
     */
    showImportAccountsModal: function() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.id = 'importAccountsModal';
        
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <div class="modal-title">📥 Import tài khoản từ file</div>
                    <button class="modal-close" onclick="document.getElementById('importAccountsModal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="info-box" style="background: #1a1a2e; border-left: 4px solid #667eea; padding: 15px; margin-bottom: 20px;">
                        <h4 style="margin: 0 0 10px 0; color: #667eea;">📝 Định dạng file via.txt</h4>
                        <p style="margin: 5px 0; color: #888; font-size: 13px;">
                            Mỗi dòng chứa thông tin tài khoản phân cách bởi dấu "|":<br>
                            <code style="color: #aaa; background: #0f0f1e; padding: 5px; display: block; margin-top: 5px;">
                                UID|username|2FA_key|cookies|token|email||date
                            </code>
                        </p>
                        <p style="margin: 10px 0 0 0; color: #888; font-size: 12px;">
                            <strong>Ví dụ:</strong><br>
                            <code style="color: #aaa; background: #0f0f1e; padding: 5px; display: block; margin-top: 5px; font-size: 11px; overflow-x: auto;">
                                123456789|user01|ABC123|c_user=123;xs=abc|EAAA...|email@example.com||01/01/2025
                            </code>
                        </p>
                    </div>

                    <div class="input-group">
                        <label>Chọn file via.txt:</label>
                        <input type="file" id="viaFileInput" class="input" accept=".txt" 
                               style="padding: 10px; cursor: pointer;">
                        <small style="color: #888; display: block; margin-top: 5px;">
                            Hỗ trợ file .txt với định dạng via
                        </small>
                    </div>

                    <div id="importPreview" style="display: none; margin-top: 20px;">
                        <div class="card" style="background: #1a1a2e;">
                            <div class="card-header" style="background: #16213e;">
                                📊 Xem trước dữ liệu
                            </div>
                            <div class="card-body" id="previewContent">
                                <!-- Preview will be inserted here -->
                            </div>
                        </div>
                    </div>

                    <div id="importProgress" style="display: none; margin-top: 20px;">
                        <div class="progress-bar">
                            <div id="importProgressBar" class="progress-fill" style="width: 0%;"></div>
                        </div>
                        <p id="importStatus" style="text-align: center; margin-top: 10px; color: #888;">
                            Đang xử lý...
                        </p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="document.getElementById('importAccountsModal').remove()">Hủy</button>
                    <button class="btn-primary" id="btnImportAccounts" onclick="FileImport.importAccounts()" disabled>
                        📥 Import tài khoản
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);

        // Setup file input listener
        document.getElementById('viaFileInput').addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file) {
                await this.previewViaFile(file);
            }
        });
    },

    /**
     * Preview via.txt file content
     */
    previewViaFile: async function(file) {
        const reader = new FileReader();
        
        reader.onload = async (e) => {
            const content = e.target.result;
            const lines = content.split('\n').filter(line => line.trim() && !line.startsWith('#'));
            
            // Parse first few lines for preview
            const previewLines = lines.slice(0, 5);
            let validCount = 0;
            let previewHTML = '<table class="data-table"><thead><tr><th>UID</th><th>Username</th><th>Email</th><th>Phương thức</th></tr></thead><tbody>';
            
            previewLines.forEach(line => {
                const parts = line.split('|');
                if (parts.length >= 6) {
                    const uid = parts[0].trim();
                    const username = parts[1].trim();
                    const email = parts[5].trim();
                    const hasToken = parts[4].trim().length > 0;
                    const hasCookies = parts[3].trim().length > 0;
                    
                    const method = hasCookies ? 'Cookies' : (hasToken ? 'Token' : 'Email');
                    
                    previewHTML += `
                        <tr>
                            <td>${uid}</td>
                            <td>${username}</td>
                            <td>${email || 'N/A'}</td>
                            <td><span class="badge badge-info">${method}</span></td>
                        </tr>
                    `;
                    validCount++;
                }
            });
            
            previewHTML += '</tbody></table>';
            
            if (lines.length > 5) {
                previewHTML += `<p style="text-align: center; margin-top: 10px; color: #888;">... và ${lines.length - 5} tài khoản khác</p>`;
            }
            
            document.getElementById('previewContent').innerHTML = `
                <div style="margin-bottom: 15px;">
                    <span class="badge badge-success">✅ Tổng số: ${lines.length} tài khoản</span>
                    <span class="badge badge-info">📝 Hợp lệ: ${validCount}/${previewLines.length}</span>
                </div>
                ${previewHTML}
            `;
            
            document.getElementById('importPreview').style.display = 'block';
            document.getElementById('btnImportAccounts').disabled = lines.length === 0;
        };
        
        reader.readAsText(file);
    },

    /**
     * Import accounts from via.txt file
     */
    importAccounts: async function() {
        const fileInput = document.getElementById('viaFileInput');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('Vui lòng chọn file!');
            return;
        }

        // Show progress
        document.getElementById('importProgress').style.display = 'block';
        document.getElementById('btnImportAccounts').disabled = true;

        try {
            // Create form data
            const formData = new FormData();
            formData.append('file', file);

            // Update progress
            this.updateProgress(10, 'Đang tải file lên...');

            // Upload to backend
            const response = await fetch(`${this.apiUrl}/api/accounts/import-via`, {
                method: 'POST',
                body: formData
            });

            this.updateProgress(50, 'Đang xử lý dữ liệu...');

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Lỗi import file');
            }

            const result = await response.json();

            this.updateProgress(100, 'Hoàn thành!');

            // Show success message
            setTimeout(() => {
                document.getElementById('importAccountsModal').remove();
                
                // Show success modal
                this.showImportResult(result);
                
                // Reload accounts page
                if (window.BiAds) {
                    BiAds.log('success', `✅ Import thành công ${result.total_imported} tài khoản`);
                    BiAds.loadPage('accounts');
                }
            }, 500);

        } catch (error) {
            this.updateProgress(0, '');
            document.getElementById('importProgress').style.display = 'none';
            document.getElementById('btnImportAccounts').disabled = false;
            
            alert(`❌ Lỗi: ${error.message}`);
            console.error('Import error:', error);
        }
    },

    /**
     * Show import proxies modal
     */
    showImportProxiesModal: function() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.id = 'importProxiesModal';
        
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <div class="modal-title">📥 Import proxy từ file</div>
                    <button class="modal-close" onclick="document.getElementById('importProxiesModal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="info-box" style="background: #1a1a2e; border-left: 4px solid #667eea; padding: 15px; margin-bottom: 20px;">
                        <h4 style="margin: 0 0 10px 0; color: #667eea;">📝 Định dạng file proxy.txt</h4>
                        <p style="margin: 5px 0; color: #888; font-size: 13px;">
                            Mỗi dòng chứa một proxy, hỗ trợ các định dạng:<br>
                            <code style="color: #aaa; background: #0f0f1e; padding: 5px; display: block; margin-top: 5px;">
                                IP:PORT<br>
                                IP:PORT:USERNAME:PASSWORD<br>
                                http://IP:PORT<br>
                                socks5://USERNAME:PASSWORD@IP:PORT
                            </code>
                        </p>
                    </div>

                    <div class="input-group">
                        <label>Chọn file proxy.txt:</label>
                        <input type="file" id="proxyFileInput" class="input" accept=".txt" 
                               style="padding: 10px; cursor: pointer;">
                        <small style="color: #888; display: block; margin-top: 5px;">
                            Hỗ trợ file .txt với danh sách proxy
                        </small>
                    </div>

                    <div id="proxyImportPreview" style="display: none; margin-top: 20px;">
                        <div class="card" style="background: #1a1a2e;">
                            <div class="card-header" style="background: #16213e;">
                                📊 Xem trước dữ liệu
                            </div>
                            <div class="card-body" id="proxyPreviewContent">
                                <!-- Preview will be inserted here -->
                            </div>
                        </div>
                    </div>

                    <div id="proxyImportProgress" style="display: none; margin-top: 20px;">
                        <div class="progress-bar">
                            <div id="proxyImportProgressBar" class="progress-fill" style="width: 0%;"></div>
                        </div>
                        <p id="proxyImportStatus" style="text-align: center; margin-top: 10px; color: #888;">
                            Đang xử lý...
                        </p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="document.getElementById('importProxiesModal').remove()">Hủy</button>
                    <button class="btn-primary" id="btnImportProxies" onclick="FileImport.importProxies()" disabled>
                        📥 Import proxy
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);

        // Setup file input listener
        document.getElementById('proxyFileInput').addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file) {
                await this.previewProxyFile(file);
            }
        });
    },

    /**
     * Preview proxy.txt file content
     */
    previewProxyFile: async function(file) {
        const reader = new FileReader();
        
        reader.onload = async (e) => {
            const content = e.target.result;
            const lines = content.split('\n').filter(line => line.trim() && !line.startsWith('#'));
            
            // Parse first few lines for preview
            const previewLines = lines.slice(0, 5);
            let previewHTML = '<table class="data-table"><thead><tr><th>IP</th><th>Port</th><th>Protocol</th><th>Auth</th></tr></thead><tbody>';
            
            previewLines.forEach(line => {
                // Basic parsing for preview
                let protocol = 'http';
                let cleanLine = line;
                
                if (line.includes('://')) {
                    const parts = line.split('://');
                    protocol = parts[0];
                    cleanLine = parts[1];
                }
                
                const hasAuth = cleanLine.includes('@') || (cleanLine.split(':').length > 2);
                const ipPort = cleanLine.split(':')[0] + ':' + cleanLine.split(':')[1];
                
                previewHTML += `
                    <tr>
                        <td>${ipPort.split(':')[0]}</td>
                        <td>${ipPort.split(':')[1]}</td>
                        <td><span class="badge badge-info">${protocol.toUpperCase()}</span></td>
                        <td>${hasAuth ? '✅ Có' : '❌ Không'}</td>
                    </tr>
                `;
            });
            
            previewHTML += '</tbody></table>';
            
            if (lines.length > 5) {
                previewHTML += `<p style="text-align: center; margin-top: 10px; color: #888;">... và ${lines.length - 5} proxy khác</p>`;
            }
            
            document.getElementById('proxyPreviewContent').innerHTML = `
                <div style="margin-bottom: 15px;">
                    <span class="badge badge-success">✅ Tổng số: ${lines.length} proxy</span>
                </div>
                ${previewHTML}
            `;
            
            document.getElementById('proxyImportPreview').style.display = 'block';
            document.getElementById('btnImportProxies').disabled = lines.length === 0;
        };
        
        reader.readAsText(file);
    },

    /**
     * Import proxies from proxy.txt file
     */
    importProxies: async function() {
        const fileInput = document.getElementById('proxyFileInput');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('Vui lòng chọn file!');
            return;
        }

        // Show progress
        document.getElementById('proxyImportProgress').style.display = 'block';
        document.getElementById('btnImportProxies').disabled = true;

        try {
            // Create form data
            const formData = new FormData();
            formData.append('file', file);

            // Update progress
            this.updateProxyProgress(10, 'Đang tải file lên...');

            // Upload to backend
            const response = await fetch(`${this.apiUrl}/api/proxies/import-txt`, {
                method: 'POST',
                body: formData
            });

            this.updateProxyProgress(50, 'Đang xử lý dữ liệu...');

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Lỗi import file');
            }

            const result = await response.json();

            this.updateProxyProgress(100, 'Hoàn thành!');

            // Show success message
            setTimeout(() => {
                document.getElementById('importProxiesModal').remove();
                
                // Show success modal
                this.showImportResult(result);
                
                // Reload proxy page
                if (window.BiAds) {
                    BiAds.log('success', `✅ Import thành công ${result.total_imported} proxy`);
                    BiAds.loadPage('proxy');
                }
            }, 500);

        } catch (error) {
            this.updateProxyProgress(0, '');
            document.getElementById('proxyImportProgress').style.display = 'none';
            document.getElementById('btnImportProxies').disabled = false;
            
            alert(`❌ Lỗi: ${error.message}`);
            console.error('Import error:', error);
        }
    },

    /**
     * Update import progress
     */
    updateProgress: function(percent, status) {
        document.getElementById('importProgressBar').style.width = percent + '%';
        document.getElementById('importStatus').textContent = status;
    },

    /**
     * Update proxy import progress
     */
    updateProxyProgress: function(percent, status) {
        document.getElementById('proxyImportProgressBar').style.width = percent + '%';
        document.getElementById('proxyImportStatus').textContent = status;
    },

    /**
     * Show import result modal
     */
    showImportResult: function(result) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.id = 'importResultModal';
        
        const stats = result.statistics || {};
        
        modal.innerHTML = `
            <div class="modal" style="max-width: 600px;">
                <div class="modal-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <div class="modal-title">✅ Import thành công!</div>
                    <button class="modal-close" onclick="document.getElementById('importResultModal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div style="text-align: center; padding: 20px;">
                        <div style="font-size: 64px; margin-bottom: 20px;">🎉</div>
                        <h2 style="margin: 0 0 10px 0; color: #667eea;">${result.message}</h2>
                        <p style="color: #888; margin: 0;">
                            Đã import ${result.total_imported} / ${result.total_parsed} mục
                        </p>
                    </div>

                    ${stats.total ? `
                        <div class="card" style="background: #1a1a2e; margin-top: 20px;">
                            <div class="card-header">📊 Chi tiết</div>
                            <div class="card-body">
                                <div class="grid-2">
                                    ${stats.with_cookies ? `<div>✅ Có cookies: <strong>${stats.with_cookies}</strong></div>` : ''}
                                    ${stats.with_token ? `<div>🔑 Có token: <strong>${stats.with_token}</strong></div>` : ''}
                                    ${stats.with_2fa ? `<div>🔒 Có 2FA: <strong>${stats.with_2fa}</strong></div>` : ''}
                                    ${stats.with_email ? `<div>📧 Có email: <strong>${stats.with_email}</strong></div>` : ''}
                                    ${stats.http ? `<div>🌐 HTTP: <strong>${stats.http}</strong></div>` : ''}
                                    ${stats.socks5 ? `<div>🔒 SOCKS5: <strong>${stats.socks5}</strong></div>` : ''}
                                    ${stats.with_auth ? `<div>🔐 Có auth: <strong>${stats.with_auth}</strong></div>` : ''}
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
                <div class="modal-footer">
                    <button class="btn-primary" onclick="document.getElementById('importResultModal').remove()" style="width: 100%;">
                        Đóng
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
};

// Make it globally available
window.FileImport = FileImport;
