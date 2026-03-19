/**
 * User Management Module
 * Handles User CRUD and activation for Admin
 */

const UserManage = {
    users: [],
    pagination: {
        page: 1,
        perPage: 10,
        total: 0,
        pages: 0
    },

    init() {
        this.loadUsers();
    },

    async loadUsers(query = '', page = 1) {
        try {
            this.pagination.page = page;
            const queryParam = query ? `&q=${encodeURIComponent(query)}` : '';
            const url = `/admin/users?page=${page}&per_page=${this.pagination.perPage}${queryParam}`;
            
            const data = await API.get(url);
            if (data) {
                this.users = data.users || [];
                this.pagination.total = data.total;
                this.pagination.pages = data.pages;
                this.renderTable();
                this.renderPagination(query);
            }
        } catch (error) {
            Toast.error('Không thể tải danh sách người dùng');
        }
    },

    renderTable() {
        const tbody = document.getElementById('users-table-body');
        if (!tbody) return;

        if (this.users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center py-5 text-muted">Không tìm thấy người dùng nào</td></tr>`;
            return;
        }

        tbody.innerHTML = this.users.map(user => `
            <tr class="fade-in">
                <td>
                    <div class="d-flex align-items-center">
                        <div class="sidebar-user-avatar" style="width: 36px; height: 36px; font-size: 0.8rem; margin-right: 12px;">
                            ${(user.full_name || '?').slice(0, 2).toUpperCase()}
                        </div>
                        <div>
                            <div class="fw-bold">${user.full_name}</div>
                            <div class="text-muted" style="font-size:0.75rem;">@${user.username} | ${user.email}</div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="badge ${this.getRoleBadgeClass(user.role)}">${this.getRoleLabel(user.role)}</span>
                </td>
                <td>${user.department || '<span class="text-muted">—</span>'}</td>
                <td>
                    <div style="font-size:0.8rem;">
                        ${user.student_id ? `<div>MSV: <strong>${user.student_id}</strong></div>` : ''}
                        ${user.phone ? `<div>SĐT: ${user.phone}</div>` : ''}
                    </div>
                </td>
                <td>
                    <div class="form-check form-switch">
                        <input class="form-check-input" type="checkbox" role="switch" 
                               ${user.is_active ? 'checked' : ''} 
                               onchange="UserManage.toggleActive(${user.id})">
                        <label class="form-check-label text-secondary" style="font-size:0.75rem;">
                            ${user.is_active ? 'Hoạt động' : 'Đã khóa'}
                        </label>
                    </div>
                </td>
                <td>
                    <div class="d-flex gap-2">
                        <button class="btn-glass p-2" onclick="UserManage.showEditModal(${user.id})" title="Chỉnh sửa">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-danger p-2" onclick="UserManage.deleteUser(${user.id})" title="Xóa" 
                                ${user.username === 'admin' ? 'disabled' : ''}>
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    },

    renderPagination(query) {
        let paginationContainer = document.getElementById('users-pagination');
        if (!paginationContainer) {
            const tableCard = document.querySelector('.table-responsive').parentNode;
            paginationContainer = document.createElement('div');
            paginationContainer.id = 'users-pagination';
            paginationContainer.className = 'd-flex justify-content-between align-items-center mt-3 px-3';
            tableCard.appendChild(paginationContainer);
        }

        const { page, pages, total } = this.pagination;
        
        let html = `
            <div class="text-muted" style="font-size: 0.85rem;">
                Hiển thị <strong>${this.users.length}</strong> / <strong>${total}</strong> người dùng
            </div>
            <nav>
                <ul class="pagination pagination-sm mb-0">
                    <li class="page-item ${page === 1 ? 'disabled' : ''}">
                        <a class="page-link" href="#" onclick="UserManage.goToPage(${page - 1}, '${query}')"><i class="fas fa-chevron-left"></i></a>
                    </li>
        `;

        // Simple range for pagination
        let startPage = Math.max(1, page - 2);
        let endPage = Math.min(pages, startPage + 4);
        if (endPage - startPage < 4) startPage = Math.max(1, endPage - 4);

        for (let i = startPage; i <= endPage; i++) {
            html += `
                <li class="page-item ${i === page ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="UserManage.goToPage(${i}, '${query}')">${i}</a>
                </li>
            `;
        }

        html += `
                    <li class="page-item ${page === pages ? 'disabled' : ''}">
                        <a class="page-link" href="#" onclick="UserManage.goToPage(${page + 1}, '${query}')"><i class="fas fa-chevron-right"></i></a>
                    </li>
                </ul>
            </nav>
        `;

        paginationContainer.innerHTML = html;
    },

    goToPage(page, query) {
        if (page < 1 || page > this.pagination.pages) return;
        this.loadUsers(query, page);
    },

    getRoleBadgeClass(role) {
        switch (role) {
            case 'admin': return 'bg-danger';
            case 'teacher': return 'bg-primary';
            default: return 'bg-success';
        }
    },

    getRoleLabel(role) {
        switch (role) {
            case 'admin': return 'Quản trị viên';
            case 'teacher': return 'Giảng viên';
            default: return 'Sinh viên';
        }
    },

    onRoleChange() {
        const role = document.getElementById('manage-role').value;
        const studentIdContainer = document.getElementById('student-id-container');
        if (studentIdContainer) {
            studentIdContainer.style.display = role === 'student' ? 'block' : 'none';
        }
    },

    showCreateModal() {
        const form = document.getElementById('userForm');
        form.reset();
        document.getElementById('manage-user-id').value = '';
        document.getElementById('userModalLabel').textContent = 'Thêm người dùng mới';
        document.getElementById('manage-username').disabled = false;
        document.getElementById('manage-reminder-pref').value = '5';
        this.onRoleChange();
        bootstrap.Modal.getOrCreateInstance(document.getElementById('userModal')).show();
    },

    showEditModal(userId) {
        const user = this.users.find(u => u.id === userId);
        if (!user) return;

        const form = document.getElementById('userForm');
        form.reset();

        document.getElementById('manage-user-id').value = user.id;
        document.getElementById('userModalLabel').textContent = 'Chỉnh sửa người dùng';
        document.getElementById('manage-username').value = user.username;
        document.getElementById('manage-username').disabled = true;
        document.getElementById('manage-email').value = user.email;
        document.getElementById('manage-full-name').value = user.full_name;
        document.getElementById('manage-role').value = user.role;
        document.getElementById('manage-department').value = user.department || '';
        document.getElementById('manage-phone').value = user.phone || '';
        document.getElementById('manage-student-id').value = user.student_id || '';
        document.getElementById('manage-reminder-pref').value = user.reminder_preference || '5';
        document.getElementById('manage-password').value = '';

        this.onRoleChange();
        bootstrap.Modal.getOrCreateInstance(document.getElementById('userModal')).show();
    },

    async submitForm(e) {
        e.preventDefault();
        const userId = document.getElementById('manage-user-id').value;

        const payload = {
            email: document.getElementById('manage-email').value,
            full_name: document.getElementById('manage-full-name').value,
            role: document.getElementById('manage-role').value,
            department: document.getElementById('manage-department').value,
            phone: document.getElementById('manage-phone').value,
            student_id: document.getElementById('manage-student-id').value,
            reminder_preference: document.getElementById('manage-reminder-pref').value
        };

        const password = document.getElementById('manage-password').value;
        if (password) payload.password = password;

        try {
            if (userId) {
                await API.put(`/admin/users/${userId}`, payload);
                Toast.success('Cập nhật người dùng thành công');
            } else {
                payload.username = document.getElementById('manage-username').value;
                await API.post('/admin/users', payload);
                Toast.success('Tạo người dùng thành công');
            }
            bootstrap.Modal.getOrCreateInstance(document.getElementById('userModal')).hide();
            this.loadUsers('', this.pagination.page);
        } catch (error) {
            Toast.error(error.message || 'Có lỗi xảy ra');
        }
    },

    async toggleActive(userId) {
        try {
            await API.put(`/admin/users/${userId}/toggle-active`);
            Toast.success('Cập nhật trạng thái thành công');
            // Update local state to avoid full reload if possible, but for simplicity:
            this.loadUsers('', this.pagination.page);
        } catch (error) {
            Toast.error('Không thể cập nhật trạng thái');
            this.loadUsers('', this.pagination.page); // Revert UI
        }
    },

    async deleteUser(userId) {
        if (!confirm('Bạn có chắc muốn xóa người dùng này? Thao tác này có thể ảnh hưởng đến dữ liệu liên quan.')) return;

        try {
            await API.delete(`/admin/users/${userId}`);
            Toast.success('Xóa người dùng thành công');
            this.loadUsers('', this.pagination.page);
        } catch (error) {
            Toast.error(error.message || 'Không thể xóa người dùng');
        }
    },

    search(query) {
        clearTimeout(this.searchTimer);
        this.searchTimer = setTimeout(() => {
            this.loadUsers(query, 1);
        }, 500);
    }
};
