import threading
import time
from datetime import datetime, timedelta

def start_reminder_worker(app):
    def run():
        # Wait a bit for the server to fully start
        time.sleep(10)
        
        while True:
            try:
                with app.app_context():
                    from app.models import ScheduleReminder
                    from app.services.email_service import EmailService
                    from app.extensions import db
                    
                    now = datetime.utcnow() + timedelta(hours=7)
                    # Use a slightly larger window to be safe or just <=
                    pending = ScheduleReminder.query.filter_by(is_sent=False).filter(ScheduleReminder.target_time <= now).all()
                    
                    if pending:
                        print(f"[Worker] Found {len(pending)} pending reminders due at {now.strftime('%H:%M:%S')}")
                        
                    for r in pending:
                        success, error = EmailService.send_schedule_reminder(r)
                        if success:
                            r.is_sent = True
                            r.sent_at = now
                            print(f"[Worker] Successfully sent reminder ID {r.id}")
                        else:
                            print(f"[Worker] Failed to send reminder ID {r.id}: {error}")
                    
                    db.session.commit()

                    # Weekly/Daily Cleanup (at 3 AM or similar)
                    # For simplicity, let's just do it every hour but check if it's 3:xx
                    if now.hour == 3 and now.minute == 0:
                        from app.repositories.chat_repository import ChatRepository
                        chat_repo = ChatRepository()
                        deleted_count = chat_repo.cleanup_old_messages(days=14)
                        if deleted_count > 0:
                            print(f"[Worker] Cleaned up {deleted_count} messages older than 14 days.")

            except Exception as e:
                print(f"[Worker Error] {str(e)}")
            
            # Sleep for 60 seconds before next check
            time.sleep(60)
    
    # We use a daemon thread so it dies when the main process dies
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    print("[Worker] Background reminder worker started.")
