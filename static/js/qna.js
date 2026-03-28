const QnA = {
    questions: [],
    filter: 'all', // all, unresolved, mine
    searchQuery: '',
    replyingTo: {}, // { questionId: { id, name, email } }
    openDiscussions: new Set(),

    async init() {
        await this.loadQuestions();
        this.initSocket();
    },

    initSocket() {
        // Use the shared Realtime socket directly if it exists, otherwise it will be handles by global listeners
        window.addEventListener('qna-realtime-update', async (e) => {
            const data = e.detail;
            console.log('[QnA] Realtime update:', data);

            // Re-load questions to sync state
            await this.loadQuestions();
            Toast.info(data.action === 'new_answer' ? 'Có bình luận mới trong thảo luận' : 'Thảo luận đã được cập nhật');
        });
    },

    async loadQuestions() {
        try {
            const data = await API.get('/qna/questions');
            if (data) {
                this.questions = data.questions || [];
                this.render();
                this.updateStats();
            }
        } catch (error) {
            Toast.error('Không thể tải danh sách câu hỏi');
        }
    },

    setFilter(filter, el) {
        this.filter = filter;
        document.querySelectorAll('.qna-filter').forEach(b => b.classList.remove('active'));
        el.classList.add('active');
        this.render();
    },

    handleSearch(e) {
        this.searchQuery = e.target.value.toLowerCase().trim();
        this.render();
    },

    getFilteredQuestions() {
        let filtered = [...this.questions];

        // Apply tab filter
        if (this.filter === 'unresolved') {
            filtered = filtered.filter(q => !q.is_resolved);
        } else if (this.filter === 'mine') {
            const currentUserId = parseInt(sessionStorage.getItem('user_id') || '0');
            filtered = filtered.filter(q => q.asker_id === currentUserId);
        }

        // Apply search query
        if (this.searchQuery) {
            filtered = filtered.filter(q =>
                q.title.toLowerCase().includes(this.searchQuery) ||
                q.content.toLowerCase().includes(this.searchQuery) ||
                (q.course_name && q.course_name.toLowerCase().includes(this.searchQuery))
            );
        }

        return filtered;
    },

    render() {
        const container = document.getElementById('qna-list');
        const countEl = document.getElementById('qna-count');
        if (!container) return;

        const filtered = this.getFilteredQuestions();
        if (countEl) countEl.textContent = `Hiển thị ${filtered.length} câu hỏi`;

        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="glass-card text-center py-5">
                    <i class="fas fa-search text-muted mb-3 d-block" style="font-size: 3rem; opacity: 0.2;"></i>
                    <p class="text-muted">Không tìm thấy câu hỏi nào phù hợp</p>
                    <button class="btn text-danger mt-2" onclick="QnA.resetFilters()">Xóa tất cả bộ lọc</button>
                </div>`;
            return;
        }

        container.innerHTML = filtered.map(q => `
            <div class="glass-card mb-4 fade-in border-0 shadow-sm" style="border-left: 4px solid ${q.is_resolved ? 'var(--accent-green)' : 'var(--accent-orange)'} !important;">
                <div class="qna-question-header mb-3">
                    <div class="sidebar-user-avatar" style="width:42px; height:42px; font-size: 0.9rem;">${getInitials(q.asker_name)}</div>
                    <div style="flex:1; min-width:0;">
                        <h5 class="fw-bold mb-1" style="font-size:1.05rem;">${q.title}</h5>
                        <div class="d-flex align-items-center flex-wrap gap-2 mt-1" style="font-size:0.75rem; color:var(--text-muted);">
                            <span class="fw-bold text-secondary">${q.asker_name}</span>
                            <span>•</span>
                            <span>${timeAgo(q.created_at)}</span>
                            ${q.course_name ? `<span>•</span> <span class="badge bg-secondary bg-opacity-10 text-secondary border-0"><i class="fas fa-book me-1"></i>${q.course_name}</span>` : ''}
                        </div>
                    </div>
                    <!--<div class="ms-2">
                        ${q.is_resolved ?
                '<span class="badge bg-success bg-opacity-10 text-success border-0 px-3 py-2"><i class="fas fa-check-circle me-1"></i> Đã giải quyết</span>' :
                '<span class="badge bg-warning bg-opacity-10 text-warning border-0 px-3 py-2"><i class="fas fa-clock me-1"></i> Đang chờ</span>'}
                    </div>-->
                </div>
                
                <div class="qna-question-content mb-4" style="line-height:1.7; color:var(--text-secondary);">${q.content}</div>

                <div class="qna-discussion-header mt-5 d-flex align-items-center justify-content-between" 
                     onclick="QnA.toggleDiscussion(${q.id})" style="user-select: none;">
                    <h6 class="fw-bold fs-6 mb-0">Thảo luận & Phản hồi (${q.answers_count})</h6>
                    <i class="fas fa-${this.openDiscussions.has(q.id) ? 'chevron-up' : 'chevron-down'} discussion-chevron" id="chevron-${q.id}"></i>
                </div>

                <div id="discussion-content-${q.id}" class="discussion-content-wrapper" style="display: ${this.openDiscussions.has(q.id) ? 'block' : 'none'};">
                    <!-- Answers Section -->
                    <div class="answers-container" id="answers-container-${q.id}">
                        ${this.renderAnswers(q)}
                    </div>

                    <!-- Discussion Input Area -->
                    <div class="reply-area">
                        <div id="reply-indicator-${q.id}" class="reply-to-indicator">
                            <span><i class="fas fa-reply me-2"></i>Đang trả lời: <strong id="reply-name-${q.id}"></strong></span>
                            <i class="fas fa-times reply-to-close" onclick="QnA.cancelReply(${q.id})"></i>
                        </div>
                        <div class="comment-input-container" id="comment-input-container-${q.id}">
                            <textarea class="comment-textarea" id="answer-content-${q.id}" 
                                      placeholder="Viết phản hồi hoặc ghi chú..." 
                                      onfocus="document.getElementById('comment-input-container-${q.id}').classList.add('active')"
                                      onblur="if(!this.value) document.getElementById('comment-input-container-${q.id}').classList.remove('active')"></textarea>
                            <div class="comment-upload-icon" title="Đính kèm file/ảnh">
                                <i class="fas fa-arrow-up" style="font-size: 0.7rem;"></i>
                            </div>
                        </div>
                        <div class="comment-footer">
                            <button class="btn-primary-custom px-4 py-2" onclick="QnA.submitAnswer(${q.id})">
                                Gửi bình luận
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    },

    toggleDiscussion(questionId) {
        const content = document.getElementById(`discussion-content-${questionId}`);
        const chevron = document.getElementById(`chevron-${questionId}`);
        if (!content) return;

        if (content.style.display === 'none') {
            content.style.display = 'block';
            this.openDiscussions.add(questionId);
            if (chevron) {
                chevron.classList.remove('fa-chevron-down');
                chevron.classList.add('fa-chevron-up');
            }
        } else {
            content.style.display = 'none';
            this.openDiscussions.delete(questionId);
            if (chevron) {
                chevron.classList.remove('fa-chevron-up');
                chevron.classList.add('fa-chevron-down');
            }
        }
    },

    updateStats() {
        const total = this.questions.length;
        const resolved = this.questions.filter(q => q.is_resolved).length;
        const answeredCount = this.questions.filter(q => q.answers_count > 0).length;
        const ratio = total > 0 ? Math.round((answeredCount / total) * 100) : 0;

        document.getElementById('stat-total-q').textContent = total;
        document.getElementById('stat-resolved-q').textContent = resolved;
        document.getElementById('stat-ratio-q').textContent = `${ratio}%`;

        // Update popular courses
        const courses = {};
        this.questions.forEach(q => {
            if (q.course_name) {
                courses[q.course_name] = (courses[q.course_name] || 0) + 1;
            }
        });

        const sorted = Object.entries(courses).sort((a, b) => b[1] - a[1]).slice(0, 5);
        const popularEl = document.getElementById('popular-courses');
        if (popularEl) {
            if (sorted.length === 0) {
                popularEl.innerHTML = '<span class="text-muted small italic">Chưa có môn học nào</span>';
            } else {
                popularEl.innerHTML = sorted.map(([name, count]) => `
                    <span class="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-10 py-2 px-3 fw-normal" 
                          style="cursor:pointer;" onclick="QnA.filterByCourse('${name}')">
                        ${name} <span class="bg-primary text-white ms-1 rounded-circle" style="padding: 0 5px; font-size:0.6rem;">${count}</span>
                    </span>
                `).join('');
            }
        }
    },

    filterByCourse(name) {
        document.getElementById('qna-search').value = name;
        this.searchQuery = name.toLowerCase();
        this.render();
    },

    resetFilters() {
        this.filter = 'all';
        this.searchQuery = '';
        document.getElementById('qna-search').value = '';
        document.querySelectorAll('.qna-filter').forEach(b => {
            b.classList.toggle('active', b.onclick.toString().includes('all'));
        });
        this.render();
    },

    showCreateModal() {
        const modal = document.getElementById('questionModal');
        document.getElementById('questionForm').reset();
        bootstrap.Modal.getOrCreateInstance(modal).show();
    },

    async submitQuestion(e) {
        e.preventDefault();
        const payload = {
            title: document.getElementById('question-title').value,
            content: document.getElementById('question-content').value,
            course_name: document.getElementById('question-course').value,
        };

        try {
            await API.post('/qna/questions', payload);
            Toast.success('Đặt câu hỏi thành công');
            bootstrap.Modal.getOrCreateInstance(document.getElementById('questionModal')).hide();
            await this.loadQuestions();
        } catch (error) {
            Toast.error(error.message);
        }
    },

    renderAnswers(question) {
        const answers = question.answers || [];
        if (answers.length === 0) {
            return '<p class="text-muted small italic px-3">Chưa có thảo luận nào.</p>';
        }

        const roots = answers.filter(a => !a.parent_id);
        const childrenMap = {};
        answers.forEach(a => {
            if (a.parent_id) {
                if (!childrenMap[a.parent_id]) childrenMap[a.parent_id] = [];
                childrenMap[a.parent_id].push(a);
            }
        });

        const currentUserId = parseInt(sessionStorage.getItem('user_id') || '0');
        const userRole = sessionStorage.getItem('role');

        const renderRecursive = (items, level = 0) => {
            return items.map(a => {
                const children = childrenMap[a.id] || [];
                return this.renderAnswerItem(a, level > 0, currentUserId, userRole, level, renderRecursive(children, level + 1));
            }).join('');
        };

        return renderRecursive(roots);
    },

    renderAnswerItem(a, isReply, currentUserId, userRole, level = 0, childrenHtml = '') {
        const canDelete = (a.answered_by === currentUserId || userRole === 'admin');

        return `
            <div class="comment-wrapper" id="answer-${a.id}">
                <div class="comment-item ${level > 0 ? 'reply' : ''}">
                    <div class="sidebar-user-avatar" style="width:32px; height:32px; font-size:0.7rem; flex-shrink:0;">${getInitials(a.answerer_name)}</div>
                    <div class="comment-body">
                        <div class="comment-author-name">
                            ${a.answerer_name} 
                            ${a.parent_name ? `<span class="text-muted small ms-2 fw-normal" style="opacity:0.7;"><i class="fas fa-reply me-1"></i>trả lời <strong>${a.parent_name}</strong></span>` : ''}
                        </div>
                        <div class="comment-author-email">${a.answerer_email || ''}</div>
                        <div class="comment-content">${a.content}</div>
                        <div class="comment-actions">
                            <a onclick="QnA.handleReplyClick(${a.question_id}, ${a.id}, '${a.answerer_name}', '${a.answerer_email}')">Trả lời</a>
                            ${canDelete ? `<a class="delete-btn text-danger text-decoration-none" onclick="QnA.deleteAnswer(${a.id})">Xóa</a>` : ''}
                        </div>
                    </div>
                </div>
                ${childrenHtml ? `<div class="children-wrapper">${childrenHtml}</div>` : ''}
            </div>
        `;
    },

    handleReplyClick(questionId, answerId, name, email) {
        this.replyingTo[questionId] = { id: answerId, name, email };

        const indicator = document.getElementById(`reply-indicator-${questionId}`);
        const nameEl = document.getElementById(`reply-name-${questionId}`);
        const inputContainer = document.getElementById(`comment-input-container-${questionId}`);
        const textarea = document.getElementById(`answer-content-${questionId}`);

        if (indicator && nameEl && inputContainer) {
            indicator.style.display = 'flex';
            nameEl.textContent = `${name} - ${email}`;
            inputContainer.classList.add('active');
            inputContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
            textarea.focus();
        }
    },

    cancelReply(questionId) {
        delete this.replyingTo[questionId];
        const indicator = document.getElementById(`reply-indicator-${questionId}`);
        const inputContainer = document.getElementById(`comment-input-container-${questionId}`);
        if (indicator) indicator.style.display = 'none';
        if (inputContainer) inputContainer.classList.remove('active');
    },

    async submitAnswer(questionId) {
        const textarea = document.getElementById(`answer-content-${questionId}`);
        const content = textarea.value.trim();
        if (!content) {
            Toast.error('Vui lòng nhập câu trả lời');
            return;
        }

        const replying = this.replyingTo[questionId];
        const payload = {
            content: content,
            question_id: questionId,
            parent_id: replying ? replying.id : null
        };

        try {
            await API.post('/qna/answers', payload);
            Toast.success('Gửi bình luận thành công');
            textarea.value = '';
            this.cancelReply(questionId);
            await this.loadQuestions();
        } catch (error) {
            Toast.error(error.message);
        }
    },

    async deleteAnswer(answerId) {
        if (!confirm('Bạn có chắc chắn muốn xóa bình luận này?')) return;

        try {
            await API.delete(`/qna/answers/${answerId}`);
            Toast.success('Đã xóa bình luận');
            await this.loadQuestions();
        } catch (error) {
            Toast.error(error.message || 'Không thể xóa bình luận');
        }
    },

    async resolveQuestion(questionId) {
        try {
            await API.put(`/qna/questions/${questionId}/resolve`, {});
            Toast.success('Đánh dấu đã giải quyết');
            await this.loadQuestions();
        } catch (error) {
            Toast.error(error.message);
        }
    },
};
