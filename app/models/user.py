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
    reminder_preference = db.Column(db.String(100), default='5') # Comma-separated minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_tasks = db.relationship('Task', backref='creator', lazy='dynamic', foreign_keys='Task.created_by')
    task_assignments = db.relationship('TaskAssignment', backref='assignee', lazy='dynamic')
    documents = db.relationship('Document', backref='uploader', lazy='dynamic')
    questions = db.relationship('Question', backref='asker', lazy='dynamic', foreign_keys='Question.asked_by')
    answers = db.relationship('Answer', backref='answerer', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

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
            'reminder_preference': self.reminder_preference,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<User {self.username}>'
