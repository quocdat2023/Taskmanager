from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models import ScheduleReminder, Schedule
from app.extensions import db
from app.services.email_service import EmailService
from datetime import datetime, timedelta

reminder_bp = Blueprint('reminder', __name__, url_prefix='/api/reminders')

@reminder_bp.route('/admin/all', methods=['GET'])
@jwt_required()
def get_all_reminders():
    # Role check (pseudo-code)
    reminders = ScheduleReminder.query.order_by(ScheduleReminder.target_time.desc()).all()
    
    total = len(reminders)
    pending = len([r for r in reminders if not r.is_sent])
    sent = total - pending
    
    data = []
    for r in reminders:
        d = r.to_dict()
        d['schedule_title'] = r.schedule.title
        d['creator_name'] = r.schedule.creator_user.full_name if r.schedule.creator_user else '—'
        data.append(d)
        
    return jsonify({
        "reminders": data,
        "stats": { "total": total, "pending": pending, "sent": sent }
    })

@reminder_bp.route('/admin/send-pending', methods=['POST'])
@jwt_required()
def send_pending():
    # This would usually be a cron job, but we'll expose it to Admin
    now = datetime.utcnow() + timedelta(hours=7)
    pending = ScheduleReminder.query.filter_by(is_sent=False).filter(ScheduleReminder.target_time <= now).all()
    
    count = 0
    for r in pending:
        success, _ = EmailService.send_schedule_reminder(r)
        if success:
            r.is_sent = True
            r.sent_at = now
            count += 1
            
    db.session.commit()
    return jsonify({"message": f"Đã gửi {count} nhắc hẹn.", "total_processed": len(pending)})

@reminder_bp.route('/schedule/<int:schedule_id>', methods=['GET'])
@jwt_required()
def get_reminders(schedule_id):
    reminders = ScheduleReminder.query.filter_by(schedule_id=schedule_id).all()
    return jsonify({"reminders": [r.to_dict() for r in reminders]})

@reminder_bp.route('/schedule/<int:schedule_id>', methods=['POST'])
@jwt_required()
def set_reminders(schedule_id):
    data = request.get_json()
    offsets = data.get('offsets', []) # list of minutes
    
    schedule = Schedule.query.get_or_404(schedule_id)
    ScheduleReminder.query.filter_by(schedule_id=schedule_id).delete()
    
    for offset in offsets:
        try:
            minutes = int(offset)
            target = schedule.start_time - timedelta(minutes=minutes)
            new_r = ScheduleReminder(
                schedule_id=schedule_id,
                offset_minutes=minutes,
                target_time=target
            )
            db.session.add(new_r)
        except:
            continue
            
    db.session.commit()
    return jsonify({"message": "Cài đặt nhắc hẹn thành công"})
