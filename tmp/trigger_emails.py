from app import create_app
from app.models import ScheduleReminder
from app.services.email_service import EmailService
from app.extensions import db
from datetime import datetime

app = create_app()
with app.app_context():
    now = datetime.now()
    # Find all due unsent reminders
    pending = ScheduleReminder.query.filter_by(is_sent=False).filter(ScheduleReminder.target_time <= now).all()
    print(f"Bắt đầu xử lý {len(pending)} nhắc hẹn...")
    
    for r in pending:
        print(f"Đang gửi ID {r.id} cho {r.schedule.creator_user.email}...")
        success, msg = EmailService.send_schedule_reminder(r)
        if success:
            r.is_sent = True
            r.sent_at = now
            print(f" -> THÀNH CÔNG.")
        else:
            print(f" -> THẤT BẠI: {msg}")
            
    db.session.commit()
    print("Hoàn tất.")
