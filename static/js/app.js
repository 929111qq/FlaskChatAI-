class ChatApp {
    constructor() {
        this.socket = null;
        this.currentSessionId = null;
        this.currentUser = null;
        this.init();
    }

    init() {
        this.initializeSocketIO();
        this.bindEvents();
        this.loadUserProfile();
    }

    initializeSocketIO() {
        this.socket = io();

        // WebSocket连接成功时的处理
        this.socket.on('connect', () => {
            console.log('WebSocket连接成功');
        });

        // 状态更新处理
        this.socket.on('status', (data) => {
            console.log('状态更新:', data.msg);
        });
    }

    bindEvents() {
        // 登录表单事件
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // 注册表单事件
        const regForm = document.getElementById('regForm');
        if (regForm) {
            regForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // 表单切换
        const showRegister = document.getElementById('showRegister');
        const showLogin = document.getElementById('showLogin');
        if (showRegister && showLogin) {
            showRegister.addEventListener('click', () => this.toggleForm('register'));
            showLogin.addEventListener('click', () => this.toggleForm('login'));
        }

        // 聊天相关事件
        const sendBtn = document.getElementById('sendBtn');
        const messageInput = document.getElementById('messageInput');
        const newChatBtn = document.getElementById('newChatBtn');
        const logoutBtn = document.getElementById('logoutBtn');

        if (sendBtn) sendBtn.addEventListener('click', () => this.sendMessage());
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            messageInput.addEventListener('input', () => this.adjustTextareaHeight());
        }
        if (newChatBtn) newChatBtn.addEventListener('click', () => this.createNewChat());
        if (logoutBtn) logoutBtn.addEventListener('click', () => this.logout());
    }

    async handleLogin(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();

            if (response.ok) {
                this.showMessage('登录成功！', 'success');
                setTimeout(() => { window.location.href = '/chat'; }, 1000);
            } else {
                this.showMessage(data.error, 'error');
            }
        } catch (error) {
            this.showMessage('登录失败，请重试', 'error');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const username = document.getElementById('regUsername').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const data = await response.json();

            if (response.ok) {
                this.showMessage('注册成功！正在跳转...', 'success');
                setTimeout(() => { window.location.href = '/chat'; }, 1000);
            } else {
                this.showMessage(data.error, 'error');
            }
        } catch (error) {
            this.showMessage('注册失败，请重试', 'error');
        }
    }
    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        if (!message) return;

        // 显示用户消息
        this.appendMessage(message, 'user');
        messageInput.value = '';
        this.adjustTextareaHeight();

        // 显示加载状态
        const loadingId = this.appendMessage('正在思考中...', 'assistant', true);

        try {
            const response = await fetch('/api/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, session_id: this.currentSessionId })
            });
            const data = await response.json();

            if (response.ok) {
                // 移除加载消息
                this.removeMessage(loadingId);
                // 显示AI响应
                this.appendMessage(data.message.response, 'assistant');

                // 更新会话ID
                if (!this.currentSessionId) {
                    this.currentSessionId = data.session_id;
                    this.loadChatSessions();
                }
            } else {
                this.removeMessage(loadingId);
                this.appendMessage('抱歉，发送消息失败: ' + data.error, 'error');
            }
        } catch (error) {
            this.removeMessage(loadingId);
            this.appendMessage('网络错误，请重试', 'error');
        }
    }

    appendMessage(content, type, isLoading = false) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        const messageId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        messageDiv.id = messageId;
        messageDiv.className = `message ${type}`;

        if (isLoading) {
            messageDiv.innerHTML = `<div>${content}</div>`;
        } else {
            messageDiv.innerHTML = `<div>${this.formatMessage(content)}</div><div>${new Date().toLocaleTimeString()}</div>`;
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return messageId;
    }

    removeMessage(messageId) {
        const message = document.getElementById(messageId);
        if (message) {
            message.remove();
        }
    }

    formatMessage(content) {
        // 简单的消息格式化
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    adjustTextareaHeight() {
        const textarea = document.getElementById('messageInput');
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    async loadUserProfile() {
        try {
            const response = await fetch('/api/auth/profile');
            if (response.ok) {
                const data = await response.json();
                this.currentUser = data.user;

                const userName = document.getElementById('userName');
                if (userName) {
                    userName.textContent = this.currentUser.username;
                }

                this.loadChatSessions();
            }
        } catch (error) {
            console.error('加载用户信息失败:', error);
        }
    }

    async loadChatSessions() {
        try {
            const response = await fetch('/api/chat/sessions');
            if (response.ok) {
                const data = await response.json();
                this.renderSessionList(data.sessions);
            }
        } catch (error) {
            console.error('加载会话列表失败:', error);
        }
    }
    renderSessionList(sessions) {
        const sessionList = document.getElementById('sessionList');
        if (!sessionList) return;

        sessionList.innerHTML = '';
        sessions.forEach(session => {
            const sessionDiv = document.createElement('div');
            sessionDiv.className = 'session-item';
            sessionDiv.innerHTML = `<div>${session.title || '新对话'}</div><div>${new Date(session.updated_at).toLocaleDateString()}</div>`;
            sessionDiv.addEventListener('click', () => this.loadChatHistory(session.session_id));
            sessionList.appendChild(sessionDiv);
        });
    }

    async loadChatHistory(sessionId) {
        try {
            const response = await fetch(`/api/chat/history/${sessionId}`);
            if (response.ok) {
                const data = await response.json();
                this.currentSessionId = sessionId;
                this.renderChatHistory(data.messages);
            }
        } catch (error) {
            console.error('加载聊天历史失败:', error);
        }
    }
    renderChatHistory(messages) {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        messages.forEach(message => {
            this.appendMessage(message.message, 'user');
            if (message.response) {
                this.appendMessage(message.response, 'assistant');
            }
        });
    }
    createNewChat() {
        this.currentSessionId = null;
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = `<div>开始新的对话！我可以帮助您解答问题、进行对话。请输入您的问题。</div>`;
    }
    async logout() {
        try {
            const response = await fetch('/api/auth/logout', { method: 'POST' });
            if (response.ok) {
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('退出失败:', error);
        }
    }
    toggleForm(type) {
        const loginForm = document.getElementById('loginForm').parentElement;
        const registerForm = document.getElementById('registerForm');
        if (type === 'register') {
            loginForm.style.display = 'none';
            registerForm.style.display = 'block';
        } else {
            loginForm.style.display = 'block';
            registerForm.style.display = 'none';
        }
    }

    showMessage(message, type) {
        // 创建消息提示
        const msgDiv = document.createElement('div');
        msgDiv.className = `alert alert-${type}`;
        msgDiv.textContent = message;
        msgDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        if (type === 'success') {
            msgDiv.style.background = '#d4edda';
            msgDiv.style.color = '#155724';
            msgDiv.style.border = '1px solid #c3e6cb';
        } else {
            msgDiv.style.background = '#f8d7da';
            msgDiv.style.color = '#721c24';
            msgDiv.style.border = '1px solid #f5c6cb';
        }
        document.body.appendChild(msgDiv);
        setTimeout(() => { msgDiv.remove(); }, 3000);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
