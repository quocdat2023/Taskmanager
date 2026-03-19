from app.extensions import db
from datetime import datetime


class AcademicYear(db.Model):
    __tablename__ = 'academic_years'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)  # VD: 2024-2025
    start_year = db.Column(db.Integer, nullable=False)             # VD: 2024
    end_year = db.Column(db.Integer, nullable=False)               # VD: 2025
    is_active = db.Column(db.Boolean, default=False)               # Năm học hiện tại
    description = db.Column(db.String(200), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'start_year': self.start_year,
            'end_year': self.end_year,
            'is_active': self.is_active,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }

    def __repr__(self):
        return f'<AcademicYear {self.name}>'
