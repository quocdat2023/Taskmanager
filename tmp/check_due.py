from app import create_app
from app.models import ScheduleReminder
from datetime import datetime

app = create_app()
with app.app_context():
    now = datetime.now()
    all_rem = ScheduleReminder.query.all()
    print(f"Server Local Time: {now}")
    print(f"Total count in DB: {len(all_rem)}")
    for r in all_rem:
        is_due = r.target_time <= now
        print(f"ID {r.id}: Target {r.target_time}, Sent: {r.is_sent}, Due: {is_due}")
