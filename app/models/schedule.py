from app.extensions import db
from datetime import datetime


class Schedule(db.Model):
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_type = db.Column(db.String(50), nullable=False, default='class')  # class, exam, meeting, event
    course_name = db.Column(db.String(150), nullable=True)
    course_code = db.Column(db.String(20), nullable=True)
    class_group = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(200), nullable=True)  # Phòng học
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_rule = db.Column(db.String(100), nullable=True)  # weekly, biweekly
    color = db.Column(db.String(7), default='#4A90D9')  # Calendar color
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship defined by backref in User model (user_creator)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type,
            'course_name': self.course_name,
            'course_code': self.course_code,
            'class_group': self.class_group,
            'location': self.location,
            'start': self.start_time.isoformat() + 'Z' if self.start_time else None,
            'end': self.end_time.isoformat() + 'Z' if self.end_time else None,
            'start_time': self.start_time.isoformat() + 'Z' if self.start_time else None,
            'end_time': self.end_time.isoformat() + 'Z' if self.end_time else None,
            'is_recurring': self.is_recurring,
            'recurrence_rule': self.recurrence_rule,
            'color': self.color,
            'backgroundColor': self.color,
            'created_by': self.created_by,
            'creator_name': self.user_creator.full_name if self.user_creator else None,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }

    def __repr__(self):
        return f'<Schedule {self.title}>'
