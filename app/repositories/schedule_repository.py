from app.repositories.base_repository import BaseRepository
from app.models.schedule import Schedule
from app.extensions import db
from datetime import datetime


class ScheduleRepository(BaseRepository):
    def __init__(self):
        super().__init__(Schedule)

    def get_by_creator(self, user_id):
        return Schedule.query.filter_by(created_by=user_id).order_by(Schedule.start_time.asc()).all()

    def get_by_date_range(self, start_date, end_date, user_id=None):
        query = Schedule.query.filter(
            Schedule.start_time < end_date,
            Schedule.end_time > start_date
        )
        if user_id:
            query = query.filter_by(created_by=user_id)
        return query.order_by(Schedule.start_time.asc()).all()

    def get_upcoming(self, limit=10):
        return Schedule.query.filter(
            Schedule.start_time >= datetime.utcnow()
        ).order_by(Schedule.start_time.asc()).limit(limit).all()

    def get_by_course(self, course_code):
        return Schedule.query.filter_by(course_code=course_code).order_by(Schedule.start_time.asc()).all()

    def create_schedule(self, title, start_time, end_time, created_by, **kwargs):
        schedule = Schedule(
            title=title,
            start_time=start_time,
            end_time=end_time,
            created_by=created_by,
            **kwargs
        )
        db.session.add(schedule)
        db.session.commit()
        return schedule
