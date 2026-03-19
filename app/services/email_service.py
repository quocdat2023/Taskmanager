from flask_mail import Message
from app.extensions import mail
from flask import current_app

class EmailService:
    @staticmethod
    def send_schedule_reminder(reminder):
        schedule = reminder.schedule
        user = schedule.creator_user
        
        if not user or not user.email:
            return False, "Không có email người dùng"

        # Content based on context (from user request)
        content_header = f"Chào {user.full_name},\n\nĐây là tin nhắn nhắc nhở cho sự kiện sắp tới của bạn:\n"
        event_info = f"- Sự kiện: {schedule.title}\n- Thời gian: {schedule.start_time.strftime('%H:%M %d/%m/%Y')}\n- Địa điểm: {schedule.location or 'Trực tuyến'}\n"
        
        # Action suggestions (from user request)
        action_hint = f"\n💡 Gợi ý: Hãy chuẩn bị sớm — kiểm tra địa điểm hoặc thiết bị và tài liệu trước 10 phút."
        # action_hint = ""
        # if schedule.location and ("Phòng" in schedule.location or "P." in schedule.location):
        #     action_hint = f"\n💡 Gợi ý: Hãy di chuyển đến {schedule.location} sớm để chuẩn bị."
        # else:
        #     action_hint = f"\n💡 Gợi ý: Đây là sự kiện trực tuyến, hãy chuẩn bị thiết bị và tài liệu trước 10 phút."

        body = content_header + event_info + action_hint + "\n\nTrân trọng,\n Hệ thống quản lý lịch học."

        msg = Message(
            subject=f"[Nhắc hẹn #{reminder.id}] {schedule.title}",
            recipients=[user.email],
            body=body
        )

        try:
            with current_app.app_context():
                mail.send(msg)
            return True, "Email đã gửi thành công"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def send_task_assignment_notification(task):
        creator = task.creator
        assignments = task.assignments.all()
        
        # Collect recipient emails and names
        recipients = []
        if creator and creator.email:
            recipients.append(creator.email)
            
        participants = []
        for a in assignments:
            if a.assignee:
                participants.append(a.assignee.full_name)
                if a.assignee.email:
                    recipients.append(a.assignee.email)
        
        if not recipients:
            return False, "Không có người nhận email"
            
        # Avoid duplicate emails
        recipients = list(set(recipients))
        priority_dict = {
            'low': 'Thấp',
            'medium': 'Trung bình',
            'high': 'Cao',
            'urgent': 'Khẩn cấp'
        }

        body = f"Chào bạn,\n\nThông báo về việc giao/cập nhật công việc mới:\n\n"
        body += f"📌 Công việc: {task.title}\n"
        body += f"👤 Người giao: {creator.full_name if creator else 'Hệ thống'}\n"
        body += f"✅ Độ ưu tiên: {priority_dict.get(task.priority, 'Không có mô tả chi tiết')}\n"
        body += f"📝 Nội dung: {task.description or 'Không có mô tả chi tiết'}\n"
        body += f"📅 Thời hạn: {task.due_date.strftime('%H:%M %d/%m/%Y') if task.due_date else 'Không có'}\n"
        body += f"👥 Thành viên tham gia: {', '.join(participants) if participants else 'Chỉ mình bạn'}\n\n"
        body += "Vui lòng truy cập hệ thống để biết thêm chi tiết.\n\nTrân trọng,\nBan quản lý nhiệm vụ EduTask."

        msg = Message(
            subject=f"[Công việc #{task.id}] {task.title}",
            recipients=recipients,
            body=body
        )

        try:
            with current_app.app_context():
                mail.send(msg)
            return True, "Email công việc đã gửi thành công"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def send_new_member_notification(task, user):
        """Sends notification to ONLY one new member."""
        if not user or not user.email:
            return False, "Người dùng không có email"
            
        priority_dict = {
            'low': 'Thấp',
            'medium': 'Trung bình',
            'high': 'Cao',
            'urgent': 'Khẩn cấp'
        }

        body = f"Chào {user.full_name},\n\nBạn đã được thêm vào công việc mới sau khi được phê duyệt:\n\n"
        body += f"📌 Công việc: {task.title}\n"
        body += f"👤 Người giao: {task.creator.full_name if task.creator else 'Hệ thống'}\n"
        body += f"✅ Độ ưu tiên: {priority_dict.get(task.priority, 'Bình thường')}\n"
        body += f"📅 Thời hạn: {task.due_date.strftime('%H:%M %d/%m/%Y') if task.due_date else 'Không có'}\n"
        body += f"📝 Nội dung: {task.description or 'Không có'}\n\n"
        body += "Vui lòng truy cập hệ thống để tham gia công việc.\n\nTrân trọng,\nBan quản lý nhiệm vụ EduTask."

        msg = Message(
            subject=f"[Công việc mới #{task.id}] {task.title}",
            recipients=[user.email],
            body=body
        )

        try:
            with current_app.app_context():
                mail.send(msg)
            return True, "Email thông báo thành viên mới đã gửi thành công"
        except Exception as e:
            return False, str(e)
