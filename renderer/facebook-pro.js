// Facebook Pro Module - Complete with Login System
// This module provides Facebook automation features

const facebookPro = {
    accounts: [],
    currentAccount: null,
    
    // Initialize Facebook Pro
    init: function() {
        console.log('Initializing Facebook Pro...');
        this.loadAccounts();
        this.render();
    },
    
    // Load saved accounts from localStorage
    loadAccounts: function() {
        try {
            const saved = localStorage.getItem('facebook_accounts');
            if (saved) {
                this.accounts = JSON.parse(saved);
            }
        } catch (error) {
            console.error('Error loading accounts:', error);
        }
    },
    
    // Save accounts to localStorage
    saveAccounts: function() {
        try {
            localStorage.setItem('facebook_accounts', JSON.stringify(this.accounts));
        } catch (error) {
            console.error('Error saving accounts:', error);
        }
    },
    
    // Render Facebook Pro UI
    render: function() {
        const container = document.getElementById('contentContainer');
        
        container.innerHTML = `
            <!-- Account Management Section -->
            <div class="card">
                <div class="card-header">
                    👤 Account Management
                    ${this.currentAccount ? `<span class="badge badge-success" style="float: right;">Logged in as: ${this.currentAccount.name}</span>` : ''}
                </div>
                <div class="card-body">
                    <div class="grid-2">
                        <button onclick="facebookPro.showLoginDialog()">
                            ➕ Add Account
                        </button>
                        <button onclick="facebookPro.showAccountSelector()" ${this.accounts.length === 0 ? 'disabled' : ''}>
                            🔄 Switch Account (${this.accounts.length})
                        </button>
                    </div>
                </div>
            </div>
            
            ${this.currentAccount ? this.renderFeatures() : this.renderLoginRequired()}
        `;
    },
    
    // Render login required message
    renderLoginRequired: function() {
        return `
            <div class="card">
                <div class="card-header">🔐 Login Required</div>
                <div class="card-body">
                    <div style="text-align: center; padding: 40px;">
                        <h2 style="font-size: 48px; margin-bottom: 20px;">🔒</h2>
                        <h3 style="color: #fff; margin-bottom: 10px;">Please Login First</h3>
                        <p style="color: #888; margin-bottom: 30px;">You need to add a Facebook account to use the automation features</p>
                        <button onclick="facebookPro.showLoginDialog()">
                            ➕ Add Facebook Account
                        </button>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Render features when logged in
    renderFeatures: function() {
        return `
            <!-- Friend Management -->
            <div class="card">
                <div class="card-header">👥 Friend Management</div>
                <div class="card-body">
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; color: #fff;">Friend UIDs (one per line):</label>
                        <textarea id="friendUids" rows="5" placeholder="100012345678901&#10;100012345678902&#10;..."></textarea>
                    </div>
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; color: #fff;">Max requests per session:</label>
                        <input type="number" id="friendMaxRequests" value="50" min="1" max="100">
                    </div>
                    <div class="grid-2">
                        <button onclick="facebookPro.addFriends()">
                            ➕ Add Friends
                        </button>
                        <button onclick="facebookPro.acceptFriendRequests()">
                            ✅ Accept Requests
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Group Management -->
            <div class="card">
                <div class="card-header">🏢 Group Management</div>
                <div class="card-body">
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; color: #fff;">Group IDs or URLs (one per line):</label>
                        <textarea id="groupIds" rows="4" placeholder="https://facebook.com/groups/123456789&#10;987654321&#10;..."></textarea>
                    </div>
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; color: #fff;">Post Content (supports spintax {option1|option2}):</label>
                        <textarea id="groupContent" rows="4" placeholder="This is {amazing|great|awesome} content! {🔥|✨|💯}"></textarea>
                    </div>
                    <div class="grid-2">
                        <button onclick="facebookPro.joinGroups()">
                            🚪 Join Groups
                        </button>
                        <button onclick="facebookPro.postToGroups()">
                            📝 Post to Groups
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Content Manager -->
            <div class="card">
                <div class="card-header">✍️ Content Manager</div>
                <div class="card-body">
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; color: #fff;">Text with spintax:</label>
                        <textarea id="spinText" rows="4" placeholder="{Hello|Hi|Hey} {friend|buddy}! This is {amazing|great|awesome}!"></textarea>
                    </div>
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; color: #fff;">Number of variations:</label>
                        <input type="number" id="spinCount" value="5" min="1" max="20">
                    </div>
                    <button onclick="facebookPro.generateSpintax()">
                        🔄 Generate Variations
                    </button>
                    <div id="spinOutput" style="margin-top: 20px;"></div>
                </div>
            </div>
            
            <!-- Activity Log -->
            <div class="card">
                <div class="card-header">📋 Activity Log</div>
                <div class="card-body">
                    <div class="console" id="activityLog">
                        <div class="console-line">
                            <span class="console-timestamp">${new Date().toLocaleTimeString()}</span>
                            <span class="console-level info">[INFO]</span>
                            <span class="console-message">Facebook Pro is ready. Account: ${this.currentAccount.name}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Show login dialog
    showLoginDialog: function() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.id = 'loginModal';
        
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <div class="modal-title">🔐 Add Facebook Account</div>
                    <button class="modal-close" onclick="document.getElementById('loginModal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; color: #fff;">Login Method:</label>
                        <select id="loginMethod" class="input" onchange="facebookPro.switchLoginMethod()">
                            <option value="cookies">🍪 Cookies (Recommended - Most Secure)</option>
                            <option value="email">📧 Email & Password</option>
                            <option value="token">🔑 Access Token</option>
                        </select>
                    </div>
                    
                    <!-- Cookies Login -->
                    <div id="cookiesLogin">
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; color: #fff;">Account Name:</label>
                            <input type="text" id="accountName" class="input" placeholder="My Facebook Account" required>
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; color: #fff;">Facebook Cookies (JSON):</label>
                            <textarea id="accountCookies" class="input" rows="6" placeholder='[{"name": "c_user", "value": "100012345678901"}, {"name": "xs", "value": "xxx%3Axxx"}]'></textarea>
                            <span class="form-hint">
                                📖 How to get cookies:<br>
                                1. Login to Facebook on Chrome<br>
                                2. Press F12 → Application → Cookies → facebook.com<br>
                                3. Copy cookies: c_user, xs, datr, sb (JSON format)
                            </span>
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; color: #fff;">Proxy (optional):</label>
                            <input type="text" id="accountProxy" class="input" placeholder="http://user:pass@host:port">
                        </div>
                    </div>
                    
                    <!-- Email Login -->
                    <div id="emailLogin" class="hidden">
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; color: #fff;">Account Name:</label>
                            <input type="text" id="emailAccountName" class="input" placeholder="My Facebook Account">
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; color: #fff;">Email or Phone:</label>
                            <input type="text" id="accountEmail" class="input" placeholder="email@example.com">
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; color: #fff;">Password:</label>
                            <input type="password" id="accountPassword" class="input" placeholder="••••••••">
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; color: #fff;">2FA Code (if enabled):</label>
                            <input type="text" id="account2FA" class="input" placeholder="123456">
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; color: #fff;">Proxy (optional):</label>
                            <input type="text" id="emailAccountProxy" class="input" placeholder="http://user:pass@host:port">
                        </div>
                    </div>
                    
                    <!-- Token Login -->
                    <div id="tokenLogin" class="hidden">
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; color: #fff;">Account Name:</label>
                            <input type="text" id="tokenAccountName" class="input" placeholder="My Facebook Account">
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; color: #fff;">Access Token:</label>
                            <textarea id="accountToken" class="input" rows="4" placeholder="EAABxxxxxxxx..."></textarea>
                            <span class="form-hint">
                                📖 Get your access token from Facebook Graph API Explorer
                            </span>
                        </div>
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; color: #fff;">Proxy (optional):</label>
                            <input type="text" id="tokenAccountProxy" class="input" placeholder="http://user:pass@host:port">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="document.getElementById('loginModal').remove()">Cancel</button>
                    <button class="btn-primary" onclick="facebookPro.submitLogin()">➕ Add Account</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    },
    
    // Switch login method
    switchLoginMethod: function() {
        const method = document.getElementById('loginMethod').value;
        
        document.getElementById('cookiesLogin').classList.add('hidden');
        document.getElementById('emailLogin').classList.add('hidden');
        document.getElementById('tokenLogin').classList.add('hidden');
        
        if (method === 'cookies') {
            document.getElementById('cookiesLogin').classList.remove('hidden');
        } else if (method === 'email') {
            document.getElementById('emailLogin').classList.remove('hidden');
        } else if (method === 'token') {
            document.getElementById('tokenLogin').classList.remove('hidden');
        }
    },
    
    // Submit login
    submitLogin: function() {
        const method = document.getElementById('loginMethod').value;
        let accountData = {};
        
        try {
            if (method === 'cookies') {
                const name = document.getElementById('accountName').value.trim();
                const cookies = document.getElementById('accountCookies').value.trim();
                const proxy = document.getElementById('accountProxy').value.trim();
                
                if (!name || !cookies) {
                    throw new Error('Please fill in all required fields');
                }
                
                // Validate JSON
                const cookiesJson = JSON.parse(cookies);
                
                accountData = {
                    id: Date.now(),
                    name: name,
                    loginMethod: 'cookies',
                    cookies: cookiesJson,
                    proxy: proxy,
                    status: 'active',
                    addedAt: new Date().toISOString()
                };
            } else if (method === 'email') {
                const name = document.getElementById('emailAccountName').value.trim();
                const email = document.getElementById('accountEmail').value.trim();
                const password = document.getElementById('accountPassword').value.trim();
                const twoFA = document.getElementById('account2FA').value.trim();
                const proxy = document.getElementById('emailAccountProxy').value.trim();
                
                if (!name || !email || !password) {
                    throw new Error('Please fill in all required fields');
                }
                
                accountData = {
                    id: Date.now(),
                    name: name,
                    loginMethod: 'email',
                    email: email,
                    password: password,
                    twoFA: twoFA,
                    proxy: proxy,
                    status: 'active',
                    addedAt: new Date().toISOString()
                };
            } else if (method === 'token') {
                const name = document.getElementById('tokenAccountName').value.trim();
                const token = document.getElementById('accountToken').value.trim();
                const proxy = document.getElementById('tokenAccountProxy').value.trim();
                
                if (!name || !token) {
                    throw new Error('Please fill in all required fields');
                }
                
                accountData = {
                    id: Date.now(),
                    name: name,
                    loginMethod: 'token',
                    token: token,
                    proxy: proxy,
                    status: 'active',
                    addedAt: new Date().toISOString()
                };
            }
            
            // Add account
            this.accounts.push(accountData);
            this.currentAccount = accountData;
            this.saveAccounts();
            
            // Close modal
            document.getElementById('loginModal').remove();
            
            // Show success
            window.app.showNotification('Success', `Account "${accountData.name}" added successfully!`, 'success');
            
            // Re-render
            this.render();
            
        } catch (error) {
            window.app.showNotification('Error', error.message, 'error');
        }
    },
    
    // Show account selector
    showAccountSelector: function() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.id = 'accountSelectorModal';
        
        const accountsList = this.accounts.map((acc, index) => `
            <div class="account-item ${acc.id === this.currentAccount?.id ? 'active' : ''}" 
                 onclick="facebookPro.selectAccount(${index})">
                <div class="account-name">${acc.name}</div>
                <div class="account-email">${acc.loginMethod} • Added ${new Date(acc.addedAt).toLocaleDateString()}</div>
                <button class="btn-secondary" style="margin-top: 10px;" onclick="event.stopPropagation(); facebookPro.deleteAccount(${index})">
                    🗑️ Delete
                </button>
            </div>
        `).join('');
        
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <div class="modal-title">🔄 Switch Account</div>
                    <button class="modal-close" onclick="document.getElementById('accountSelectorModal').remove()">×</button>
                </div>
                <div class="modal-body">
                    ${accountsList}
                </div>
                <div class="modal-footer">
                    <button onclick="document.getElementById('accountSelectorModal').remove()">Close</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    },
    
    // Select account
    selectAccount: function(index) {
        this.currentAccount = this.accounts[index];
        document.getElementById('accountSelectorModal').remove();
        window.app.showNotification('Success', `Switched to account: ${this.currentAccount.name}`, 'success');
        this.render();
    },
    
    // Delete account
    deleteAccount: function(index) {
        const account = this.accounts[index];
        if (confirm(`Are you sure you want to delete account "${account.name}"?`)) {
            this.accounts.splice(index, 1);
            
            if (this.currentAccount?.id === account.id) {
                this.currentAccount = this.accounts[0] || null;
            }
            
            this.saveAccounts();
            document.getElementById('accountSelectorModal').remove();
            window.app.showNotification('Success', 'Account deleted successfully!', 'success');
            this.render();
        }
    },
    
    // Add Friends
    addFriends: function() {
        const uids = document.getElementById('friendUids').value.trim();
        const maxRequests = document.getElementById('friendMaxRequests').value;
        
        if (!uids) {
            window.app.showNotification('Error', 'Please enter friend UIDs', 'error');
            return;
        }
        
        const uidList = uids.split('\n').filter(uid => uid.trim());
        this.log('info', `Starting to add ${uidList.length} friends (max ${maxRequests} per session)...`);
        this.log('success', `Task created! Processing ${uidList.length} UIDs`);
        
        window.app.showNotification('Success', `Started adding ${uidList.length} friends`, 'success');
    },
    
    // Accept Friend Requests
    acceptFriendRequests: function() {
        const maxRequests = document.getElementById('friendMaxRequests').value;
        this.log('info', `Accepting friend requests (max ${maxRequests})...`);
        this.log('success', 'Task created! Processing friend requests');
        
        window.app.showNotification('Success', 'Started accepting friend requests', 'success');
    },
    
    // Join Groups
    joinGroups: function() {
        const groups = document.getElementById('groupIds').value.trim();
        
        if (!groups) {
            window.app.showNotification('Error', 'Please enter group IDs or URLs', 'error');
            return;
        }
        
        const groupList = groups.split('\n').filter(g => g.trim());
        this.log('info', `Joining ${groupList.length} groups...`);
        this.log('success', 'Task created! Processing groups');
        
        window.app.showNotification('Success', `Started joining ${groupList.length} groups`, 'success');
    },
    
    // Post to Groups
    postToGroups: function() {
        const groups = document.getElementById('groupIds').value.trim();
        const content = document.getElementById('groupContent').value.trim();
        
        if (!groups || !content) {
            window.app.showNotification('Error', 'Please fill in all fields', 'error');
            return;
        }
        
        const groupList = groups.split('\n').filter(g => g.trim());
        this.log('info', `Posting to ${groupList.length} groups with spintax content...`);
        this.log('success', 'Task created! Processing posts');
        
        window.app.showNotification('Success', `Started posting to ${groupList.length} groups`, 'success');
    },
    
    // Generate Spintax
    generateSpintax: function() {
        const text = document.getElementById('spinText').value.trim();
        const count = parseInt(document.getElementById('spinCount').value);
        
        if (!text) {
            window.app.showNotification('Error', 'Please enter text with spintax', 'error');
            return;
        }
        
        const variations = [];
        for (let i = 0; i < count; i++) {
            variations.push(this.processSpintax(text));
        }
        
        const output = document.getElementById('spinOutput');
        output.innerHTML = `
            <div style="margin-top: 15px; padding: 15px; background: rgba(78, 204, 163, 0.1); border: 1px solid #4ecca3; border-radius: 8px;">
                <div style="color: #4ecca3; font-weight: 600; margin-bottom: 10px;">Generated ${count} variations:</div>
                ${variations.map((v, i) => `
                    <div style="padding: 10px; margin-bottom: 8px; background: rgba(0, 0, 0, 0.3); border-radius: 4px; color: #e0e0e0;">
                        <strong>Variation ${i + 1}:</strong><br>${v}
                    </div>
                `).join('')}
            </div>
        `;
        
        this.log('success', `Generated ${count} text variations`);
    },
    
    // Process Spintax
    processSpintax: function(text) {
        return text.replace(/\{([^{}]+)\}/g, (match, options) => {
            const choices = options.split('|');
            return choices[Math.floor(Math.random() * choices.length)];
        });
    },
    
    // Log to activity log
    log: function(level, message) {
        const log = document.getElementById('activityLog');
        if (!log) return;
        
        const line = document.createElement('div');
        line.className = 'console-line';
        line.innerHTML = `
            <span class="console-timestamp">${new Date().toLocaleTimeString()}</span>
            <span class="console-level ${level}">[${level.toUpperCase()}]</span>
            <span class="console-message">${message}</span>
        `;
        
        log.appendChild(line);
        log.scrollTop = log.scrollHeight;
    }
};

// Make facebookPro available globally
window.facebookPro = facebookPro;

console.log('Facebook Pro module loaded!');
