from app.repositories.base_repository import BaseRepository
from app.models.task import Task, TaskAssignment, TaskHistory, TaskRequest, SubTask, TaskComment, TaskAttachment
from app.extensions import db
from datetime import datetime


class TaskRepository(BaseRepository):
    def __init__(self):
        super().__init__(Task)

    def get_all_tasks(self, semester=None, academic_year=None, status=None, search=None, page=1, per_page=20):
        query = Task.query
        if semester:
            query = query.filter_by(semester=semester)
        if academic_year:
            query = query.filter_by(academic_year=academic_year)
        if status:
            query = query.filter_by(status=status)
        if search:
            like = f'%{search}%'
            query = query.filter(
                db.or_(Task.title.ilike(like), Task.course_name.ilike(like))
            )
        return query.order_by(Task.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def get_tasks_by_creator(self, user_id, semester=None, academic_year=None, status=None, search=None, page=1, per_page=20):
        query = Task.query.filter_by(created_by=user_id)
        if semester:
            query = query.filter_by(semester=semester)
        if academic_year:
            query = query.filter_by(academic_year=academic_year)
        if status:
            query = query.filter_by(status=status)
        if search:
            like = f'%{search}%'
            query = query.filter(
                db.or_(Task.title.ilike(like), Task.course_name.ilike(like))
            )
        return query.order_by(Task.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def get_tasks_by_assignee(self, user_id, semester=None, academic_year=None, status=None, search=None, page=1, per_page=20):
        query = Task.query.join(TaskAssignment).filter(TaskAssignment.user_id == user_id)
        if semester:
            query = query.filter(Task.semester == semester)
        if academic_year:
            query = query.filter(Task.academic_year == academic_year)
        if status:
            query = query.filter(TaskAssignment.status == status)
        if search:
            like = f'%{search}%'
            query = query.filter(
                db.or_(Task.title.ilike(like), Task.course_name.ilike(like))
            )
        return query.order_by(Task.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def get_tasks_by_creator_or_assignee(self, user_id, semester=None, academic_year=None, status=None, search=None, page=1, per_page=20):
        query = Task.query.outerjoin(TaskAssignment).filter(
            db.or_(
                Task.created_by == user_id,
                TaskAssignment.user_id == user_id
            )
        )
        if semester:
            query = query.filter(Task.semester == semester)
        if academic_year:
            query = query.filter(Task.academic_year == academic_year)
        if status:
            query = query.filter(Task.status == status)
        if search:
            like = f'%{search}%'
            query = query.filter(
                db.or_(Task.title.ilike(like), Task.course_name.ilike(like))
            )
        return query.distinct().order_by(Task.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def get_tasks_by_status(self, status, user_id=None):
        query = Task.query.filter_by(status=status)
        if user_id:
            query = query.filter_by(created_by=user_id)
        return query.order_by(Task.created_at.desc()).all()

    def get_overdue_tasks(self):
        return Task.query.filter(
            Task.due_date < datetime.utcnow(),
            Task.status != 'done'
        ).all()

    def create_task(self, title, description, created_by, assignee_ids=None, **kwargs):
        task = Task(
            title=title,
            description=description,
            created_by=created_by,
            **kwargs
        )
        db.session.add(task)
        db.session.flush()

        if assignee_ids:
            for uid in assignee_ids:
                assignment = TaskAssignment(task_id=task.id, user_id=uid)
                db.session.add(assignment)

        db.session.commit()
        return task

    def update_task_status(self, task_id, status):
        task = self.get_by_id(task_id)
        if task:
            task.status = status
            db.session.commit()
        return task

    def update_task(self, task_id, **kwargs):
        task = self.get_by_id(task_id)
        if not task:
            return None
        assignee_ids = kwargs.pop('assignee_ids', None)
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        if assignee_ids is not None:
            TaskAssignment.query.filter_by(task_id=task.id).delete()
            for uid in assignee_ids:
                assignment = TaskAssignment(task_id=task.id, user_id=uid)
                db.session.add(assignment)
        db.session.commit()
        return task

    def update_assignment_status(self, assignment_id, status, note=None):
        assignment = TaskAssignment.query.get(assignment_id)
        if assignment:
            assignment.status = status
            if note:
                assignment.note = note
            if status in ('done', 'approved'):
                assignment.submitted_at = datetime.utcnow()
            db.session.commit()
        return assignment

    def get_assignment(self, task_id, user_id):
        return TaskAssignment.query.filter_by(task_id=task_id, user_id=user_id).first()

    def get_task_stats(self, user_id=None):
        base_query = Task.query
        if user_id:
            base_query = base_query.outerjoin(TaskAssignment).filter(
                db.or_(
                    Task.created_by == user_id,
                    TaskAssignment.user_id == user_id
                )
            ).distinct()
        
        pending_requests = 0
        if not user_id:
            pending_requests = TaskRequest.query.filter_by(status='pending').count()

        return {
            'total': base_query.count(),
            'todo': base_query.filter(Task.status == 'todo').count(),
            'in_progress': base_query.filter(Task.status == 'in_progress').count(),
            'done': base_query.filter(Task.status == 'done').count(),
            'overdue': base_query.filter(Task.status != 'done', Task.due_date < datetime.utcnow()).count(),
            'pending_requests': pending_requests
        }

    # Task History Methods
    def add_history(self, task_id, user_id, action, details=None):
        history = TaskHistory(
            task_id=task_id,
            user_id=user_id,
            action=action,
            details=details
        )
        db.session.add(history)
        db.session.commit()
        return history

    def get_task_history(self, task_id, page=1, per_page=10):
        return TaskHistory.query.filter_by(task_id=task_id).order_by(TaskHistory.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    # Task Request Methods (Approvals)
    def create_request(self, task_id, requester_id, request_type, target_user_id=None, note=None):
        req = TaskRequest(
            task_id=task_id,
            requester_id=requester_id,
            request_type=request_type,
            target_user_id=target_user_id,
            note=note
        )
        db.session.add(req)
        db.session.commit()
        return req

    def get_pending_requests(self):
        return TaskRequest.query.filter_by(status='pending').order_by(TaskRequest.created_at.desc()).all()

    def update_request_status(self, request_id, status, processed_by, note=None):
        req = TaskRequest.query.get(request_id)
        if req:
            req.status = status
            req.processed_at = datetime.utcnow()
            req.processed_by = processed_by
            if note:
                req.note = note
            db.session.commit()
        return req

    def _update_parent_task_progress(self, task_id):
        task = Task.query.get(task_id)
        if not task: return
        total = task.subtasks.count()
        if total == 0:
            return  # If no subtasks, let manual progress remain or set to 0. Better to not force 0 if they manually typed it.
        done = task.subtasks.filter_by(is_done=True).count()
        task.progress = int((done / total) * 100)
        db.session.commit()

    # Subtasks
    def create_subtask(self, task_id, title):
        st = SubTask(task_id=task_id, title=title)
        db.session.add(st)
        db.session.commit()
        self._update_parent_task_progress(task_id)
        return st

    def update_subtask(self, subtask_id, **kwargs):
        st = SubTask.query.get(subtask_id)
        if st:
            for k, v in kwargs.items():
                if hasattr(st, k):
                    setattr(st, k, v)
            db.session.commit()
            if 'is_done' in kwargs:
                self._update_parent_task_progress(st.task_id)
        return st

    def delete_subtask(self, subtask_id):
        st = SubTask.query.get(subtask_id)
        if st:
            task_id = st.task_id
            db.session.delete(st)
            db.session.commit()
            self._update_parent_task_progress(task_id)
            return True
        return False

    # Comments
    def add_comment(self, task_id, user_id, content, parent_id=None):
        c = TaskComment(task_id=task_id, user_id=user_id, content=content, parent_id=parent_id)
        db.session.add(c)
        db.session.commit()
        return c

    def get_comment(self, comment_id):
        return TaskComment.query.get(comment_id)

    def delete_comment(self, comment_id):
        c = TaskComment.query.get(comment_id)
        if c:
            db.session.delete(c)
            db.session.commit()
            return True
        return False

    # Attachments
    def add_attachment(self, task_id, filename, file_path, file_type=None):
        a = TaskAttachment(task_id=task_id, filename=filename, file_path=file_path, file_type=file_type)
        db.session.add(a)
        db.session.commit()
        return a

    def delete_attachment(self, attachment_id):
        a = TaskAttachment.query.get(attachment_id)
        if a:
            db.session.delete(a)
            db.session.commit()
            return True
        return False

