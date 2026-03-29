const AdminQnA = {
    questions: [],
    currentPage: 1,
    totalPages: 1,
    perPage: 10,
    searchQuery: '',
    isLoading: false,
    deleteTarget: null, // { type, id }

    async init() {
        this.currentPage = 1;
        this.questions = [];
        await this.loadQuestions();
        this.setupEventListeners();
    },

    setupEventListeners() {
        const confirmBtn = document.getElementById('btn-confirm-delete');
        if (confirmBtn) {
            confirmBtn.onclick = () => this.executeDelete();
        }
    },

    async loadQuestions(append = false) {
        if (this.isLoading) return;
        this.isLoading = true;

        try {
            const url = `/qna/admin/questions?page=${this.currentPage}&per_page=${this.perPage}&search=${encodeURIComponent(this.searchQuery)}`;
            const response = await API.get(url);

            if (response) {
                if (append) {
                    this.questions = [...this.questions, ...response.questions];
                } else {
                    this.questions = response.questions;
                }

                this.totalPages = response.pages;
                this.render();

                const loadMoreBtn = document.getElementById('load-more-container');
                if (loadMoreBtn) {
                    if (this.currentPage < this.totalPages) {
                        loadMoreBtn.classList.remove('d-none');
                    } else {
                        loadMoreBtn.classList.add('d-none');
                    }
                }
            }
        } catch (error) {
            console.error('Error loading questions:', error);
            Toast.error('Không thể tải danh sách thảo luận');
        } finally {
            this.isLoading = false;
        }
    },

    async loadMore() {
        if (this.currentPage < this.totalPages) {
            this.currentPage++;
            await this.loadQuestions(true);
        }
    },

    handleSearch(e) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.searchQuery = e.target.value.trim();
            this.currentPage = 1;
            this.questions = [];
            this.loadQuestions();
        }, 500);
    },

    render() {
        const container = document.getElementById('admin-qna-list');
        if (!container) return;

        if (this.questions.length === 0) {
            container.innerHTML = `
                <div class="glass-card text-center py-5">
                    <i class="fas fa-comments text-muted mb-3 d-block" style="font-size: 3rem; opacity: 0.2;"></i>
                    <p class="text-muted">Không có thảo luận nào</p>
                </div>`;
            return;
        }

        container.innerHTML = this.questions.map(q => this.renderQuestionCard(q)).join('');
    },

    renderQuestionCard(q) {
        return `
            <div class="qna-admin-card" id="question-card-${q.id}">
                <div class="qna-user-header">
                    <div class="sidebar-user-avatar">${this.getInitials(q.asker_name)}</div>
                    <div class="qna-user-info">
                        <h6>${this.escapeHtml(q.asker_name)}</h6>
                        <div class="qna-user-meta">
                            <span>${q.asker_role || 'Thành viên'}</span>
                            <span class="text-separator">•</span>
                            <span>${this.timeAgo(q.created_at)}</span>
                            <span class="text-separator">•</span>
                            <i class="far fa-comments"></i> ${q.answers_count}
                           <!-- ${q.is_resolved ? '<button class="btn-resolve" disabled><i class="fas fa-check"></i> Đã giải quyết</button>' : ''} -->
                        </div>
                    </div>
                </div>

                <div class="qna-content">
                    ${this.escapeHtml(q.content).replace(/\n/g, '<br>')}
                </div>

                <div class="discussion-section-header" onclick="AdminQnA.toggleComments(${q.id})">
                    <h6>Thảo luận & Phản hồi (${q.answers_count})</h6>
                    <i class="fas fa-chevron-down" id="chevron-${q.id}"></i>
                </div>

                <div id="comments-${q.id}" class="d-none">
                    <div class="comment-list">
                        ${this.renderAnswers(q)}
                    </div>

                    <div class="admin-input-area">
                        <textarea class="admin-textarea" id="reply-input-${q.id}" placeholder="Viết phản hồi hoặc ghi chú..."></textarea>
                        <div class="d-flex justify-content-end">
                            <button class="btn-primary-custom" onclick="AdminQnA.submitReply(${q.id})">Gửi bình luận</button>
                        </div>
                    </div>
                </div>

                <div class="mt-3">
                    <button class="btn-primary-custom px-4 py-2" onclick="AdminQnA.confirmDelete('question', ${q.id})">
                        <i class="fas fa-trash-alt me-1"></i> Xóa thảo luận
                    </button>
                   <!-- ${!q.is_resolved ? `
                        <button class="px-4 py-2" style="background:linear-gradient(135deg, #22c55e, #16a34a); color: white; border: none; padding: 10px 24px; border-radius: var(--radius-sm); font-weight: 600; font-size: 0.85rem; cursor: pointer; transition: all var(--transition-fast); display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 15px var(--primary-glow);" onclick="AdminQnA.markResolved(${q.id})">
                            <i class="fas fa-check me-1"></i> Đánh dấu đã giải quyết
                        </button>
                    ` : ''} -->
                </div>
            </div>
        `;
    },

    toggleComments(id) {
        const el = document.getElementById(`comments-${id}`);
        const chevron = document.getElementById(`chevron-${id}`);
        if (el) {
            el.classList.toggle('d-none');
            if (chevron) {
                chevron.classList.toggle('fa-chevron-down');
                chevron.classList.toggle('fa-chevron-up');
            }
        }
    },

    renderAnswers(question) {
        const answers = question.answers || [];
        if (answers.length === 0) return '';

        const roots = answers.filter(a => !a.parent_id);
        const childrenMap = {};
        answers.forEach(a => {
            if (a.parent_id) {
                if (!childrenMap[a.parent_id]) childrenMap[a.parent_id] = [];
                childrenMap[a.parent_id].push(a);
            }
        });

        const renderRecursive = (items, level = 0) => {
            return items.map(a => {
                const children = childrenMap[a.id] || [];
                let html = `
                    <div class="comment-item" id="comment-${a.id}">
                        <div class="sidebar-user-avatar">${this.getInitials(a.answerer_name)}</div>
                        <div class="comment-body">
                            <div class="comment-author">
                                ${this.escapeHtml(a.answerer_name)}
                                ${a.parent_name ? `<span class="reply-badge"><i class="fas fa-reply"></i> trả lời ${this.escapeHtml(a.parent_name)}</span>` : ''}
                            </div>
                            <div class="comment-email">${this.escapeHtml(a.answerer_email || '')}</div>
                            <div class="comment-text">${this.escapeHtml(a.content).replace(/\n/g, '<br>')}</div>
                            <div class="comment-actions">
                                <a class="btn-action-link" onclick="AdminQnA.handleReplyClick(${question.id}, ${a.id}, '${a.answerer_name}')">Trả lời</a>
                                <a class="btn-action-link btn-action-delete" onclick="AdminQnA.confirmDelete('comment', ${a.id})">Xóa</a>
                            </div>
                            ${children.length > 0 ? `<div class="nested-comments">${renderRecursive(children, level + 1)}</div>` : ''}
                        </div>
                    </div>
                `;
                return html;
            }).join('');
        };

        return renderRecursive(roots);
    },

    handleReplyClick(questionId, answerId, name) {
        const input = document.getElementById(`reply-input-${questionId}`);
        if (input) {
            input.value = `@${name} `;
            input.focus();
            this.replyingToId = answerId;
        }
    },

    async submitReply(questionId) {
        const input = document.getElementById(`reply-input-${questionId}`);
        const content = input.value.trim();
        if (!content) return;

        try {
            await API.post('/qna/answers', {
                content: content,
                question_id: questionId,
                parent_id: this.replyingToId || null
            });
            Toast.success('Gửi bình luận thành công');
            input.value = '';
            this.replyingToId = null;
            // Refresh this question data
            const updated = await API.get(`/qna/questions/${questionId}`);
            if (updated && updated.question) {
                this.questions = this.questions.map(q => q.id === questionId ? updated.question : q);
                this.render();
                // Keep open
                this.toggleComments(questionId);
            }
        } catch (error) {
            Toast.error(error.message);
        }
    },

    getInitials(name) {
        if (!name) return '??';
        return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
    },

    timeAgo(dateStr) {
        const date = new Date(dateStr);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);

        let interval = seconds / 31536000;
        if (interval > 1) return Math.floor(interval) + " năm trước";
        interval = seconds / 2592000;
        if (interval > 1) return Math.floor(interval) + " tháng trước";
        interval = seconds / 86400;
        if (interval > 1) return Math.floor(interval) + " ngày trước";
        interval = seconds / 3600;
        if (interval > 1) return Math.floor(interval) + " giờ trước";
        interval = seconds / 60;
        if (interval > 1) return Math.floor(interval) + " phút trước";
        return Math.floor(seconds) + " giây trước";
    },

    confirmDelete(type, id) {
        this.deleteTarget = { type, id };
        const msg = type === 'question'
            ? 'Bạn có chắc chắn muốn xóa toàn bộ thảo luận này không? Tất cả bình luận liên quan cũng sẽ bị xóa.'
            : 'Bạn có chắc chắn muốn xóa bình luận này không?';

        const modalMsg = document.getElementById('delete-modal-message');
        if (modalMsg) modalMsg.textContent = msg;

        const modalEl = document.getElementById('deleteModal');
        if (modalEl) {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        }
    },

    async executeDelete() {
        if (!this.deleteTarget) return;
        const { type, id } = this.deleteTarget;

        try {
            if (type === 'question') {
                await API.delete(`/qna/questions/${id}`);
                Toast.success('Đã xóa thảo luận');
                this.questions = this.questions.filter(q => q.id !== id);
            } else {
                await API.delete(`/qna/answers/${id}`);
                Toast.success('Đã xóa bình luận');
                // Deep refresh or filter
                this.questions = this.questions.map(q => {
                    if (q.answers) {
                        q.answers = q.answers.filter(a => a.id !== id);
                    }
                    return q;
                });
            }
            this.render();

            const modalEl = document.getElementById('deleteModal');
            if (modalEl) {
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
            }
        } catch (error) {
            Toast.error(error.message || 'Không thể xóa');
        }
    },

    async markResolved(id) {
        try {
            await API.put(`/qna/questions/${id}/resolve`);
            Toast.success('Đã đánh dấu đã giải quyết');

            this.questions = this.questions.map(q => {
                if (q.id === id) q.is_resolved = true;
                return q;
            });
            this.render();
        } catch (error) {
            Toast.error(error.message || 'Không thể thực hiện');
        }
    },

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};
