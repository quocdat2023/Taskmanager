from app.extensions import db
from datetime import datetime


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_name = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)  # bytes
    file_type = db.Column(db.String(50), nullable=True)
    course_name = db.Column(db.String(150), nullable=True)
    course_code = db.Column(db.String(20), nullable=True)
    class_group = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(50), default='general')  # lecture, assignment, reference, general
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'course_name': self.course_name,
            'course_code': self.course_code,
            'class_group': self.class_group,
            'category': self.category,
            'uploaded_by': self.uploaded_by,
            'uploader_name': self.uploader.full_name if self.uploader else None,
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }

    def __repr__(self):
        return f'<Document {self.title}>'
