from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, teacher, student
    avatar = db.Column(db.String(256), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    student_id = db.Column(db.String(20), nullable=True)  # Mã sinh viên
    department = db.Column(db.String(100), nullable=True)  # Khoa
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    reminder_preference = db.Column(db.String(100), default='5') # Comma-separated minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_tasks = db.relationship('Task', backref='creator', lazy='dynamic', foreign_keys='Task.created_by', cascade='all, delete-orphan')
    task_assignments = db.relationship('TaskAssignment', backref='assignee', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='uploader', lazy='dynamic', cascade='all, delete-orphan')
    questions = db.relationship('Question', backref='asker', lazy='dynamic', foreign_keys='Question.asked_by', cascade='all, delete-orphan')
    answers = db.relationship('Answer', backref='answerer', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('TaskComment', backref='author', lazy='dynamic', foreign_keys='TaskComment.user_id', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    histories = db.relationship('TaskHistory', backref='performer', lazy='dynamic', foreign_keys='TaskHistory.user_id', cascade='all, delete-orphan')
    requests_sent = db.relationship('TaskRequest', backref='sender', lazy='dynamic', foreign_keys='TaskRequest.requester_id', cascade='all, delete-orphan')
    requests_received = db.relationship('TaskRequest', backref='target', lazy='dynamic', foreign_keys='TaskRequest.target_user_id', cascade='all, delete-orphan')
    requests_processed = db.relationship('TaskRequest', backref='admin_proc', lazy='dynamic', foreign_keys='TaskRequest.processed_by', cascade='all, delete-orphan')
    sent_messages = db.relationship('ChatMessage', backref='user_sender', lazy='dynamic', foreign_keys='ChatMessage.sender_id', cascade='all, delete-orphan')
    received_messages = db.relationship('ChatMessage', backref='user_receiver', lazy='dynamic', foreign_keys='ChatMessage.receiver_id', cascade='all, delete-orphan')
    created_schedules = db.relationship('Schedule', backref='user_creator', lazy='dynamic', foreign_keys='Schedule.created_by', cascade='all, delete-orphan')
    created_academic_years = db.relationship('AcademicYear', backref='academic_creator', lazy='dynamic', foreign_keys='AcademicYear.created_by', cascade='save-update, merge')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'avatar': self.avatar,
            'phone': self.phone,
            'student_id': self.student_id,
            'department': self.department,
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'reminder_preference': self.reminder_preference,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<User {self.username}>'
