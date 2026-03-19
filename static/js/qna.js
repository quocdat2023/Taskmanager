const QnA = {
    questions: [],
    filter: 'all', // all, unresolved, mine
    searchQuery: '',

    async init() {
        await this.loadQuestions();
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
                    <button class="btn btn-link text-primary mt-2" onclick="QnA.resetFilters()">Xóa tất cả bộ lọc</button>
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
                    <div class="ms-2">
                        ${q.is_resolved ? 
                            '<span class="badge bg-success bg-opacity-10 text-success border-0 px-3 py-2"><i class="fas fa-check-circle me-1"></i> Đã giải quyết</span>' : 
                            '<span class="badge bg-warning bg-opacity-10 text-warning border-0 px-3 py-2"><i class="fas fa-clock me-1"></i> Đang chờ</span>'}
                    </div>
                </div>
                
                <div class="qna-question-content mb-4" style="line-height:1.7; color:var(--text-secondary);">${q.content}</div>

                <!-- Answers Section -->
                <div class="answers-wrapper mt-4 pt-3 border-top border-secondary border-opacity-10">
                    <div class="d-flex align-items-center mb-3">
                        <i class="fas fa-comments text-muted me-2"></i>
                        <span class="fw-bold small">${q.answers_count} Câu trả lời</span>
                    </div>

                    ${(q.answers || []).map(a => `
                        <div class="qna-answer mb-3 p-3 rounded-3" style="background: rgba(0,0,0,0.02); border-left: 2px solid rgba(108, 92, 231, 0.3);">
                            <div class="d-flex align-items-center gap-2 mb-2" style="font-size:0.75rem;">
                                <div class="sidebar-user-avatar" style="width:24px; height:24px; font-size: 0.6rem;">${getInitials(a.answerer_name)}</div>
                                <span class="fw-bold">${a.answerer_name}</span>
                                ${getRoleBadge(a.answerer_role)}
                                <span class="text-muted ms-auto">${timeAgo(a.created_at)}</span>
                            </div>
                            <div style="font-size:0.85rem; line-height:1.6; color:var(--text-secondary);">${a.content}</div>
                        </div>
                    `).join('')}
                </div>

                <div class="actions-footer mt-4 d-flex flex-wrap gap-2 align-items-center">
                    <button class="btn btn-sm btn-primary-custom px-3" onclick="QnA.showAnswerForm(${q.id})">
                        <i class="fas fa-reply me-1"></i> Trả lời
                    </button>
                    ${!q.is_resolved ? `
                        <button class="btn btn-sm btn-success px-3" onclick="QnA.resolveQuestion(${q.id})">
                            <i class="fas fa-check-circle me-1"></i> Đánh dấu hoàn tất
                        </button>
                    ` : ''}
                    
                    <div class="ms-auto small text-muted">
                        Cập nhật lúc: ${formatDateTime(q.updated_at)}
                    </div>
                </div>

                <div id="answer-form-${q.id}" class="mt-3 p-3 bg-light rounded-3" style="display:none;">
                    <label class="form-label-custom small mb-2">Viết câu trả lời của bạn</label>
                    <textarea class="form-control-custom bg-white mb-2" id="answer-content-${q.id}" placeholder="Chia sẻ kiến thức của bạn..." rows="3"></textarea>
                    <div class="d-flex gap-2">
                        <button class="btn-primary-custom py-1 px-3 fs-7" onclick="QnA.submitAnswer(${q.id})">Gửi trả lời</button>
                        <button class="btn btn-sm btn-light py-1 px-3 border" onclick="document.getElementById('answer-form-${q.id}').style.display='none'">Hủy</button>
                    </div>
                </div>
            </div>
        `).join('');
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

        const sorted = Object.entries(courses).sort((a,b) => b[1] - a[1]).slice(0, 5);
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

    showAnswerForm(questionId) {
        const form = document.getElementById(`answer-form-${questionId}`);
        if (form) form.style.display = 'block';
    },

    async submitAnswer(questionId) {
        const content = document.getElementById(`answer-content-${questionId}`).value.trim();
        if (!content) {
            Toast.error('Vui lòng nhập câu trả lời');
            return;
        }

        try {
            await API.post('/qna/answers', {
                content: content,
                question_id: questionId,
            });
            Toast.success('Trả lời thành công');
            await this.loadQuestions();
        } catch (error) {
            Toast.error(error.message);
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
