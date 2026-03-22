from app.extensions import db
from datetime import datetime


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='todo')  # todo, in_progress, done, approved
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high, urgent
    due_date = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_name = db.Column(db.String(150), nullable=True)
    course_code = db.Column(db.String(20), nullable=True)
    class_group = db.Column(db.String(50), nullable=True)
    semester = db.Column(db.String(20), nullable=True)
    academic_year = db.Column(db.String(20), nullable=True)
    attachment = db.Column(db.String(256), nullable=True)
    progress = db.Column(db.Integer, default=0)
    estimated_time = db.Column(db.String(50), nullable=True)
    actual_time = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assignments = db.relationship('TaskAssignment', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    history = db.relationship('TaskHistory', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    requests = db.relationship('TaskRequest', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    subtasks = db.relationship('SubTask', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('TaskComment', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    task_attachments = db.relationship('TaskAttachment', backref='task', lazy='dynamic', cascade='all, delete-orphan')

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
            'progress': self.progress,
            'estimated_time': self.estimated_time,
            'actual_time': self.actual_time,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
            'assignees': [a.to_dict() for a in self.assignments],
            'subtasks': [s.to_dict() for s in self.subtasks],
            'comments': [c.to_dict() for c in self.comments],
            'attachments': [a.to_dict() for a in self.task_attachments],
        }

    def __repr__(self):
        return f'<Task {self.title}>'


class TaskAssignment(db.Model):
    __tablename__ = 'task_assignments'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='todo')  # todo, in_progress, done, approved
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


class SubTask(db.Model):
    __tablename__ = 'sub_tasks'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    progress = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'title': self.title,
            'is_done': self.is_done,
            'progress': self.progress
        }


class TaskComment(db.Model):
    __tablename__ = 'task_comments'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('task_comments.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id])
    replies = db.relationship('TaskComment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'user_name': self.author.full_name if self.author else 'Unknown',
            'content': self.content,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() + 'Z'
        }


class TaskAttachment(db.Model):
    __tablename__ = 'task_attachments'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(50), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'uploaded_at': self.uploaded_at.isoformat() + 'Z'
        }


class TaskHistory(db.Model):
    __tablename__ = 'task_history'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship defined by backref 'performer' in User model

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'user_name': self.performer.full_name if self.performer else 'Unknown',
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
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='pending')
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships defined by backrefs in User model (sender, target, admin_proc)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'task_title': self.task.title if self.task else 'N/A',
            'requester_id': self.requester_id,
            'requester_name': self.sender.full_name if self.sender else 'Unknown',
            'request_type': self.request_type,
            'target_user_id': self.target_user_id,
            'target_user_name': self.target.full_name if self.target else None,
            'status': self.status,
            'note': self.note,
            'created_at': self.created_at.isoformat() + 'Z',
            'processed_at': self.processed_at.isoformat() + 'Z' if self.processed_at else None,
        }

