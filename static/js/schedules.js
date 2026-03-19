const TypeConfig = {
    main: { color: '#d4ac0d', label: 'Dạy chính' },
    makeup: { color: '#2980b9', label: 'Dạy bù' },
    homeroom: { color: '#8e44ad', label: 'Sinh hoạt chủ nhiệm' },
    absent: { color: '#c0392b', label: 'Đã báo vắng' },
    substitute: { color: '#27ae60', label: 'Dạy thay' },
    other: { color: '#16a085', label: 'Sự kiện khác' },
};

const Schedules = {
    calendar: null,
    currentScheduleRef: null,
    allSchedules: [],
    academicYears: [],
    activeAcademicYear: null,

    async init() {
        this.initDOM();
        this.initModalActions();
        
        await this.loadAcademicYears();
        
        const role = sessionStorage.getItem('role');
        if (role === 'admin') {
            await this.loadTeachersFilter();
        }
        
        await this.initCalendar();

        // Realtime update when notification received
        window.addEventListener('new-notification', () => {
            console.log('Realtime update: Schedule calendar refreshing...');
            this.loadSchedules();
        });

        // Periodic fallback
        setInterval(() => this.loadSchedules(), 30000);
    },

    async loadAcademicYears() {
        try {
            const data = await API.get('/academic-years');
            this.academicYears = data.academic_years || [];
            this.activeAcademicYear = this.academicYears.find(y => y.is_active) || null;
            this.populateSemesterFilter();
        } catch (e) { /* silent */ }
    },

    populateSemesterFilter() {
        const filter = document.getElementById('semester-filter');
        if (!filter) return;

        filter.innerHTML = '<option value="">Tất cả năm học / học kỳ</option>';

        this.academicYears.forEach(y => {
            const semesters = ['Học kỳ I', 'Học kỳ II', 'Học kỳ III'];
            semesters.forEach(sem => {
                const opt = document.createElement('option');
                opt.value = `${y.name}|${sem}`;
                opt.textContent = `${y.name} / ${sem}`;
                if (y.is_active) opt.textContent += ' ✓';
                filter.appendChild(opt);
            });
        });

        // Auto-select active year's semester II as default
        if (this.activeAcademicYear) {
            const defaultVal = `${this.activeAcademicYear.name}|Học kỳ II`;
            filter.value = defaultVal;
        }
    },

    async loadTeachersFilter() {
        const filter = document.getElementById('teacher-filter');
        if (!filter) return;

        try {
            const data = await API.get('/users');
            if (data && data.users) {
                const teachers = data.users.filter(u => u.role === 'teacher');
                
                // Keep "Tất cả giảng viên" as first option
                filter.innerHTML = '<option value="all">Tất cả giảng viên</option>';
                
                teachers.forEach(t => {
                    const opt = document.createElement('option');
                    opt.value = t.id;
                    opt.textContent = `${t.full_name} (@${t.username})`;
                    filter.appendChild(opt);
                });
            }
        } catch (e) {
            console.error('Error loading teachers for filter', e);
        }
    },



    async initCalendar() {
        const calendarEl = document.getElementById('calendar');
        if (!calendarEl) return;

        this.calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'vi',
            headerToolbar: {
                left: 'prev today next',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            events: async (info) => {
                try {
                    const teacherId = document.getElementById('teacher-filter')?.value || '';
                    const qsTeacher = teacherId ? `&user_id=${teacherId}` : '';
                    const url = `/schedules?start=${encodeURIComponent(info.startStr)}&end=${encodeURIComponent(info.endStr)}&_=${Date.now()}${qsTeacher}`;

                    const data = await API.get(url);
                    this.allSchedules = data.schedules || [];

                    // Render default list if no specific event is active
                    this.renderAllSchedulesList();
                    this.currentScheduleRef = null;

                    return this.allSchedules.map(s => {
                        const typeInfo = TypeConfig[s.event_type] || TypeConfig.main;
                        return {
                            ...s,
                            backgroundColor: 'transparent',
                            borderColor: 'transparent',
                            textColor: 'var(--text-primary)',
                            dotColor: typeInfo.color
                        };
                    });
                } catch (error) {
                    return [];
                }
            },
            eventClick: (info) => {
                this.showDetail(info.event);
            },
            eventContent: function (arg) {
                const start = arg.event.start ? arg.event.start.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) : '';
                const end = arg.event.end ? arg.event.end.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) : '';
                const loc = arg.event.extendedProps.location || '';
                const dotColor = arg.event.extendedProps.dotColor || '#fff';
                const isTimeGrid = arg.view.type.includes('timeGrid');

                if (isTimeGrid) {
                    return {
                        html: `<div style="padding: 2px; font-size: 0.75rem; color: var(--text-primary); border-left: 3px solid ${dotColor}; height: 100%; display: flex; flex-direction: column; gap: 2px; overflow: hidden; background: rgba(255,255,255,0.02);">
                                <div class="fw-bold" style="font-size: 0.7rem;"><i class="far fa-clock text-muted me-2"></i> ${start} - ${end}</div>
                                <div style="font-weight: 600; white-space: normal; line-height: 1.1;"><i class="fas fa-book text-muted me-2"></i> ${arg.event.title}</div>
                                ${loc ? `<div class="text-secondary"><i class="fas fa-map-marker-alt"></i> ${loc}</div>` : ''}
                               </div>`
                    };
                }

                const title = loc ? `${start} - ${loc}` : start;
                return {
                    html: `<div style="display:flex; align-items:center; gap:6px; font-size:0.85rem; padding: 2px 4px; color:var(--text-primary)">
                            <div style="background:${dotColor}; width:8px; height:8px; border-radius:50%; flex-shrink:0;"></div>
                            <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${title}</span>
                           </div>`
                };
            },
            timeZone: 'local',
            editable: false,
            selectable: true,
            dayMaxEvents: 3,
            height: 'auto',
            eventDisplay: 'auto',
            eventBackgroundColor: 'transparent',
            eventBorderColor: 'transparent',
            slotMinTime: '06:00:00',
            slotMaxTime: '22:00:00',
        });

        this.calendar.render();
    },

    async loadSchedules() {
        if (this.calendar) {
            this.calendar.refetchEvents();
        }
    },

    showCreateModal() {
        this.currentScheduleRef = null;
        const modal = document.getElementById('scheduleModal');
        const form = document.getElementById('scheduleForm');

        document.getElementById('scheduleModalLabel').textContent = 'Thêm lịch giảng dạy';
        form.reset();
        document.getElementById('schedule-id').value = '';
        
        // Reset reminders - Use user's global preference
        const prefs = (sessionStorage.getItem('reminder_preference') || '5').split(',');
        document.querySelectorAll('.reminder-check').forEach(cb => {
            cb.checked = prefs.includes(cb.value);
        });

        bootstrap.Modal.getOrCreateInstance(modal).show();
    },

    async showEditModal(id) {
        const schedule = this.allSchedules.find(s => String(s.id) === String(id));
        if (!schedule) return;

        this.currentScheduleRef = { id: schedule.id, title: schedule.title, extendedProps: schedule };
        const modal = document.getElementById('scheduleModal');

        document.getElementById('scheduleModalLabel').textContent = 'Sửa lịch giảng dạy';
        document.getElementById('schedule-id').value = schedule.id;
        document.getElementById('schedule-title').value = schedule.title;
        document.getElementById('schedule-type').value = schedule.event_type || 'main';
        document.getElementById('schedule-location').value = schedule.location || '';
        document.getElementById('schedule-start').value = schedule.start_time ? schedule.start_time.slice(0, 16) : '';
        document.getElementById('schedule-end').value = schedule.end_time ? schedule.end_time.slice(0, 16) : '';
        document.getElementById('schedule-course-code').value = schedule.course_code || '';
        document.getElementById('schedule-course-name').value = schedule.course_name || '';
        document.getElementById('schedule-class-group').value = schedule.class_group || '';
        document.getElementById('schedule-description').value = schedule.description || '';

        // Load reminders
        document.querySelectorAll('.reminder-check').forEach(cb => cb.checked = false);
        try {
            const res = await API.get(`/reminders/schedule/${id}`);
            if (res && res.reminders) {
                const offsets = res.reminders.map(r => String(r.offset_minutes));
                document.querySelectorAll('.reminder-check').forEach(cb => {
                    if (offsets.includes(cb.value)) cb.checked = true;
                });
            }
        } catch (e) {
            console.error('Error loading reminders:', e);
        }

        bootstrap.Modal.getOrCreateInstance(modal).show();
    },

    async submitForm(e) {
        e.preventDefault();
        const scheduleId = document.getElementById('schedule-id').value;

        const payload = {
            title: document.getElementById('schedule-title').value,
            description: document.getElementById('schedule-description').value,
            event_type: document.getElementById('schedule-type').value,
            start_time: document.getElementById('schedule-start').value,
            end_time: document.getElementById('schedule-end').value,
            course_name: document.getElementById('schedule-course-name').value,
            course_code: document.getElementById('schedule-course-code').value,
            class_group: document.getElementById('schedule-class-group').value,
            location: document.getElementById('schedule-location').value
        };

        const offsets = [];
        document.querySelectorAll('.reminder-check:checked').forEach(cb => {
            offsets.push(parseInt(cb.value));
        });

        try {
            const start = payload.start_time;
            const end = payload.end_time;

            if (new Date(start) >= new Date(end)) {
                Toast.error('Thời gian kết thúc phải sau thời gian bắt đầu');
                return;
            }

            let savedId = scheduleId;
            if (scheduleId) {
                await API.put(`/schedules/${scheduleId}`, payload);
            } else {
                const res = await API.post('/schedules', payload);
                savedId = res.schedule.id;
            }
            
            // Save reminders
            await API.post(`/reminders/schedule/${savedId}`, { offsets });

            Toast.success('Lưu lịch giảng dạy và nhắc hẹn thành công');
            bootstrap.Modal.getOrCreateInstance(document.getElementById('scheduleModal')).hide();

            setTimeout(() => this.loadSchedules(), 300);
        } catch (error) {
            Toast.error(error.message);
        }
    },

    suggestReminders() {
        const title = (document.getElementById('schedule-title').value || '').toLowerCase();
        const loc = (document.getElementById('schedule-location').value || '').toLowerCase();
        const type = document.getElementById('schedule-type').value;
        
        // Uncheck others, but keep 5m as base default
        document.querySelectorAll('.reminder-check').forEach(cb => cb.checked = (cb.id === 'rem-5m'));
        
        // Logical rules
        if (title.includes('thi') || title.includes('kiểm tra') || title.includes('exam')) {
            // Important: 1 day + 1 hour
            document.getElementById('rem-1d').checked = true;
            document.getElementById('rem-1h').checked = true;
        } else if (loc.includes('online') || loc.includes('zoom') || loc.includes('meet')) {
            // Online: 15 min
            document.getElementById('rem-15m').checked = true;
        } else if (type === 'makeup' || type === 'substitute') {
            // Change of routine: 1 day
            document.getElementById('rem-1d').checked = true;
        } else {
            // Default: 1 hour before
            document.getElementById('rem-1h').checked = true;
        }
        
        Toast.info('💡 Hệ thống đã gợi ý mốc nhắc hẹn tối ưu cho bạn.');
    },

    initDOM() {
        const teacherFilter = document.getElementById('teacher-filter');
        if (teacherFilter) {
            teacherFilter.addEventListener('change', () => {
                this.loadSchedules();
            });
        }

        const modalSearch = document.getElementById('modal-course-search');
        if (modalSearch) {
            modalSearch.addEventListener('input', () => {
                this.renderAllSchedulesList(modalSearch.value);
            });
        }
    },

    async showListModal() {
        const query = document.getElementById('modal-course-search')?.value || '';
        const container = document.getElementById('modal-list-content');
        if (container) container.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"></div></div>';

        try {
            const teacherId = document.getElementById('teacher-filter')?.value || '';
            const qsTeacher = teacherId ? `user_id=${teacherId}` : '';
            const data = await API.get(`/schedules?${qsTeacher}&_=${Date.now()}`);
            this.allSchedules = data.schedules || [];
            this.renderAllSchedulesList(query);
            bootstrap.Modal.getOrCreateInstance(document.getElementById('eventListModal')).show();
        } catch (error) {
            Toast.error('Không thể tải danh sách sự kiện');
        }
    },

    renderAllSchedulesList(query = '') {
        const container = document.getElementById('modal-list-content');
        if (!container) return;

        const filtered = this.allSchedules.filter(s => {
            if (!query) return true;
            const q = query.toLowerCase();
            return s.title.toLowerCase().includes(q) ||
                (s.location && s.location.toLowerCase().includes(q)) ||
                (s.course_name && s.course_name.toLowerCase().includes(q));
        });

        if (filtered.length === 0) {
            container.innerHTML = '<div class="text-muted text-center" style="font-size:0.85rem; margin-top:20px;">Không tìm thấy sự kiện nào.</div>';
            return;
        }

        let html = '';
        filtered.forEach(s => {
            const typeInfo = TypeConfig[s.event_type] || TypeConfig.main;
            const startDate = new Date(s.start_time);
            const timeStr = startDate.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
            const dateStr = startDate.toLocaleDateString('vi-VN');

            html += `
                <div class="course-item" onclick="Schedules.showDetailFromList(${s.id})">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="background:${typeInfo.color}; width:10px; height:10px; border-radius:50%; flex-shrink:0;"></div>
                        <div style="flex:1;">
                            <div class="fw-bold" style="font-size:0.9rem;">${s.title}</div>
                            <div class="text-muted" style="font-size:0.75rem;">
                                <i class="far fa-clock me-1"></i>${timeStr} - ${dateStr}
                                ${s.location ? ` | <i class="fas fa-map-marker-alt ms-1 me-1"></i>${s.location}` : ''}
                            </div>
                        </div>
                        <i class="fas fa-chevron-right text-muted" style="font-size:0.7rem;"></i>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    },

    showDetailFromList(id) {
        // Hide list modal first
        const listModal = bootstrap.Modal.getInstance(document.getElementById('eventListModal'));
        if (listModal) listModal.hide();

        // Find matching event generated by FullCalendar
        const eventObj = this.calendar.getEventById(String(id));
        if (eventObj) {
            this.showDetail(eventObj);
        } else {
            // Find raw obj
            const schedule = this.allSchedules.find(s => String(s.id) === String(id));
            if (schedule) {
                this.showDetail({
                    id: schedule.id,
                    title: schedule.title,
                    extendedProps: schedule,
                    startStr: schedule.start,
                    endStr: schedule.end
                });
            }
        }
    },

    initModalActions() {
        const btnEdit = document.getElementById('btn-edit-schedule');
        const btnDelete = document.getElementById('btn-delete-schedule');

        if (btnEdit) {
            btnEdit.addEventListener('click', () => {
                bootstrap.Modal.getOrCreateInstance(document.getElementById('scheduleDetailModal')).hide();
                if (this.currentScheduleRef) {
                    this.showEditModal(this.currentScheduleRef.id);
                }
            });
        }

        if (btnDelete) {
            btnDelete.addEventListener('click', () => {
                if (this.currentScheduleRef) {
                    this.deleteSchedule(this.currentScheduleRef.id);
                }
            });
        }
    },

    showDetail(event) {
        this.currentScheduleRef = event;
        const props = event.extendedProps || {};
        const typeInfo = TypeConfig[props.event_type] || TypeConfig.main;
        const role = sessionStorage.getItem('role');

        const teacherHtml = (role === 'admin' && props.creator_name) ? `
            <div style="grid-column: span 2; margin-top: 8px; border-top: 1px dashed var(--glass-border); padding-top: 8px;">
                <i class="fas fa-user-tie text-muted me-2"></i>Giảng viên: <strong class="text-primary">${props.creator_name}</strong>
            </div>` : '';

        const detailHtml = `
            <div style="margin-bottom:16px;">
                <h5 style="font-weight:700; margin-bottom:8px;">${event.title}</h5>
                <span class="badge" style="background:${typeInfo.color}; color:#fff; border-radius:12px; font-weight:500; padding:4px 10px;">${typeInfo.label}</span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:0.85rem;">
                <div><i class="far fa-clock text-muted me-2"></i>Bắt đầu:<br><strong>${formatDateTime(event.startStr)}</strong></div>
                <div><i class="far fa-clock text-muted me-2"></i>Kết thúc:<br><strong>${formatDateTime(event.endStr)}</strong></div>
                <div><i class="fas fa-map-marker-alt text-muted me-2"></i>Phòng:<br><strong>${props.location || '—'}</strong></div>
                <div><i class="fas fa-book text-muted me-2"></i>Lớp/Nhóm:<br><strong>${props.class_group || '—'}</strong></div>
                <div style="grid-column: span 2;"><i class="fas fa-info-circle text-muted me-2"></i>Học phần:<br><strong>${props.course_code ? `[${props.course_code}] ` : ''}${props.course_name || '—'}</strong></div>
                ${teacherHtml}
            </div>
            ${props.description ? `<div style="margin-top:16px;"><span class="text-white" style="font-size:0.8rem;">Mô tả:</span><p style="color:var(--text-secondary);font-size:0.9rem;margin-top:4px;">${props.description}</p></div>` : ''}
        `;

        document.getElementById('scheduleDetailBody').innerHTML = detailHtml;
        bootstrap.Modal.getOrCreateInstance(document.getElementById('scheduleDetailModal')).show();
    },

    async deleteSchedule(scheduleId) {
        if (!confirm('Bạn có chắc muốn xóa lịch này vĩnh viễn?')) return;
        try {
            await API.delete(`/schedules/${scheduleId}`);
            Toast.success('Xóa lịch học thành công');
            bootstrap.Modal.getOrCreateInstance(document.getElementById('scheduleDetailModal')).hide();
            this.loadSchedules();
        } catch (error) {
            Toast.error('Không thể xóa lịch học');
        }
    },
};
