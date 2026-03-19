/**
 * Task Management Module
 * Handles task CRUD, card grid with lazy-load + pagination, and Kanban board
 */

const Tasks = {
    tasks: [],
    students: [],
    academicYears: [],
    activeAcademicYear: null,

    /* ── Pagination state ── */
    pagination: {
        page: 1,
        perPage: 12,   // cards per page
        total: 0,
        pages: 0,
        hasNext: false,
        hasPrev: false
    },

    /* ── Lazy-load / infinite-scroll state ── */
    lazyMode: false,          // true = infinite scroll, false = pagination buttons
    lazyLoading: false,
    lazyPage: 1,
    lazyDone: false,
    _searchTimer: null,
    initialized: false,
    dragDropInitialized: false,
    notificationListenerAdded: false,
    timerId: null,

    /* ================================================================
       INIT
    ================================================================ */
    async init() {
        if (this.initialized) return;

        await Promise.all([
            this.loadStudents(),
            this.loadAcademicYears(),
            this.loadMe()
        ]);
        await this.loadTasks(1);

        /* Determine display mode:
           - Card grid  => lazy-load + pagination
           - Kanban     => no pagination
           - Table      => pagination only */
        const grid = document.getElementById('tasks-card-grid');
        if (grid) {
            this.lazyMode = true;
            this._initLazySentinel();
        }

        // Drag-drop for kanban
        this.initDragDrop();

        // Realtime refresh on notification
        if (!this.notificationListenerAdded) {
            window.addEventListener('new-notification', () => {
                this.loadTasks(this.pagination.page);
            });
            this.notificationListenerAdded = true;
        }

        // Periodic refresh every 30s
        if (this.timerId) clearInterval(this.timerId);
        this.timerId = setInterval(() => this.loadTasks(this.pagination.page), 30000);

        this.initialized = true;
    },

    /* ================================================================
       DATA LOADING
    ================================================================ */
    async loadStudents() {
        try {
            const data = await API.get('/teachers');
            if (data) this.students = data.teachers || [];
        } catch (e) { /* silent */ }
    },

    async loadAcademicYears() {
        try {
            const data = await API.get('/academic-years');
            this.academicYears = data.academic_years || [];
            this.activeAcademicYear = this.academicYears.find(y => y.is_active) || null;
            this.populateYearSelects();
        } catch (e) { /* silent */ }
    },

    async loadMe() {
        try {
            const data = await API.get('/me');
            if (data && data.user) {
                this.currentUser = data.user;
                sessionStorage.setItem('user_id', data.user.id);
            }
        } catch (e) { /* silent */ }
    },

    populateYearSelects() {
        const selects = document.querySelectorAll('#filter-year, #task-academic-year');
        selects.forEach(sel => {
            if (!sel) return;
            const currentVal = sel.value;
            const isFilter = sel.id === 'filter-year';
            const firstOption = sel.options[0];
            sel.innerHTML = '';
            sel.appendChild(firstOption);
            this.academicYears.forEach(y => {
                const opt = document.createElement('option');
                opt.value = y.name;
                opt.textContent = y.name + (y.is_active ? ' ✓ (Hiện tại)' : '');
                sel.appendChild(opt);
            });
            if (currentVal) {
                sel.value = currentVal;
            } else if (!isFilter && this.activeAcademicYear) {
                sel.value = this.activeAcademicYear.name;
            }
        });
    },

    _buildUrl(page) {
        const semester = document.getElementById('filter-semester')?.value || '';
        const year = document.getElementById('filter-year')?.value || '';
        const status = document.getElementById('filter-status')?.value || '';
        const search = document.getElementById('filter-search')?.value || '';
        let url = `/tasks?page=${page}&per_page=${this.pagination.perPage}`;
        if (semester) url += `&semester=${encodeURIComponent(semester)}`;
        if (year) url += `&academic_year=${encodeURIComponent(year)}`;
        if (status) url += `&status=${encodeURIComponent(status)}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        return url;
    },

    /** Full reload (page 1) — resets lazy state */
    async loadTasks(page = 1) {
        this.pagination.page = page;

        // Reset lazy state when reloading from scratch
        if (page === 1) {
            this.tasks = [];
            this.lazyPage = 1;
            this.lazyDone = false;
        }

        try {
            this._showSkeleton();
            const data = await API.get(this._buildUrl(page));
            if (data) {
                this.tasks = data.tasks || [];
                this.pagination.total = data.total;
                this.pagination.pages = data.pages;
                this.pagination.hasNext = data.has_next;
                this.pagination.hasPrev = data.has_prev;
                this.lazyPage = page;
                if (!data.has_next) this.lazyDone = true;
                this.render();
                this._updateCountLabel();
            }
        } catch (error) {
            Toast.error('Không thể tải danh sách công việc');
        }
    },

    /** Append next page (lazy / infinite scroll) */
    async loadMoreTasks() {
        if (this.lazyLoading || this.lazyDone) return;
        this.lazyLoading = true;
        this._sentinelSpinner(true);

        try {
            const nextPage = this.lazyPage + 1;
            const data = await API.get(this._buildUrl(nextPage));
            if (data) {
                const newTasks = data.tasks || [];
                this.tasks = [...this.tasks, ...newTasks];
                this.lazyPage = nextPage;
                if (!data.has_next) this.lazyDone = true;
                this.pagination.total = data.total;
                this.pagination.pages = data.pages;
                this.pagination.hasNext = data.has_next;
                this._appendCards(newTasks);
                this._updateCountLabel();
            }
        } catch (e) {
            Toast.error('Không thể tải thêm công việc');
        } finally {
            this.lazyLoading = false;
            this._sentinelSpinner(!this.lazyDone);
        }
    },

    /* ================================================================
       RENDER ROUTER
    ================================================================ */
    render() {
        const grid = document.getElementById('tasks-card-grid');
        const tbody = document.getElementById('tasks-table-body');
        const kanban = document.getElementById('kanban-board');

        if (grid) { this.renderCards(); }
        if (tbody) { this.renderTable(tbody); }
        if (kanban) { this.renderKanban(); }

        // Pagination bar only when NOT in lazy mode
        if (!this.lazyMode) this.renderPagination();
    },

    /* ================================================================
       CARD GRID + LAZY LOAD
    ================================================================ */
    _showSkeleton() {
        const grid = document.getElementById('tasks-card-grid');
        if (!grid) return;
        grid.innerHTML = Array.from({ length: 9 }, () => `
            <div class="task-skeleton-card">
                <div class="skeleton-line" style="height:12px; width:55%;"></div>
                <div class="skeleton-line" style="height:20px; width:85%;"></div>
                <div class="skeleton-line" style="height:13px; width:70%;"></div>
                <div class="d-flex gap-2 mt-2">
                    <div class="skeleton-line" style="height:22px; width:70px; border-radius:20px;"></div>
                    <div class="skeleton-line" style="height:22px; width:60px; border-radius:20px;"></div>
                </div>
            </div>
        `).join('');
    },

    renderCards() {
        const grid = document.getElementById('tasks-card-grid');
        if (!grid) return;

        grid.innerHTML = '';

        if (this.tasks.length === 0) {
            grid.innerHTML = `
                <div class="tasks-empty-state">
                    <div class="empty-icon"><i class="fas fa-clipboard-list"></i></div>
                    <p>Không tìm thấy công việc nào</p>
                </div>`;
            this._hidePagination();
            return;
        }

        grid.innerHTML = this.tasks.map(t => this._cardHtml(t)).join('');

        // Add fade-in animation to each card
        grid.querySelectorAll('.task-card').forEach((card, i) => {
            card.style.animationDelay = `${i * 40}ms`;
            card.classList.add('card-fade-in');
        });

        if (this.lazyMode) {
            // Show sentinel spinner if more pages exist
            this._sentinelSpinner(this.pagination.hasNext);
            // Also show pagination buttons below sentinel
            this._renderCardPagination();
        } else {
            this.renderPagination();
        }
    },

    _appendCards(tasks) {
        const grid = document.getElementById('tasks-card-grid');
        if (!grid || !tasks.length) return;

        const start = this.tasks.length - tasks.length;
        tasks.forEach((t, i) => {
            const wrapper = document.createElement('div');
            wrapper.innerHTML = this._cardHtml(t);
            const card = wrapper.firstElementChild;
            card.style.animationDelay = `${i * 40}ms`;
            card.classList.add('card-fade-in');
            grid.appendChild(card);
        });
        this._renderCardPagination();
    },

    _cardHtml(task) {
        const priorityClass = `priority-${task.priority}`;
        const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'done';
        const dueBadge = task.due_date
            ? `<span class="task-card-meta-item ${isOverdue ? 'text-danger' : ''}">
                   <i class="far fa-calendar-alt"></i> ${formatDate(task.due_date)}
               </span>`
            : '';

        const assigneeAvatars = (task.assignees || []).slice(0, 4).map(a =>
            `<span class="kanban-card-assignee" title="${a.user_name}">${getInitials(a.user_name)}</span>`
        ).join('');
        const extraAssignees = (task.assignees || []).length > 4
            ? `<span style="font-size:0.7rem;color:var(--text-muted);margin-left:4px;">+${task.assignees.length - 4}</span>`
            : '';

        const isAdminOrTeacher = sessionStorage.getItem('role') === 'admin' || sessionStorage.getItem('role') === 'teacher';
        const actionBtns = isAdminOrTeacher ? `
            <button onclick="event.stopPropagation(); Tasks.showEditModal(${task.id})" title="Chỉnh sửa">
                <i class="fas fa-edit"></i>
            </button>
            <button class="danger" onclick="event.stopPropagation(); Tasks.deleteTask(${task.id})" title="Xóa">
                <i class="fas fa-trash"></i>
            </button>
        ` : '';

        return `
        <div class="task-card ${priorityClass}" onclick="Tasks.showDetail(${task.id})">
            <div class="task-card-header">
                <div class="task-card-title">${task.title}</div>
                ${getPriorityBadge(task.priority)}
            </div>

            ${task.description ? `<div class="task-card-desc">${task.description}</div>` : ''}

            <div class="task-card-meta">
                ${getStatusBadge(task.status)}
                ${dueBadge}
                ${task.course_name ? `<span class="task-card-meta-item"><i class="fas fa-book"></i> ${task.course_name}</span>` : ''}
                ${task.class_group ? `<span class="task-card-meta-item"><i class="fas fa-users"></i> ${task.class_group}</span>` : ''}
            </div>

            <div class="task-card-footer">
                <div class="task-card-assignees">
                    ${assigneeAvatars}${extraAssignees}
                    ${!(task.assignees && task.assignees.length) ? '<span style="font-size:0.75rem;color:var(--text-muted);">Chưa giao</span>' : ''}
                </div>
                <div class="task-card-actions">
                    ${actionBtns}
                </div>
            </div>
        </div>`;
    },

    /* ── Pagination buttons below the card grid ── */
    _renderCardPagination() {
        const bar = document.getElementById('tasks-pagination-bar');
        const nav = document.getElementById('tasks-pagination-nav');
        const info = document.getElementById('tasks-page-info');
        if (!bar) return;

        const { total, pages, hasNext, hasPrev } = this.pagination;
        const currentPage = this.lazyMode ? this.lazyPage : this.pagination.page;

        if (total === 0) { bar.style.display = 'none'; return; }
        bar.style.display = 'flex';

        // Info text
        const shown = this.tasks.length;
        info.textContent = `Hiển thị ${shown} / ${total} công việc`;

        // Page buttons
        let html = `
            <li class="page-item ${!hasPrev ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="Tasks.goToPage(${currentPage - 1}); return false;">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>`;

        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(pages, startPage + 4);
        if (endPage - startPage < 4) startPage = Math.max(1, endPage - 4);

        for (let i = startPage; i <= endPage; i++) {
            html += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="Tasks.goToPage(${i}); return false;">${i}</a>
                </li>`;
        }

        html += `
            <li class="page-item ${!hasNext && this.lazyDone ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="Tasks.goToPage(${currentPage + 1}); return false;">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>`;

        nav.innerHTML = html;
    },

    _hidePagination() {
        const bar = document.getElementById('tasks-pagination-bar');
        if (bar) bar.style.display = 'none';
    },

    /* ── Intersection Observer sentinel ── */
    _initLazySentinel() {
        const sentinel = document.getElementById('lazy-load-sentinel');
        if (!sentinel) return;

        this._observer = new IntersectionObserver(entries => {
            const entry = entries[0];
            if (entry.isIntersecting && !this.lazyLoading && !this.lazyDone) {
                this.loadMoreTasks();
            }
        }, { rootMargin: '120px' });

        this._observer.observe(sentinel);
    },

    _sentinelSpinner(show) {
        const el = document.getElementById('lazy-load-sentinel');
        if (el) el.style.display = show ? 'flex' : 'none';
    },

    /* ================================================================
       TABLE VIEW
    ================================================================ */
    renderTable(tbody) {
        if (this.tasks.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><i class="fas fa-tasks empty-state-icon"></i><p class="empty-state-text">Chưa có công việc nào</p></div></td></tr>`;
            return;
        }
        tbody.innerHTML = this.tasks.map(task => `
            <tr>
                <td>
                    <div style="font-weight:600;color:var(--text-primary);">${task.title}</div>
                    <div style="font-size:0.75rem;color:var(--text-muted);margin-top:2px;">${task.course_name || ''} ${task.class_group ? '- ' + task.class_group : ''}</div>
                    <div style="font-size:0.75rem;color:var(--text-muted);margin-top:2px;">${task.creator_name || ''}</div>
                    ${getStatusBadge(task.status)}
                </td>
                <td>${getPriorityBadge(task.priority)}</td>
                <td>
                    <div style="display:flex;align-items:center;gap:4px;">
                        ${(task.assignees || []).slice(0, 3).map(a => `<span class="kanban-card-assignee" title="${a.user_name}">${getInitials(a.user_name)}</span>`).join('')}
                        ${(task.assignees || []).length > 3 ? `<span style="font-size:0.7rem;color:var(--text-muted);">+${task.assignees.length - 3}</span>` : ''}
                    </div>
                </td>
                <td style="font-size:0.8rem;">${task.due_date ? formatDate(task.due_date) : '<span style="color:var(--text-muted)">—</span>'}</td>
                <td>
                    <div style="display:flex;gap:6px;">
                        <button class="btn-glass" style="padding:6px 10px;font-size:0.75rem;" onclick="Tasks.showDetail(${task.id})"><i class="fas fa-eye"></i></button>
                        ${(sessionStorage.getItem('role') === 'admin' || sessionStorage.getItem('role') === 'teacher') ? `
                            <button class="btn-glass" style="padding:6px 10px;font-size:0.75rem;" onclick="Tasks.showEditModal(${task.id})"><i class="fas fa-edit"></i></button>
                            <button class="btn-danger" style="padding:6px 10px;font-size:0.75rem;" onclick="Tasks.deleteTask(${task.id})"><i class="fas fa-trash"></i></button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `).join('');
    },

    renderPagination() {
        let paginationContainer = document.getElementById('tasks-pagination');
        if (!paginationContainer) {
            const tableBody = document.getElementById('tasks-table-body');
            if (!tableBody) return;
            const tableContainer = tableBody.closest('.table-responsive');
            paginationContainer = document.createElement('div');
            paginationContainer.id = 'tasks-pagination';
            paginationContainer.className = 'd-flex justify-content-between align-items-center mt-3 px-3';
            tableContainer.parentNode.appendChild(paginationContainer);
        }

        const { page, pages, total } = this.pagination;
        if (total === 0) { paginationContainer.innerHTML = ''; return; }

        let html = `
            <div class="text-muted" style="font-size:0.85rem;">
                Hiển thị <strong>${this.tasks.length}</strong> / <strong>${total}</strong> công việc
            </div>
            <nav><ul class="pagination pagination-sm mb-0">
                <li class="page-item ${page === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="Tasks.goToPage(${page - 1})"><i class="fas fa-chevron-left"></i></a>
                </li>`;

        let startPage = Math.max(1, page - 2);
        let endPage = Math.min(pages, startPage + 4);
        if (endPage - startPage < 4) startPage = Math.max(1, endPage - 4);

        for (let i = startPage; i <= endPage; i++) {
            html += `<li class="page-item ${i === page ? 'active' : ''}"><a class="page-link" href="#" onclick="Tasks.goToPage(${i})">${i}</a></li>`;
        }

        html += `
                <li class="page-item ${page === pages ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="Tasks.goToPage(${page + 1})"><i class="fas fa-chevron-right"></i></a>
                </li>
            </ul></nav>`;

        paginationContainer.innerHTML = html;
    },

    goToPage(page) {
        if (page < 1 || page > this.pagination.pages) return;
        if (this.lazyMode) {
            // In lazy mode: jump to page (full reload)
            this.tasks = [];
            this.lazyPage = page;
            this.lazyDone = false;
            this.pagination.page = page;
            this._loadPageCards(page);
        } else {
            this.loadTasks(page);
        }
    },

    async _loadPageCards(page) {
        try {
            this._showSkeleton();
            const data = await API.get(this._buildUrl(page));
            if (data) {
                this.tasks = data.tasks || [];
                this.pagination.total = data.total;
                this.pagination.pages = data.pages;
                this.pagination.hasNext = data.has_next;
                this.pagination.hasPrev = data.has_prev;
                this.lazyPage = page;
                this.lazyDone = !data.has_next;
                this.renderCards();
                this._updateCountLabel();
                // Scroll to top of card grid
                document.getElementById('tasks-card-grid')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        } catch (e) {
            Toast.error('Không thể tải trang');
        }
    },

    /* ================================================================
       KANBAN BOARD
    ================================================================ */
    renderKanban() {
        const statuses = ['todo', 'in_progress', 'done'];
        statuses.forEach(status => {
            const body = document.getElementById(`kanban-${status}`);
            const countEl = document.getElementById(`count-${status}`);
            if (!body) return;

            const currentUserId = parseInt(sessionStorage.getItem('user_id'));
            const filteredTasks = this.tasks.filter(t => {
                const myAssignment = t.assignees?.find(a => a.user_id === currentUserId);
                const effectiveStatus = myAssignment ? myAssignment.status : t.status;
                return effectiveStatus === status;
            });
            if (countEl) countEl.textContent = filteredTasks.length;

            if (filteredTasks.length === 0) {
                body.innerHTML = `<div class="empty-state" style="padding:30px;"><p style="font-size:0.8rem;color:var(--text-muted);opacity:0.6;">Kéo thả công việc vào đây</p></div>`;
                return;
            }

            body.innerHTML = filteredTasks.map(task => `
                <div class="kanban-card" draggable="true" data-task-id="${task.id}"
                     ondragstart="Tasks.onDragStart(event, ${task.id})"
                     onclick="Tasks.showDetail(${task.id})">
                    <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px;">
                        ${getPriorityBadge(task.priority)}
                        ${task.due_date ? `<span style="font-size:0.7rem;color:var(--text-muted);"><i class="far fa-clock"></i> ${formatDate(task.due_date)}</span>` : ''}
                    </div>
                    <div class="kanban-card-title">${task.title}</div>
                    ${task.course_name ? `<div class="kanban-card-meta"><i class="fas fa-book"></i> ${task.course_name}</div>` : ''}
                    <div class="d-flex justify-content-between align-items-center mt-2">
                        <div class="kanban-card-assignees">
                            ${(task.assignees || []).slice(0, 4).map(a => `<span class="kanban-card-assignee" title="${a.user_name}">${getInitials(a.user_name)}</span>`).join('')}
                        </div>
                        <div style="display:flex;gap:4px;">
                            ${(sessionStorage.getItem('role') === 'admin' || sessionStorage.getItem('role') === 'teacher') ? `
                                <button class="btn-glass p-1" style="font-size:0.7rem;width:26px;height:26px;" onclick="event.stopPropagation(); Tasks.showEditModal(${task.id})"><i class="fas fa-edit"></i></button>
                                <button class="btn-danger p-1" style="font-size:0.7rem;width:26px;height:26px;" onclick="event.stopPropagation(); Tasks.deleteTask(${task.id})"><i class="fas fa-trash"></i></button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `).join('');
        });
    },

    /* ================================================================
       DRAG & DROP
    ================================================================ */
    onDragStart(event, taskId) {
        event.dataTransfer.setData('text/plain', taskId);
        event.target.style.opacity = '0.5';
    },

    initDragDrop() {
        if (this.dragDropInitialized) return;

        const board = document.getElementById('kanban-board');
        if (!board) return;

        const columns = document.querySelectorAll('.kanban-body');
        columns.forEach(col => {
            col.addEventListener('dragover', e => { e.preventDefault(); col.classList.add('drag-over'); });
            col.addEventListener('dragleave', () => col.classList.remove('drag-over'));
            col.addEventListener('drop', async e => {
                e.preventDefault();
                col.classList.remove('drag-over');
                const taskId = e.dataTransfer.getData('text/plain');
                const newStatus = col.dataset.status;
                if (taskId && newStatus) await this.updateStatus(parseInt(taskId), newStatus);
            });
        });

        this.dragDropInitialized = true;
    },

    async updateStatus(taskId, status) {
        try {
            await API.put(`/tasks/${taskId}/status`, { status });
            Toast.success('Cập nhật trạng thái thành công');
            await this.loadTasks(this.lazyMode ? 1 : this.pagination.page);
        } catch (error) {
            Toast.error('Không thể cập nhật trạng thái');
        }
    },

    /* ================================================================
       SEARCH (debounced)
    ================================================================ */
    onSearch(value) {
        clearTimeout(this._searchTimer);
        this._searchTimer = setTimeout(() => this.loadTasks(1), 400);
    },

    resetFilters() {
        ['filter-semester', 'filter-year', 'filter-status', 'filter-search'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });
        this.loadTasks(1);
    },

    /* ================================================================
       COUNT LABEL
    ================================================================ */
    _updateCountLabel() {
        const label = document.getElementById('tasks-count-label');
        if (label) {
            label.textContent = `${this.pagination.total} công việc`;
        }
    },

    /* ================================================================
       CRUD MODALS
    ================================================================ */
    showCreateModal() {
        document.getElementById('taskModalLabel').textContent = 'Tạo công việc mới';
        document.getElementById('taskForm').reset();
        document.getElementById('task-id').value = '';
        this.populateYearSelects();
        const container = document.getElementById('assignee-checkboxes');
        if (container) container.innerHTML = this.students.map(s => this.renderAssigneeRow(s)).join('');
        bootstrap.Modal.getOrCreateInstance(document.getElementById('taskModal')).show();
    },

    async showEditModal(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (!task) return;
        document.getElementById('taskModalLabel').textContent = 'Chỉnh sửa công việc';
        document.getElementById('task-id').value = task.id;
        document.getElementById('task-title').value = task.title;
        document.getElementById('task-description').value = task.description || '';
        document.getElementById('task-priority').value = task.priority;
        document.getElementById('task-status').value = task.status;
        document.getElementById('task-due-date').value = task.due_date ? task.due_date.split('T')[0] : '';
        document.getElementById('task-course-name').value = task.course_name || '';
        document.getElementById('task-course-code').value = task.course_code || '';
        document.getElementById('task-class-group').value = task.class_group || '';
        if (document.getElementById('task-semester')) document.getElementById('task-semester').value = task.semester || '';
        if (document.getElementById('task-academic-year')) document.getElementById('task-academic-year').value = task.academic_year || '';
        const container = document.getElementById('assignee-checkboxes');
        if (container) {
            const assignedIds = (task.assignees || []).map(a => a.user_id);
            container.innerHTML = this.students.map(s => this.renderAssigneeRow(s, assignedIds)).join('');
        }
        bootstrap.Modal.getOrCreateInstance(document.getElementById('taskModal')).show();
    },

    async submitForm(e) {
        e.preventDefault();
        const taskId = document.getElementById('task-id').value;
        const assigneeIds = Array.from(document.querySelectorAll('#assignee-checkboxes input:checked')).map(cb => parseInt(cb.value));
        const payload = {
            title: document.getElementById('task-title').value,
            description: document.getElementById('task-description').value,
            priority: document.getElementById('task-priority').value,
            status: document.getElementById('task-status').value,
            due_date: document.getElementById('task-due-date').value || null,
            course_name: document.getElementById('task-course-name').value,
            course_code: document.getElementById('task-course-code').value,
            class_group: document.getElementById('task-class-group').value,
            semester: document.getElementById('task-semester')?.value || null,
            academic_year: document.getElementById('task-academic-year')?.value || null,
            assignee_ids: assigneeIds,
        };
        try {
            if (taskId) {
                await API.put(`/tasks/${taskId}`, payload);
                Toast.success('Cập nhật công việc thành công');
            } else {
                await API.post('/tasks', payload);
                Toast.success('Tạo công việc thành công');
            }
            bootstrap.Modal.getOrCreateInstance(document.getElementById('taskModal')).hide();
            await this.loadTasks(1);
        } catch (error) {
            Toast.error(error.message);
        }
    },

    async deleteTask(taskId) {
        const isAdmin = sessionStorage.getItem('role') === 'admin';
        const msg = isAdmin ? 'Bạn có chắc muốn xóa công việc này vĩnh viễn?' : 'Gửi yêu cầu xóa công việc này cho Admin?';
        if (!confirm(msg)) return;
        try {
            const res = await API.delete(`/tasks/${taskId}`);
            Toast.success(res.message || 'Thao tác thành công');
            await this.loadTasks(1);
        } catch (error) {
            Toast.error(error.message || 'Không thể xóa công việc');
        }
    },

    async withdrawTask(taskId) {
        if (!confirm('Bạn muốn rút khỏi công việc này? Yêu cầu sẽ được gửi cho Admin phê duyệt.')) return;
        try {
            const res = await API.post(`/tasks/${taskId}/withdraw`);
            Toast.success(res.message || 'Yêu cầu rút đã được gửi');
            bootstrap.Modal.getInstance(document.getElementById('taskDetailModal')).hide();
            await this.loadTasks(1);
        } catch (error) {
            Toast.error(error.message || 'Không thể gửi yêu cầu');
        }
    },

    async showDetail(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (!task) return;

        // Fetch history
        let history = [];
        try {
            const res = await API.get(`/tasks/${taskId}/history`);
            history = res.history || [];
        } catch (e) { console.error('History load failed', e); }

        const currentUserId = parseInt(sessionStorage.getItem('user_id'));
        const isAssigned = task.assignees?.some(a => a.user_id === currentUserId);

        const detailHtml = `
            <ul class="nav nav-tabs mb-3" role="tablist">
                <li class="nav-item"><a class="nav-link active" data-bs-toggle="tab" href="#detail-info">Chi tiết</a></li>
                <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#detail-history">Lịch sử</a></li>
            </ul>
            <div class="tab-content">
                <div class="tab-pane fade show active" id="detail-info">
                    <div style="margin-bottom:20px;">
                        <div style="display:flex;gap:8px;margin-bottom:16px;">
                            ${getStatusBadge(task.status)} ${getPriorityBadge(task.priority)}
                        </div>
                        <h5 style="font-weight:700;margin-bottom:12px;">${task.title}</h5>
                        <p style="color:var(--text-secondary);font-size:0.9rem;line-height:1.7;">${task.description || 'Không có mô tả'}</p>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:0.85rem;">
                        <div><span style="color:var(--text-muted);">Người tạo:</span> <strong>${task.creator_name || ''}</strong></div>
                        <div><span style="color:var(--text-muted);">Hạn:</span> <strong>${task.due_date ? formatDate(task.due_date) : '—'}</strong></div>
                        <div><span style="color:var(--text-muted);">Môn học:</span> <strong>${task.course_name || '—'}</strong></div>
                        <div><span style="color:var(--text-muted);">Nhóm lớp:</span> <strong>${task.class_group || '—'}</strong></div>
                        <div><span style="color:var(--text-muted);">Học kỳ:</span> <strong>${task.semester || '—'}</strong></div>
                        <div><span style="color:var(--text-muted);">Năm học:</span> <strong>${task.academic_year || '—'}</strong></div>
                        <div><span style="color:var(--text-muted);">Tạo lúc:</span> <strong>${formatDateTime(task.created_at)}</strong></div>
                    </div>
                    ${task.assignees && task.assignees.length > 0 ? `
                        <div style="margin-top:20px;">
                            <span style="color:var(--text-muted);font-size:0.8rem;">Người được giao:</span>
                            <div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:8px;">
                                ${task.assignees.map(a => `
                                    <div style="display:flex;align-items:center;gap:8px;background:var(--glass-bg);padding:6px 12px;border-radius:var(--radius-sm);border:1px solid var(--border-color);">
                                        <span class="kanban-card-assignee" style="width:24px;height:24px;font-size:0.6rem;margin:0;">${getInitials(a.user_name)}</span>
                                        <div style="display:flex;flex-direction:column;">
                                            <span style="font-size:0.8rem;">${a.user_name}</span>
                                            <span style="font-size:0.65rem; color:var(--text-muted);">${getStatusLabel(a.status)}</span>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
                <div class="tab-pane fade" id="detail-history">
                    <div class="history-list" style="max-height:400px; overflow-y:auto; font-size:0.85rem;">
                        ${history.length > 0 ? history.map(h => `
                            <div class="history-item mb-3 pb-2 border-bottom" style="border-color:var(--border-color)!important;">
                                <div class="d-flex justify-content-between">
                                    <strong style="color:var(--accent-red);">${h.user_name}</strong>
                                    <span class="text-muted" style="font-size:0.75rem;">${formatDateTime(h.created_at)}</span>
                                </div>
                                <div class="mt-1"><span class="badge bg-secondary" style="font-size:0.65rem;">${Tasks.getActionLabel(h.action)}</span></div>
                                <div class="mt-1 text-secondary">${h.details || ''}</div>
                            </div>
                        `).join('') : '<p class="text-muted">Chưa có lịch sử thay đổi</p>'}
                    </div>
                </div>
            </div>
        `;

        document.getElementById('taskDetailBody').innerHTML = detailHtml;

        // Add footer buttons
        let footerHtml = '<button type="button" class="btn-glass" data-bs-dismiss="modal">Đóng</button>';
        if (isAssigned) {
            footerHtml += `<button type="button" class="btn-glass btn-sm" onclick="Tasks.withdrawTask(${task.id})"><i class="fas fa-sign-out-alt me-1"></i>Rút khỏi task</button>`;
        }
        document.getElementById('taskDetailFooter').innerHTML = footerHtml;

        bootstrap.Modal.getOrCreateInstance(document.getElementById('taskDetailModal')).show();
    },

    getActionLabel(action) {
        const map = {
            'create': 'Khởi tạo',
            'update': 'Cập nhật',
            'status_change': 'Trạng thái',
            'progress_change': 'Tiến độ',
            'assigned': 'Giao việc',
            'request_sent': 'Gửi yêu cầu',
            'approved': 'Phê duyệt',
            'rejected': 'Từ chối',
            'delete': 'Xóa',
            'withdraw': 'Rút lui'
        };
        return map[action] || action;
    },

    /* ================================================================
       ASSIGNEE HELPERS
    ================================================================ */
    filterAssignees(query) {
        const q = query.toLowerCase();
        document.querySelectorAll('#assignee-checkboxes .assignee-item').forEach(item => {
            item.style.display = item.innerText.toLowerCase().includes(q) ? 'flex' : 'none';
        });
    },

    toggleAllAssignees() {
        const checkboxes = document.querySelectorAll('#assignee-checkboxes .assignee-item input[type="checkbox"]');
        const visible = Array.from(checkboxes).filter(cb => cb.offsetParent !== null);
        const allChecked = visible.every(cb => cb.checked);
        visible.forEach(cb => { cb.checked = !allChecked; this.syncAssigneeRow(cb); });
    },

    renderAssigneeRow(s, assignedIds = []) {
        const isChecked = assignedIds.includes(s.id);
        return `
            <div class="assignee-item ${isChecked ? 'selected' : ''}" onclick="Tasks.toggleAssigneeRow(this, event)">
                <input class="form-check-input" type="checkbox" value="${s.id}" id="stu-${s.id}"
                       ${isChecked ? 'checked' : ''}
                       onclick="event.stopPropagation(); Tasks.syncAssigneeRow(this)">
                <label class="form-check-label" for="stu-${s.id}" style="font-size:0.85rem;color:var(--text-secondary);cursor:pointer;">
                    ${s.full_name} (${s.department || 'Giảng viên'})
                </label>
            </div>
        `;
    },

    syncAssigneeRow(checkbox) {
        const row = checkbox.closest('.assignee-item');
        if (row) row.classList.toggle('selected', checkbox.checked);
    },

    toggleAssigneeRow(row, event) {
        const checkbox = row.querySelector('input[type="checkbox"]');
        if (checkbox) { checkbox.checked = !checkbox.checked; this.syncAssigneeRow(checkbox); }
    }
};
