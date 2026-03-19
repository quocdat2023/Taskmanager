from app.extensions import db
from datetime import datetime


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='todo')  # todo, in_progress, done
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high, urgent
    due_date = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_name = db.Column(db.String(150), nullable=True)  # Tên môn học
    course_code = db.Column(db.String(20), nullable=True)  # Mã môn
    class_group = db.Column(db.String(50), nullable=True)  # Nhóm lớp
    semester = db.Column(db.String(20), nullable=True)  # Học kỳ (VD: HK1, HK2, HK3)
    academic_year = db.Column(db.String(20), nullable=True)  # Năm học (VD: 2023-2024)
    attachment = db.Column(db.String(256), nullable=True)  # File đính kèm
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assignments = db.relationship('TaskAssignment', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    history = db.relationship('TaskHistory', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    requests = db.relationship('TaskRequest', backref='task', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_by': self.created_by,
            'creator_name': self.creator.full_name if self.creator else None,
            'course_name': self.course_name,
            'course_code': self.course_code,
            'class_group': self.class_group,
            'semester': self.semester,
            'academic_year': self.academic_year,
            'attachment': self.attachment,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
            'assignees': [a.to_dict() for a in self.assignments],
        }

    def __repr__(self):
        return f'<Task {self.title}>'


class TaskAssignment(db.Model):
    __tablename__ = 'task_assignments'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='todo')  # todo, in_progress, done
    note = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'user_name': self.assignee.full_name if self.assignee else None,
            'status': self.status,
            'note': self.note,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
        }


class TaskHistory(db.Model):
    __tablename__ = 'task_history'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # 'create', 'update', 'status_change', 'assigned', 'request_sent', etc.
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else 'Unknown',
            'action': self.action,
            'details': self.details,
            'created_at': self.created_at.isoformat() + 'Z',
        }


class TaskRequest(db.Model):
    __tablename__ = 'task_requests'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    request_type = db.Column(db.String(20), nullable=False)  # 'assign', 'delete', 'withdraw'
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # For 'assign'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    requester = db.relationship('User', foreign_keys=[requester_id])
    target_user = db.relationship('User', foreign_keys=[target_user_id])
    processor = db.relationship('User', foreign_keys=[processed_by])

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'task_title': self.task.title if self.task else 'N/A',
            'requester_id': self.requester_id,
            'requester_name': self.requester.full_name if self.requester else 'Unknown',
            'request_type': self.request_type,
            'target_user_id': self.target_user_id,
            'target_user_name': self.target_user.full_name if self.target_user else None,
            'status': self.status,
            'note': self.note,
            'created_at': self.created_at.isoformat() + 'Z',
            'processed_at': self.processed_at.isoformat() + 'Z' if self.processed_at else None,
        }
