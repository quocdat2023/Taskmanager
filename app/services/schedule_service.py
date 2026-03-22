from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from datetime import datetime


class ScheduleService:
    def __init__(self):
        self.repo = ScheduleRepository()
        self.notification_repo = NotificationRepository()
        self.user_repo = UserRepository()

    def create_schedule(self, title, start_time, end_time, created_by, **kwargs):
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00')).replace(tzinfo=None)
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00')).replace(tzinfo=None)

        schedule = self.repo.create_schedule(
            title=title,
            start_time=start_time,
            end_time=end_time,
            created_by=created_by,
            **kwargs
        )

        # Notify all students about new schedule
        students = self.user_repo.get_students()
        for student in students:
            self.notification_repo.create_notification(
                user_id=student.id,
                title='Lịch học mới',
                message=f'Lịch học mới: {title}',
                notification_type='schedule',
                reference_type='schedule',
                reference_id=schedule.id
            )

        return schedule

    def get_schedule(self, schedule_id):
        return self.repo.get_by_id(schedule_id)

    def get_all_schedules(self):
        return self.repo.get_all()

    def get_schedules_by_creator(self, user_id):
        return self.repo.get_by_creator(user_id)

    def get_schedules_by_range(self, start_date, end_date, user_id=None):
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).replace(tzinfo=None)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).replace(tzinfo=None)
        return self.repo.get_by_date_range(start_date, end_date, user_id)

    def get_upcoming(self, limit=10):
        return self.repo.get_upcoming(limit)

    def update_schedule(self, schedule_id, **kwargs):
        for field in ['start_time', 'end_time']:
            if field in kwargs and isinstance(kwargs[field], str):
                kwargs[field] = datetime.fromisoformat(kwargs[field].replace('Z', '+00:00')).replace(tzinfo=None)
        
        schedule = self.repo.update(schedule_id, **kwargs)
        if schedule:
            # Notify all students about schedule update
            students = self.user_repo.get_students()
            student_ids = [s.id for s in students]
            if student_ids:
                self.notification_repo.create_bulk(
                    user_ids=student_ids,
                    title='Lịch học thay đổi',
                    message=f'Lịch học "{schedule.title}" đã được cập nhật.',
                    notification_type='schedule',
                    reference_type='schedule',
                    reference_id=schedule.id
                )
        return schedule

    def delete_schedule(self, schedule_id):
        return self.repo.delete(schedule_id)
