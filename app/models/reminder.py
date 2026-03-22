from app.extensions import db
from datetime import datetime, timedelta

class ScheduleReminder(db.Model):
    __tablename__ = 'schedule_reminders'

    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    
    # Milestone in minutes before start_time (e.g., 60 for 1 hour before)
    offset_minutes = db.Column(db.Integer, nullable=False)
    
    # Calculated time at which this reminder SHOULD be sent
    # (schedule.start_time - timedelta(minutes=offset_minutes))
    target_time = db.Column(db.DateTime, nullable=False)
    
    reminder_type = db.Column(db.String(50), default='email') # email, push?
    
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, nullable=True)
    
    # Configuration
    snooze_enabled = db.Column(db.Boolean, default=True)
    snooze_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    schedule = db.relationship('Schedule', backref=db.backref('reminders', cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'offset_minutes': self.offset_minutes,
            'target_time': self.target_time.isoformat() if self.target_time else None,
            'reminder_type': self.reminder_type,
            'is_sent': self.is_sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'snooze_count': self.snooze_count,
        }

    def __repr__(self):
        return f'<ScheduleReminder {self.id} for Schedule {self.schedule_id}>'
