/**
 * Chat Module - Direct Messaging with WebSockets
 */
const ChatApp = {
    contacts: [],
    activeContact: null,
    messages: [],
    socket: null,
    searchQuery: '',

    async init() {
        await this.loadContacts();
        this.initSocket();
    },

    initSocket() {
        const token = sessionStorage.getItem('token');
        if (!token) return;

        // Initialize Socket.io client
        // The library should be included in the HTML
        this.socket = io({
            query: { token: token }
        });

        this.socket.on('connect', () => {
            console.log('Connected to WebSocket');
        });

        this.socket.on('new_message', (msg) => {
            // If the message is from the active contact, append it
            if (this.activeContact && msg.sender_id === this.activeContact.id) {
                this.messages.push(msg);
                this.renderMessages();
                this.scrollToBottom();
            } else {
                // Optionally show a notification for other contacts
                Toast.info(`${msg.sender_name}: ${msg.content.substring(0, 30)}...`);
            }
        });

        this.socket.on('message_sent', (msg) => {
            // Confirmation that our message was sent successfully
            if (this.activeContact && msg.receiver_id === this.activeContact.id) {
                this.messages.push(msg);
                this.renderMessages();
                this.scrollToBottom();
            }
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from WebSocket');
        });
    },

    async loadContacts() {
        try {
            const data = await API.get('/chat/contacts');
            if (data && data.contacts) {
                this.contacts = data.contacts;
                this.renderContacts();
            }
        } catch (error) {
            console.error('Lỗi khi tải danh sách người liên hệ', error);
        }
    },

    filterContacts(query) {
        this.searchQuery = query.toLowerCase().trim();
        this.renderContacts();
    },

    renderContacts() {
        const container = document.getElementById('contact-list');
        if (!container) return;

        let filtered = this.contacts;
        if (this.searchQuery) {
            filtered = this.contacts.filter(c => 
                c.full_name.toLowerCase().includes(this.searchQuery) ||
                c.username.toLowerCase().includes(this.searchQuery)
            );
        }

        if (filtered.length === 0) {
            container.innerHTML = '<div class="p-4 text-center text-muted small">Không tìm thấy ai</div>';
            return;
        }

        container.innerHTML = filtered.map(c => `
            <div class="contact-item ${this.activeContact && this.activeContact.id === c.id ? 'active' : ''}" 
                 onclick="ChatApp.selectContact(${JSON.stringify(c).replace(/"/g, '&quot;')})">
                <div class="sidebar-user-avatar" style="width:40px;height:40px;font-size:0.8rem;">${getInitials(c.full_name)}</div>
                <div class="contact-info">
                    <div class="contact-name">${c.full_name}</div>
                    <div class="contact-status">${getRoleName(c.role)}</div>
                </div>
            </div>
        `).join('');
    },

    async selectContact(contact) {
        this.activeContact = contact;
        this.renderContacts();
        
        // Show chat components
        document.getElementById('welcome-screen').classList.add('d-none');
        document.getElementById('chat-header').classList.remove('d-none');
        document.getElementById('chat-messages').classList.remove('d-none');
        document.getElementById('chat-input-container').classList.remove('d-none');

        // Update header info
        document.getElementById('active-contact-avatar').textContent = getInitials(contact.full_name);
        document.getElementById('active-contact-name').textContent = contact.full_name;
        document.getElementById('active-contact-role').textContent = getRoleName(contact.role);

        await this.loadMessages();
        this.scrollToBottom();
    },

    async loadMessages() {
        if (!this.activeContact) return;

        try {
            const data = await API.get(`/chat/messages/${this.activeContact.id}`);
            if (data && data.messages) {
                this.messages = data.messages;
                this.renderMessages();
            }
        } catch (error) {
            console.error('Lỗi khi tải tin nhắn', error);
        }
    },

    renderMessages() {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        const currentUserId = parseInt(sessionStorage.getItem('user_id') || '0');

        container.innerHTML = this.messages.map(m => {
            const isMe = m.sender_id === currentUserId;
            return `
                <div class="message-bubble ${isMe ? 'message-sent' : 'message-received'}">
                    <div class="message-content">${m.content}</div>
                    <div class="message-time text-end">${formatTime(m.created_at)}</div>
                </div>
            `;
        }).join('');
    },

    async sendMessage() {
        const input = document.getElementById('chat-input-field');
        const content = input.value.trim();
        if (!content || !this.activeContact || !this.socket) return;

        const token = sessionStorage.getItem('token');
        
        // Emit via WebSocket
        this.socket.emit('send_message', {
            receiver_id: this.activeContact.id,
            content: content,
            token: token
        });

        input.value = '';
        input.focus();
    },

    scrollToBottom() {
        const container = document.getElementById('chat-messages');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }
};

function getRoleName(role) {
    const roles = {
        'admin': 'Quản trị viên',
        'teacher': 'Giảng viên',
        'student': 'Sinh viên'
    };
    return roles[role] || role;
}

function formatTime(isoString) {
    if (!isoString) return '';
    try {
        const date = new Date(isoString);
        return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    } catch(e) {
        return '';
    }
}
