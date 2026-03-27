/**
 * Task Management System - Core Application JavaScript
 * Handles authentication, API calls, notifications, and common UI interactions
 */

// ===== API Helper =====
const API = {
    baseUrl: '/api',

    getToken() {
        return sessionStorage.getItem('token') || '';
    },

    setToken(token) {
        sessionStorage.setItem('token', token);
    },

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const token = this.getToken();
        const headers = { ...options.headers };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers,
            });

            // Parse json safely
            let data = {};
            try { data = await response.json(); } catch (e) { }

            if ((response.status === 401 || response.status === 422) && token) {
                // Only redirect if we HAD a token and it expired or secret changed (422)
                sessionStorage.clear();
                window.location.href = '/login';
                return null;
            }

            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    get(endpoint) {
        return this.request(endpoint);
    },

    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE',
        });
    },

    upload(endpoint, formData) {
        return this.request(endpoint, {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${this.getToken()}`,
            },
        });
    },
};

// ===== Toast Notifications =====
const Toast = {
    container: null,

    init() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    },

    show(message, type = 'info', duration = 4000) {
        if (!this.container) this.init();

        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle',
        };

        const toast = document.createElement('div');
        toast.className = `toast-item ${type}`;
        toast.innerHTML = `
            <i class="${icons[type] || icons.info}" style="font-size: 1.1rem;"></i>
            <span style="flex: 1; font-size: 0.85rem;">${message}</span>
            <i class="fas fa-times" style="cursor: pointer; opacity: 0.5;" onclick="this.parentElement.remove()"></i>
        `;

        this.container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(50px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    success(message) { this.show(message, 'success'); },
    error(message) { this.show(message, 'error'); },
    info(message) { this.show(message, 'info'); },
};

// ===== Auth Functions =====
const Auth = {
    async login(username, password) {
        try {
            const data = await API.post('/login', { username, password });
            if (data && data.token) {
                sessionStorage.clear();
                API.setToken(data.token);
                sessionStorage.setItem('role', data.user.role);
                sessionStorage.setItem('full_name', data.user.full_name);
                Toast.success('Đăng nhập thành công!');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 500);
            }
        } catch (error) {
            Toast.error(error.message || 'Đăng nhập thất bại');
        }
    },

    async register(formData) {
        try {
            const data = await API.post('/register', formData);
            if (data) {
                Toast.success(data.message || 'Đăng ký thành công! Vui lòng chờ quản trị viên phê duyệt.');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 3000);
            }
        } catch (error) {
            Toast.error(error.message || 'Đăng ký thất bại');
        }
    },

    async logout() {
        try {
            await API.post('/logout', {});
        } catch (e) { /* ignore */ }
        sessionStorage.clear();
        window.location.href = '/login';
    },
};

// Global polling for "Realtime" feel
const Realtime = {
    socket: null,
    interval: null,
    lastUnreadCount: 0,

    init() {
        if (sessionStorage.getItem('token')) {
            this.initSocket();
            this.start();
        }
    },

    initSocket() {
        const token = sessionStorage.getItem('token');
        if (!token || this.socket) return;

        this.socket = io({
            query: { token }
        });

        this.socket.on('connect', () => {
            console.log('Connected to real-time server');
        });

        this.socket.on('new_message', (msg) => {
            // If chat module exists, notify it
            window.dispatchEvent(new CustomEvent('new-chat-message', { detail: msg }));
        });

        this.socket.on('new_notification', (notif) => {
            Notifications.load();
            Toast.info(notif.message);
        });

        this.socket.on('task_updated', (data) => {
            console.log('[Socket] task_updated received:', data);
            // Dispatch specifically for task module
            window.dispatchEvent(new CustomEvent('task-realtime-update', { detail: data }));
        });

        this.socket.on('task_list_updated', (data) => {
            const currentUserId = parseInt(sessionStorage.getItem('user_id'));
            const userRole = sessionStorage.getItem('role');

            console.log('[Socket] task_list_updated received:', data);
            console.log(`[Socket Debug] CurrentUser: ${currentUserId}, Role: ${userRole}`);

            // Show toast notification only for relevant users (assignees or creator)
            if (data.action === 'status_change' && data.changer_name) {
                const assigneeIds = (data.assignee_ids || []).map(id => Number(id));
                const isAssignee = assigneeIds.includes(Number(currentUserId));
                const isCreator = Number(data.creator_id) === Number(currentUserId);
                const isChanger = Number(data.changer_id) === Number(currentUserId);

                console.log(`[Socket Filter Detail] Task: ${data.task_title}, Changer: ${data.changer_id}, TargetAssignees: ${assigneeIds}, TargetCreator: ${data.creator_id}`);
                console.log(`[Socket Filter Logic] !isChanger: ${!isChanger}, isAssignee: ${isAssignee}, isCreator: ${isCreator}`);

                // Only show toast if user is directly involved (assignee or creator)
                if (!isChanger && (isAssignee || isCreator)) {
                    Toast.info(`${data.changer_name} đã chuyển "${data.task_title}" sang ${data.new_status}`);
                } else if (!isChanger) {
                    console.log(`[Socket Filter] Suppressing toast for User ${currentUserId} (not an assignee or creator)`);
                }
            }
            // Broadcast for Kanban board and task list sync across all users
            window.dispatchEvent(new CustomEvent('task-list-realtime-update', { detail: data }));
        });
    },

    start() {
        if (this.interval) clearInterval(this.interval);
        // Initial count
        this.checkNotifications(true);

        this.interval = setInterval(() => {
            this.checkNotifications();
        }, 10000); // Poll every 10 seconds
    },

    async checkNotifications(isInitial = false) {
        try {
            const data = await API.get('/notifications/unread-count');
            if (data && data.unread_count !== undefined) {
                const newCount = data.unread_count;

                if (!isInitial && newCount > this.lastUnreadCount) {
                    // We have new notifications!
                    Notifications.load();

                    // Dispatch event for other modules to react (Realtime Refresh)
                    window.dispatchEvent(new CustomEvent('new-notification', {
                        detail: { count: newCount }
                    }));

                    // Subtle animation for the dot
                    const dot = document.getElementById('notification-count-dot');
                    if (dot) {
                        dot.style.transform = 'scale(1.5)';
                        setTimeout(() => dot.style.transform = 'scale(1)', 500);
                    }
                } else if (newCount !== this.lastUnreadCount) {
                    Notifications.updateBadge(newCount);
                }

                this.lastUnreadCount = newCount;
            }
        } catch (e) { /* ignore */ }
    }
};

// ===== Notification System =====
const Notifications = {
    async load() {
        try {
            const data = await API.get('/notifications');
            if (data) {
                this.updateBadge(data.unread_count);
                this.renderDropdown(data.notifications);
            }
        } catch (e) { /* silent */ }
    },

    updateBadge(count) {
        const badge = document.getElementById('notification-count');
        const dot = document.querySelector('.notification-dot');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline' : 'none';
        }
        if (dot) {
            dot.style.display = count > 0 ? 'block' : 'none';
        }
    },

    renderDropdown(notifications) {
        const list = document.getElementById('notification-list');
        if (!list) return;

        if (notifications.length === 0) {
            list.innerHTML = '<div class="empty-state" style="padding: 30px;"><i class="fas fa-bell-slash empty-state-icon" style="font-size: 2rem;"></i><p class="empty-state-text" style="font-size: 0.85rem;">Không có thông báo</p></div>';
            return;
        }

        const iconMap = {
            task: 'fas fa-tasks',
            task_request: 'fas fa-check-double',
            schedule: 'fas fa-calendar-alt',
            qna: 'fas fa-question-circle',
            document: 'fas fa-file-alt',
            info: 'fas fa-info-circle',
        };

        list.innerHTML = notifications.slice(0, 10).map(n => `
            <div class="notification-item ${n.is_read ? '' : 'unread'}" onclick="Notifications.handleAction(${n.id}, '${n.reference_type}', ${n.reference_id})">
                <div class="notification-icon ${n.notification_type}">
                    <i class="${iconMap[n.notification_type] || iconMap.info}"></i>
                </div>
                <div class="notification-text">
                    <div class="notification-title">${n.title} ${n.is_read ? '' : '<span class="badge bg-danger ms-1" style="font-size: 0.5rem; padding: 2px 4px;">Mới</span>'}</div>
                    <div class="notification-message">${n.message}</div>
                    <div class="notification-time">${timeAgo(n.created_at)}</div>
                </div>
            </div>
        `).join('');
    },

    async handleAction(id, refType, refId) {
        try {
            // 1. Mark as read
            await API.put(`/notifications/${id}/read`, {});
            this.load();

            // 2. Redirect based on reference
            if (refType === 'request') {
                window.location.href = '/tasks/requests';
            } else if (refType === 'task') {
                // Redirect to Kanban or Detail? Kanban usually better for context
                window.location.href = '/tasks/board';
            } else if (refType === 'document') {
                window.location.href = '/documents';
            }
            // Add more types as needed...

            // Close dropdown
            const dropdown = document.getElementById('notification-dropdown');
            if (dropdown) dropdown.classList.remove('show');
        } catch (e) {
            console.error('Notification action error:', e);
            // Fallback: just reload
            this.load();
        }
    },

    async markAllRead() {
        try {
            await API.put('/notifications/read-all', {});
            this.load();
            Toast.success('Đã đánh dấu tất cả đã đọc');
        } catch (e) { /* silent */ }
    },

    toggle() {
        const dropdown = document.getElementById('notification-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('show');
        }
    },
};

// ===== Utility Functions =====
function timeAgo(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return 'Vừa xong';
    if (diff < 3600) return `${Math.floor(diff / 60)} phút trước`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} giờ trước`;
    if (diff < 604800) return `${Math.floor(diff / 86400)} ngày trước`;
    return date.toLocaleDateString('vi-VN');
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('vi-VN', {
        day: '2-digit', month: '2-digit', year: 'numeric'
    });
}

function formatDateTime(dateStr) {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleString('vi-VN', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

function formatFileSize(bytes) {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + sizes[i];
}

function getStatusLabel(status) {
    const map = {
        'todo': 'Chưa bắt đầu',
        'in_progress': 'Đang làm',
        'done': 'Hoàn thành'
    };
    return map[status] || status;
}

function getStatusBadge(status) {
    const map = {
        'todo': '<span class="badge-status badge-todo"><i class="fas fa-circle" style="font-size:6px"></i> Chưa bắt đầu</span>',
        'in_progress': '<span class="badge-status badge-progress"><i class="fas fa-circle" style="font-size:6px"></i> Đang làm</span>',
        'done': '<span class="badge-status badge-done"><i class="fas fa-circle" style="font-size:6px"></i> Hoàn thành</span>',
    };
    return map[status] || status;
}

function getPriorityBadge(priority) {
    const map = {
        'low': '<span class="badge-priority badge-low">Thấp</span>',
        'medium': '<span class="badge-priority badge-medium">Trung bình</span>',
        'high': '<span class="badge-priority badge-high">Cao</span>',
        'urgent': '<span class="badge-priority badge-urgent">Khẩn cấp</span>',
    };
    return map[priority] || priority;
}

function getRoleBadge(role) {
    const map = {
        'admin': '<span class="badge-role badge-admin">Admin</span>',
        'teacher': '<span class="badge-role badge-teacher">Giảng viên</span>',
        'student': '<span class="badge-role badge-student">Sinh viên</span>',
    };
    return map[role] || role;
}

function getInitials(name) {
    if (!name) return '?';
    return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
}

// ===== Sidebar Navigation =====
function initSidebar() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            if (overlay) overlay.classList.toggle('show');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('show');
        });
    }

    // Active nav item
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-item').forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.startsWith(href)) {
            item.classList.add('active');
        }
    });

    // Close notification dropdown when clicking outside
    document.addEventListener('click', (e) => {
        const dropdown = document.getElementById('notification-dropdown');
        const btn = document.getElementById('notification-btn');
        if (dropdown && !dropdown.contains(e.target) && btn && !btn.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
}

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    Toast.init();
    initSidebar();

    // Load notifications and start real-time polling if logged in
    if (document.getElementById('notification-btn')) {
        Notifications.load();
        Realtime.init();
    }
});
