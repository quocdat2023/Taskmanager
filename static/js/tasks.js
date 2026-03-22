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
    activeTaskId: null,
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

    /* ── History lazy-load state ── */
    _historyItems: [],
    _historyPage: 1,
    _historyPerPage: 10,
    _historyTotal: 0,
    _historyPages: 0,
    _historyHasNext: false,
    _historyLoading: false,
    _historyTaskId: null,
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
        // If we are on the Kanban board, we should load more tasks at once
        const kanban = document.getElementById('kanban-board');
        if (kanban) {
            this.pagination.perPage = 100;
        }

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
        // Realtime refresh on notification & task update
        if (!this.notificationListenerAdded) {
            window.addEventListener('new-notification', () => {
                this.loadTasks(this.pagination.page);
            });

            window.addEventListener('task-realtime-update', (e) => {
                const { task_id, action } = e.detail;
                // 1. Always refresh the main list/board
                this.loadTasks(this.pagination.page);

                // 2. If the updated task is currently open in detail modal, refresh the modal content
                if (this.activeTaskId === task_id) {
                    console.log(`Realtime update for active task ${task_id}: ${action}`);
                    this.showDetail(task_id, true); // true = refresh mode
                }
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
        const priorityClass = `p-${task.priority}`;
        const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'done' && task.status !== 'approved';
        const dueBadge = task.due_date
            ? `<span class="meta-item ${isOverdue ? 'text-danger' : ''}">
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

        // Progress Bar
        const progress = task.progress || 0;
        const subtasks = task.subtasks || [];
        const doneSubtasks = subtasks.filter(st => st.is_done).length;
        const subtaskText = subtasks.length > 0 ? `${doneSubtasks}/${subtasks.length} nhiệm vụ con` : 'Tiến độ';

        const progressBar = `
            <div class="kanban-card-progress">
                <div class="progress-container">
                    <div class="progress-bar-fill" style="width: ${progress}%"></div>
                </div>
                <div class="progress-text">
                    <span>${subtaskText}</span>
                    <span>${progress}%</span>
                </div>
            </div>
        `;

        return `
        <div class="task-card kanban-card ${priorityClass}" onclick="Tasks.showDetail(${task.id})">
            <div class="task-card-header">
                <div class="task-card-title">${task.title}</div>
                ${getPriorityBadge(task.priority)}
            </div>

            ${task.description ? `<div class="task-card-desc" style="font-size:0.8rem; color:var(--text-muted); margin-bottom:12px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">${task.description}</div>` : ''}

            ${progressBar}

            <div class="kanban-card-meta">
                ${dueBadge}
                ${task.estimated_time ? `<span class="meta-item"><i class="far fa-clock"></i> Dự kiến: ${task.estimated_time}</span>` : ''}
                ${task.course_name ? `<span class="meta-item"><i class="fas fa-book"></i> ${task.course_name}</span>` : ''}
            </div>

            <div class="kanban-card-footer">
                <div class="kanban-card-assignees">
                    ${assigneeAvatars}${extraAssignees}
                    ${!(task.assignees && task.assignees.length) ? '<span style="font-size:0.7rem;color:var(--text-muted);">Chưa giao</span>' : ''}
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
        const statuses = ['todo', 'in_progress', 'done', 'approved'];
        const role = sessionStorage.getItem('role');
        const currentUserId = parseInt(sessionStorage.getItem('user_id'));

        statuses.forEach(status => {
            const body = document.getElementById(`kanban-${status}`);
            const countEl = document.getElementById(`count-${status}`);
            if (!body) return;

            const filteredTasks = this.tasks.filter(t => {
                const myAssignment = t.assignees?.find(a => a.user_id === currentUserId);
                const effectiveStatus = myAssignment ? myAssignment.status : t.status;
                return effectiveStatus === status;
            });
            if (countEl) countEl.textContent = filteredTasks.length;

            if (filteredTasks.length === 0) {
                body.innerHTML = `<div class="empty-state" style="padding:40px 20px; text-align:center;">
                    <i class="fas fa-box-open" style="font-size:1.5rem; opacity:0.2; margin-bottom:10px; display:block;"></i>
                    <p style="font-size:0.75rem;color:var(--text-muted);opacity:0.6;margin:0;">Trống</p>
                </div>`;
                return;
            }

            body.innerHTML = filteredTasks.map(task => {
                const priorityClass = `p-${task.priority}`;
                const progress = task.progress || 0;

                let approveActions = '';
                // Only show approve/reject for cards in 'done' column AND IF user is admin/teacher
                if (status === 'done' && (role === 'admin' || role === 'teacher')) {
                    approveActions = `
                        <div class="approve-actions" onclick="event.stopPropagation()">
                            <button class="btn-approve" onclick="Tasks.updateStatus(${task.id}, 'approved')">
                                <i class="fas fa-check"></i> Duyệt
                            </button>
                            <button class="btn-reject" onclick="Tasks.updateStatus(${task.id}, 'in_progress')">
                                <i class="fas fa-undo"></i> Từ chối
                            </button>
                        </div>
                    `;
                }

                return `
                <div class="kanban-card ${priorityClass}" draggable="true" data-task-id="${task.id}"
                     ondragstart="Tasks.onDragStart(event, ${task.id})"
                     onclick="Tasks.showDetail(${task.id})">
                    
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <span style="font-size:0.7rem; font-weight:700; color:var(--text-muted); text-transform:uppercase;">${task.course_code || 'TASK'}</span>
                        ${task.due_date ? `<span style="font-size:0.7rem;color:var(--text-muted); white-space:nowrap;"><i class="far fa-clock"></i> ${formatDate(task.due_date)}</span>` : ''}
                    </div>

                    <div class="kanban-card-title">${task.title}</div>
                    
                    <div class="kanban-card-progress">
                        <div class="progress-container">
                            <div class="progress-bar-fill" style="width: ${progress}%"></div>
                        </div>
                        <div class="progress-text">
                            <span>${progress}%</span>
                            <span>${(task.subtasks || []).filter(st => st.is_done).length}/${(task.subtasks || []).length} hoàn thành</span>
                        </div>
                    </div>

                    <div class="kanban-card-footer">
                        <div class="kanban-card-assignees">
                            ${(task.assignees || []).slice(0, 3).map(a => `<span class="kanban-card-assignee" title="${a.user_name}">${getInitials(a.user_name)}</span>`).join('')}
                            ${(task.assignees || []).length > 3 ? `<span style="font-size:0.65rem; color:var(--text-muted); margin-left:4px;">+${task.assignees.length - 3}</span>` : ''}
                        </div>
                        <div style="display:flex; gap:6px;">
                            ${(task.attachments || []).length > 0 ? `<i class="fas fa-paperclip" style="font-size:0.75rem; opacity:0.5;"></i>` : ''}
                            ${(task.comments || []).length > 0 ? `<i class="far fa-comment" style="font-size:0.75rem; opacity:0.5;"></i>` : ''}
                        </div>
                    </div>

                    ${approveActions}
                </div>
            `}).join('');
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
        if (document.getElementById('task-progress')) document.getElementById('task-progress').value = task.progress || 0;
        if (document.getElementById('task-estimated-time')) document.getElementById('task-estimated-time').value = task.estimated_time || '';
        if (document.getElementById('task-actual-time')) document.getElementById('task-actual-time').value = task.actual_time || '';
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
            progress: parseInt(document.getElementById('task-progress')?.value) || 0,
            estimated_time: document.getElementById('task-estimated-time')?.value || '',
            actual_time: document.getElementById('task-actual-time')?.value || '',
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
                const res = await API.post('/tasks', payload);
                Toast.success('Tạo công việc thành công');
                // Show email status
                if (res.email_sent) {
                    Toast.success('📧 Email thông báo đã được gửi');
                } else if (res.email_error) {
                    Toast.error('⚠️ Không gửi được email: ' + res.email_error);
                }
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

    async showDetail(taskId, isRefresh = false) {
        if (!isRefresh) {
            // Leave previous task room if any
            if (this.activeTaskId && Realtime.socket) {
                Realtime.socket.emit('leave_task', { task_id: this.activeTaskId });
            }
            this.activeTaskId = taskId;
            // Join new task room
            if (Realtime.socket) {
                Realtime.socket.emit('join_task', { task_id: taskId });
            }
        }

        const task = this.tasks.find(t => t.id === taskId);
        if (!task && !isRefresh) return;

        // Fetch latest task data to get subtasks, comments, attachments
        let updatedTask = task;
        try {
            const res = await API.get(`/tasks/${taskId}`);
            updatedTask = res.task;
        } catch (e) { }

        // Reset history state for lazy load
        this._historyItems = [];
        this._historyPage = 1;
        this._historyTotal = 0;
        this._historyPages = 0;
        this._historyHasNext = false;
        this._historyLoading = false;
        this._historyTaskId = taskId;

        const currentUserId = parseInt(sessionStorage.getItem('user_id'));
        const role = sessionStorage.getItem('role');

        // Remember which tab is currently active before re-rendering
        const activeTabHref = isRefresh
            ? document.querySelector('#taskDetailBody .nav-link.active')?.getAttribute('href') || '#detail-info'
            : '#detail-info';

        const _isTab = (tabId) => activeTabHref === tabId;

        const detailHtml = `
            <ul class="nav nav-pills nav-justified mb-4 custom-nav-pills" role="tablist">
                <li class="nav-item"><a class="nav-link ${_isTab('#detail-info') ? 'active' : ''}" data-bs-toggle="tab" href="#detail-info"><i class="fas fa-info-circle me-1"></i> Thông tin</a></li>
                <li class="nav-item"><a class="nav-link ${_isTab('#detail-subtasks') ? 'active' : ''}" data-bs-toggle="tab" href="#detail-subtasks"><i class="fas fa-tasks me-1"></i> Mục tiêu (${(updatedTask.subtasks || []).length})</a></li>
                <li class="nav-item"><a class="nav-link ${_isTab('#detail-comments') ? 'active' : ''}" data-bs-toggle="tab" href="#detail-comments"><i class="fas fa-comments me-1"></i> Thảo luận</a></li>
                <!-- <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#detail-attachments"><i class="fas fa-paperclip me-1"></i> Tài liệu</a></li> -->
                <li class="nav-item"><a class="nav-link ${_isTab('#detail-history') ? 'active' : ''}" data-bs-toggle="tab" href="#detail-history"><i class="fas fa-history me-1"></i> Lịch sử</a></li>
            </ul>
            <div class="tab-content">
                <!-- INFO TAB -->
                <div class="tab-pane fade ${_isTab('#detail-info') ? 'show active' : ''}" id="detail-info">
                    <div class="mb-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h4 class="fw-bold mb-0">${updatedTask.title}</h4>
                            ${getPriorityBadge(updatedTask.priority)}
                        </div>
                        <p class="text-secondary" style="white-space: pre-wrap; font-size:0.95rem;">${updatedTask.description || 'Không có mô tả'}</p>
                    </div>

                    <!-- Progress Section -->
                    <div class="mb-4">
                        <div class="d-flex justify-content-between mb-2">
                             <span class="fw-bold" style="font-size:0.85rem;">TIẾN ĐỘ TỔNG THỂ</span>
                             <span class="fw-bold text-primary">${updatedTask.progress}%</span>
                        </div>
                        <div class="progress-container" style="height:10px;">
                            <div class="progress-bar-fill" style="width: ${updatedTask.progress}%"></div>
                        </div>
                    </div>

                    <div class="row g-3 mb-4">
                        <div class="col-6">
                            <div class="p-3 rounded border bg-light">
                                <div class="text-muted small mb-1 uppercase fw-bold">Trạng thái</div>
                                <div>${getStatusBadge(updatedTask.status)}</div>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="p-3 rounded border bg-light">
                                <div class="text-muted small mb-1 uppercase fw-bold">Hạn chót</div>
                                <div class="fw-bold ${new Date(updatedTask.due_date) < new Date() ? 'text-danger' : ''}">
                                    <i class="far fa-calendar-alt me-1"></i> ${updatedTask.due_date ? formatDate(updatedTask.due_date) : '—'}
                                </div>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="p-3 rounded border bg-light">
                                <div class="text-muted small mb-1 uppercase fw-bold">Thời gian dự kiến</div>
                                <div class="fw-bold"><i class="far fa-clock me-1"></i> ${updatedTask.estimated_time || '—'}</div>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="p-3 rounded border bg-light">
                                <div class="text-muted small mb-1 uppercase fw-bold">Thời gian thực tế</div>
                                <div class="fw-bold"><i class="fas fa-stopwatch me-1"></i> ${updatedTask.actual_time || '—'}</div>
                            </div>
                        </div>
                    </div>

                    <div class="border-top pt-3">
                        <h6 class="fw-bold mb-3 uppercase small text-muted">Phân công & Môn học</h6>
                        <div class="row g-2 text-secondary small">
                             <div class="col-6">Môn: <strong>${updatedTask.course_name || '—'}</strong> (${updatedTask.course_code || '—'})</div>
                             <div class="col-6">Nhóm: <strong>${updatedTask.class_group || '—'}</strong></div>
                             <div class="col-6">Học kỳ: <strong>${updatedTask.semester || '—'}</strong></div>
                             <div class="col-6">Năm học: <strong>${updatedTask.academic_year || '—'}</strong></div>
                        </div>

                        <div class="mt-3 d-flex flex-wrap gap-2">
                            ${(updatedTask.assignees || []).map(a => `
                                <div class="d-flex align-items-center gap-2 bg-white border rounded px-2 py-1 shadow-sm">
                                    <span class="kanban-card-assignee" style="width:24px;height:24px;font-size:0.6rem;margin:0;">${getInitials(a.user_name)}</span>
                                    <span style="font-size:0.8rem; font-weight:600;">${a.user_name}</span>
                                    <span class="badge ${a.status === 'done' ? 'bg-success' : 'bg-secondary'}" style="font-size:0.6rem;">${getStatusLabel(a.status)}</span>
                                </div>
                            `).join('')}
                        </div>

                        ${(updatedTask.assignees || []).some(a => a.user_id === currentUserId) && role !== 'admin' ? `
                            <div class="mt-4 text-center">
                                <button class="btn btn-outline-danger btn-sm" onclick="Tasks.withdrawTask(${updatedTask.id})">
                                    <i class="fas fa-sign-out-alt me-2"></i> Rút khỏi task
                                </button>
                            </div>
                        ` : ''}
                    </div>
                </div>

                <!-- SUBTASKS TAB -->
                <div class="tab-pane fade ${_isTab('#detail-subtasks') ? 'show active' : ''}" id="detail-subtasks">
                    <div class="d-flex gap-2 mb-3">
                        <input type="text" id="new-subtask-title" class="form-control-custom py-2" placeholder="Thêm nhiệm vụ mới...">
                        <button class="btn-primary-custom" onclick="Tasks.addSubtask(${updatedTask.id})">Thêm</button>
                    </div>
                    <div id="subtasks-list" class="list-group list-group-flush">
                        ${(updatedTask.subtasks || []).map(st => `
                            <div class="list-group-item d-flex align-items-center justify-content-between py-2 border-bottom-0">
                                <div class="form-check d-flex align-items-center">
                                    <input class="form-check-input me-2" type="checkbox" ${st.is_done ? 'checked' : ''} 
                                           onchange="Tasks.toggleSubtask(${updatedTask.id}, ${st.id}, this.checked)">
                                    <span class="${st.is_done ? 'text-decoration-line-through text-muted' : ''}" style="font-size:0.95rem;">${st.title}</span>
                                </div>
                                <button class="btn text-danger p-1" onclick="Tasks.deleteSubtask(${updatedTask.id}, ${st.id})"><i class="fas fa-trash-alt"></i></button>
                            </div>
                        `).join('')}
                        ${(updatedTask.subtasks || []).length === 0 ? '<p class="text-center text-muted my-3">Chưa có nhiệm vụ con</p>' : ''}
                    </div>
                </div>

                <!-- COMMENTS TAB -->
                <div class="tab-pane fade ${_isTab('#detail-comments') ? 'show active' : ''}" id="detail-comments">
                    <div class="mb-3">
                         <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="small fw-bold text-muted uppercase">Thảo luận & Phản hồi</span>
                         </div>
                         <div id="reply-to-alert" class="alert alert-info py-2 px-3 mb-2 d-none d-flex justify-content-between align-items-center">
                            <span class="small">Đang trả lời: <strong id="reply-to-user"></strong></span>
                            <button type="button" class="btn-close" style="font-size:0.5rem;" onclick="Tasks.cancelReply()"></button>
                         </div>
                         <textarea id="comment-content" class="form-control-custom" rows="2" placeholder="Viết phản hồi hoặc ghi chú..."></textarea>
                         <div class="text-end mt-2">
                             <input type="hidden" id="comment-parent-id" value="">
                             <button class="btn-primary-custom" onclick="Tasks.addComment(${updatedTask.id})">Gửi bình luận</button>
                         </div>
                    </div>
                    <div id="comments-list" class="mt-4" style="max-height:450px; overflow-y:auto; padding-right:5px;">
                        ${this.renderCommentsTree(updatedTask.comments || [], currentUserId, role, updatedTask.id)}
                    </div>
                </div>

                <!-- ATTACHMENTS TAB -->
                <div class="tab-pane fade" id="detail-attachments">
                    <div class="mb-4 text-center p-4 border-dashed rounded" style="border: 2px dashed var(--border-color);">
                        <i class="fas fa-cloud-upload-alt text-muted mb-2" style="font-size:2rem; opacity:0.3;"></i>
                        <p class="small text-muted mb-3">Tải lên tài liệu hoặc ảnh minh họa (Max 16MB)</p>
                        <input type="file" id="attachment-file" class="d-none" onchange="Tasks.uploadAttachment(${updatedTask.id})">
                        <button class="btn-glass" onclick="document.getElementById('attachment-file').click()"><i class="fas fa-paperclip"></i> Chọn tệp tin</button>
                    </div>
                    <div id="attachments-list">
                        ${(updatedTask.attachments || []).map(a => `
                            <div class="d-flex align-items-center justify-content-between p-3 border rounded mb-2 bg-white">
                                <div class="d-flex align-items-center gap-3">
                                    <div class="sidebar-user-avatar bg-light text-primary" style="width:32px; height:32px;">
                                        <i class="${this.getFileIcon(a.file_type)}"></i>
                                    </div>
                                    <div class="d-flex flex-column">
                                        <a href="/uploads/${a.stored_name}" target="_blank" class="fw-bold small text-decoration-none">${a.file_name}</a>
                                        <span class="text-muted" style="font-size:0.65rem;">${formatDateTime(a.created_at)} • ${a.user_name}</span>
                                    </div>
                                </div>
                                <button class="btn text-danger p-1" onclick="Tasks.deleteAttachment(${updatedTask.id}, ${a.id})"><i class="fas fa-times"></i></button>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- HISTORY TAB -->
                <div class="tab-pane fade ${_isTab('#detail-history') ? 'show active' : ''}" id="detail-history">
                    <div id="history-items-container" class="history-list"></div>
                    <div id="history-load-more" class="text-center py-3" style="display:none;">
                        <button class="btn-glass" onclick="Tasks.loadMoreHistory()" id="history-load-more-btn">
                            <i class="fas fa-arrow-down me-1"></i> Tải thêm lịch sử
                        </button>
                    </div>
                    <div id="history-pagination-bar" class="d-flex justify-content-between align-items-center mt-2 px-1" style="display:none;"></div>
                    <div id="history-loading-spinner" class="text-center py-4" style="display:none;">
                        <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                        <span class="ms-2 text-muted small">Đang tải lịch sử...</span>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('taskDetailBody').innerHTML = detailHtml;

        if (!isRefresh) {
            const modalEl = document.getElementById('taskDetailModal');
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
            modal.show();

            // Handle modal close to leave room
            modalEl.addEventListener('hidden.bs.modal', () => {
                if (this.activeTaskId && Realtime.socket) {
                    Realtime.socket.emit('leave_task', { task_id: this.activeTaskId });
                }
                this.activeTaskId = null;
            }, { once: true });
        }

        // Lazy-load history when tab is clicked
        const historyTab = document.querySelector('a[href="#detail-history"]');
        if (historyTab) {
            historyTab.addEventListener('shown.bs.tab', () => {
                if (this._historyItems.length === 0 && !this._historyLoading) {
                    this.loadHistory(1);
                }
            });
        }

        // Attach Enter key for subtasks
        const subtaskInput = document.getElementById('new-subtask-title');
        if (subtaskInput) {
            subtaskInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.addSubtask(updatedTask.id);
                }
            });
        }
    },

    /* ================================================================
       SUBTASKS HANDLERS
    ================================================================ */
    async addSubtask(taskId) {
        const titleEl = document.getElementById('new-subtask-title');
        const title = titleEl.value.trim();
        if (!title) return;
        try {
            await API.post(`/tasks/${taskId}/subtasks`, { title });
            titleEl.value = '';
            Toast.success('Đã thêm nhiệm vụ con');
            this.showDetail(taskId);
            this.loadTasks(this.pagination.page);
        } catch (e) { Toast.error('Lỗi khi thêm nhiệm vụ con'); }
    },

    async toggleSubtask(taskId, subtaskId, isDone) {
        try {
            await API.put(`/tasks/${taskId}/subtasks/${subtaskId}`, { is_done: isDone });
            this.showDetail(taskId);
            this.loadTasks(this.pagination.page);
        } catch (e) { Toast.error('Lỗi khi cập nhật nhiệm vụ con'); }
    },

    async deleteSubtask(taskId, subtaskId) {
        if (!confirm('Xóa nhiệm vụ con này?')) return;
        try {
            await API.delete(`/tasks/${taskId}/subtasks/${subtaskId}`);
            Toast.success('Đã xóa nhiệm vụ con');
            this.showDetail(taskId);
            this.loadTasks(this.pagination.page);
        } catch (e) { Toast.error('Lỗi khi xóa nhiệm vụ con'); }
    },

    /* ================================================================
       COMMENT HANDLERS
    ================================================================ */
    renderCommentsTree(comments, currentUserId, role, taskId) {
        if (!comments || comments.length === 0) return '<p class="text-center text-muted">Chưa có bình luận nào</p>';

        // Structure map
        const map = {};
        const roots = [];

        // Sort by time first
        const sorted = [...comments].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

        sorted.forEach(c => {
            c.children = [];
            map[c.id] = c;
            if (c.parent_id && map[c.parent_id]) {
                map[c.parent_id].children.push(c);
            } else {
                roots.push(c);
            }
        });

        // Inverse roots to show latest first
        roots.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        const renderNode = (node, depth = 0) => {
            const isMyComment = node.user_id === currentUserId;
            const canDelete = isMyComment || role === 'admin';

            return `
                <div class="comment-node mb-3" style="margin-left: ${depth * 30}px; border-left: ${depth > 0 ? '2px solid var(--border-color)' : 'none'}; padding-left: ${depth > 0 ? '15px' : '0'};">
                    <div class="d-flex gap-3">
                        <div class="sidebar-user-avatar" style="width:32px; height:32px; font-size:0.7rem; flex-shrink:0;">${getInitials(node.user_name)}</div>
                        <div class="flex-grow-1">
                            <div class="d-flex align-items-center gap-2 mb-1">
                                <span class="fw-bold small">${node.user_name}</span>
                                <span class="text-muted" style="font-size:0.65rem;">${timeAgo(node.created_at)}</span>
                            </div>
                            <div class="text-secondary" style="font-size:0.85rem; line-height:1.5;">${node.content}</div>
                            <div class="mt-1 d-flex gap-3" style="font-size:0.7rem;">
                                <a href="javascript:void(0)" class="text-primary text-decoration-none fw-bold" onclick="Tasks.prepareReply(${node.id}, '${node.user_name}')">Trả lời</a>
                                ${canDelete ? `<a href="javascript:void(0)" class="text-danger text-decoration-none" onclick="Tasks.deleteComment(${taskId}, ${node.id})">Xóa</a>` : ''}
                            </div>
                        </div>
                    </div>
                    <div class="replies-container">
                        ${node.children.map(child => renderNode(child, depth + 1)).join('')}
                    </div>
                </div>
            `;
        };

        return roots.map(root => renderNode(root)).join('');
    },

    prepareReply(parentId, userName) {
        document.getElementById('comment-parent-id').value = parentId;
        document.getElementById('reply-to-user').innerText = userName;
        document.getElementById('reply-to-alert').classList.remove('d-none');
        document.getElementById('comment-content').focus();
    },

    cancelReply() {
        document.getElementById('comment-parent-id').value = '';
        document.getElementById('reply-to-alert').classList.add('d-none');
    },

    async addComment(taskId) {
        const contentEl = document.getElementById('comment-content');
        const parentId = document.getElementById('comment-parent-id').value;
        const content = contentEl.value.trim();
        if (!content) return;
        try {
            await API.post(`/tasks/${taskId}/comments`, {
                content,
                parent_id: parentId || null
            });
            contentEl.value = '';
            this.cancelReply();
            this.showDetail(taskId, true);
        } catch (e) { Toast.error('Lỗi khi gửi bình luận'); }
    },

    async deleteComment(taskId, commentId) {
        if (!confirm('Bạn chắc chắn muốn xóa thảo luận này?')) return;
        try {
            await API.delete(`/tasks/${taskId}/comments/${commentId}`);
            Toast.success('Đã xóa thảo luận');
            this.showDetail(taskId, true);
        } catch (e) { Toast.error(e.message || 'Lỗi khi xóa thảo luận'); }
    },

    /* ================================================================
       ATTACHMENT HANDLERS
    ================================================================ */
    async uploadAttachment(taskId) {
        const fileInput = document.getElementById('attachment-file');
        const file = fileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            await API.upload(`/tasks/${taskId}/attachments`, formData);
            Toast.success('Tải lên thành công');
            this.showDetail(taskId);
        } catch (e) { Toast.error(e.message || 'Lỗi khi tải lên tệp'); }
    },

    async deleteAttachment(taskId, attachmentId) {
        if (!confirm('Xóa tệp đính kèm này?')) return;
        try {
            await API.delete(`/tasks/${taskId}/attachments/${attachmentId}`);
            this.showDetail(taskId);
        } catch (e) { Toast.error('Lỗi khi xóa tệp'); }
    },

    getFileIcon(type) {
        if (!type) return 'far fa-file';
        if (type.includes('image')) return 'far fa-file-image';
        if (type.includes('pdf')) return 'far fa-file-pdf';
        if (type.includes('word')) return 'far fa-file-word';
        if (type.includes('excel') || type.includes('spreadsheet')) return 'far fa-file-excel';
        if (type.includes('presentation')) return 'far fa-file-powerpoint';
        return 'far fa-file-alt';
    },

    /* ================================================================
       HISTORY LAZY LOADING & PAGINATION
    ================================================================ */
    async loadHistory(page = 1) {
        if (this._historyLoading) return;
        this._historyLoading = true;

        const spinner = document.getElementById('history-loading-spinner');
        const container = document.getElementById('history-items-container');
        const loadMoreBtn = document.getElementById('history-load-more');

        if (spinner) spinner.style.display = 'flex';
        if (page === 1 && container) container.innerHTML = '';

        try {
            const res = await API.get(`/tasks/${this._historyTaskId}/history?page=${page}&per_page=${this._historyPerPage}`);
            if (res) {
                const newItems = res.history || [];
                if (page === 1) {
                    this._historyItems = newItems;
                } else {
                    this._historyItems = [...this._historyItems, ...newItems];
                }
                this._historyPage = page;
                this._historyTotal = res.total || 0;
                this._historyPages = res.pages || 0;
                this._historyHasNext = res.has_next || false;

                // Render items
                if (page === 1) {
                    this._renderHistoryItems(newItems, false);
                } else {
                    this._renderHistoryItems(newItems, true);
                }

                // Show/hide load more button
                if (loadMoreBtn) {
                    loadMoreBtn.style.display = this._historyHasNext ? 'block' : 'none';
                }

                // Render pagination info
                this._renderHistoryPagination();
            }
        } catch (e) {
            console.error('History load failed', e);
            if (container && page === 1) {
                container.innerHTML = '<p class="history-empty">Không thể tải lịch sử</p>';
            }
        } finally {
            this._historyLoading = false;
            if (spinner) spinner.style.display = 'none';
        }
    },

    async loadMoreHistory() {
        if (this._historyHasNext) {
            await this.loadHistory(this._historyPage + 1);
        }
    },

    goToHistoryPage(page) {
        if (page < 1 || page > this._historyPages) return;
        this._historyItems = [];
        this.loadHistory(page);
    },

    _renderHistoryItems(items, append = false) {
        const container = document.getElementById('history-items-container');
        if (!container) return;

        if (!append) container.innerHTML = '';

        if (this._historyItems.length === 0) {
            container.innerHTML = '<p class="history-empty">Chưa có lịch sử thay đổi</p>';
            return;
        }

        items.forEach((h, i) => {
            const div = document.createElement('div');
            div.className = 'history-item card-fade-in';
            div.style.animationDelay = `${i * 40}ms`;
            div.innerHTML = `
                <div class="d-flex justify-content-between hi-header">
                    <strong class="hi-user">${h.user_name}</strong>
                    <span class="hi-time">${formatDateTime(h.created_at)}</span>
                </div>
                <div class="mt-1">
                    <span class="hi-badge">${Tasks.getActionLabel(h.action)}</span>
                </div>
                <div class="mt-1 hi-details">${h.details || ''}</div>
            `;
            container.appendChild(div);
        });
    },

    _renderHistoryPagination() {
        const bar = document.getElementById('history-pagination-bar');
        if (!bar) return;

        if (this._historyTotal === 0) {
            bar.style.display = 'none';
            return;
        }
        bar.style.display = 'flex';

        const { _historyPage: page, _historyPages: pages, _historyTotal: total } = this;
        const shown = this._historyItems.length;

        let html = `
            <div class="text-muted" style="font-size:0.8rem;">
                ${shown} / ${total} mục
            </div>
            <nav><ul class="pagination pagination-sm mb-0" style="font-size:0.75rem;">`;

        html += `<li class="page-item ${page === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="event.preventDefault(); Tasks.goToHistoryPage(${page - 1})">
                <i class="fas fa-chevron-left"></i>
            </a></li>`;

        let startP = Math.max(1, page - 2);
        let endP = Math.min(pages, startP + 4);
        if (endP - startP < 4) startP = Math.max(1, endP - 4);

        for (let i = startP; i <= endP; i++) {
            html += `<li class="page-item ${i === page ? 'active' : ''}"><a class="page-link" href="#" onclick="event.preventDefault(); Tasks.goToHistoryPage(${i})">${i}</a></li>`;
        }

        html += `<li class="page-item ${page === pages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="event.preventDefault(); Tasks.goToHistoryPage(${page + 1})">
                <i class="fas fa-chevron-right"></i>
            </a></li></ul></nav>`;

        bar.innerHTML = html;
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
        const checkboxes = document.querySelectorAll('#assignee-checkboxes input[type="checkbox"]');
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        checkboxes.forEach(cb => {
            cb.checked = !allChecked;
            const item = cb.closest('.assignee-item');
            if (item) item.classList.toggle('selected', cb.checked);
        });
    },

    renderAssigneeRow(s, assignedIds = []) {
        const isChecked = assignedIds.includes(s.id);
        return `
            <div class="assignee-item ${isChecked ? 'selected' : ''}" onclick="Tasks.toggleAssigneeRow(this, event)">
                <div class="d-flex align-items-center gap-2">
                    <input class="form-check-input" type="checkbox" value="${s.id}" id="stu-${s.id}"
                           ${isChecked ? 'checked' : ''}
                           onclick="event.stopPropagation(); Tasks.syncAssigneeRow(this)">
                    <label class="form-check-label mb-0" for="stu-${s.id}" style="font-size:0.85rem;color:var(--text-secondary);cursor:pointer;flex:1;">
                        ${s.full_name} <span class="text-muted small">(${s.department || 'Giảng viên'})</span>
                    </label>
                </div>
            </div>
        `;
    },

    syncAssigneeRow(checkbox) {
        const row = checkbox.closest('.assignee-item');
        if (row) row.classList.toggle('selected', checkbox.checked);
    },

    toggleAssigneeRow(row, event) {
        const checkbox = row.querySelector('input[type="checkbox"]');
        if (checkbox) {
            checkbox.checked = !checkbox.checked;
            this.syncAssigneeRow(checkbox);
        }
    }
};
