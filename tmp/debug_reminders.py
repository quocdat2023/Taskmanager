from app import create_app
from app.models import ScheduleReminder
from datetime import datetime

app = create_app()
with app.app_context():
    now = datetime.utcnow()
    reminders = ScheduleReminder.query.all()
    print(f"Current time (UTC): {now}")
    print(f"Total reminders: {len(reminders)}")
    for r in reminders:
        print(f"ID {r.id}: Target {r.target_time}, Sent: {r.is_sent}, Offset: {r.offset_minutes}m")
