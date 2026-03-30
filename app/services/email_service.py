from flask_mail import Message
from app.extensions import mail
from flask import current_app


class EmailService:

    _BRAND_RED = '#e53e3e'

    _PRIORITY = {
        'low':    ('Thấp',       '#15803d', '#f0fdf4', '#bbf7d0', '&#128994;'),
        'medium': ('Trung bình', '#b45309', '#fffbeb', '#fde68a', '&#128993;'),
        'high':   ('Cao',        '#dc2626', '#fef2f2', '#fecaca', '&#128308;'),
        'urgent': ('Khẩn cấp',  '#c2410c', '#fff7ed', '#fed7aa', '&#128293;'),
    }

    @staticmethod
    def _priority(key):
        return EmailService._PRIORITY.get(
            key, ('Bình thường', '#6b7280', '#f9fafb', '#e5e7eb', '&#9898;')
        )

    # ── Shared blocks (table-based, email-safe) ───────────────────────────

    @staticmethod
    def _header_block(subtitle, title, date_str):
        return f"""
    <tr>
      <td class="rp-pad-hdr" style="padding:28px 36px 20px;border-bottom:1px solid #f1f3f5;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="padding-bottom:18px;">
              <table cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="width:32px;height:32px;background:#e53e3e;border-radius:8px;
                             text-align:center;vertical-align:middle;">
                    <span style="color:#ffffff;font-size:16px;font-weight:700;line-height:32px;">E</span>
                  </td>
                  <td style="padding-left:10px;vertical-align:middle;">
                    <span style="color:#e53e3e;font-size:16px;font-weight:700;">EduTask</span>
                    <span style="color:#d1d5db;padding:0 6px;">&middot;</span>
                    <span style="color:#6b7280;font-size:12px;font-weight:500;">{subtitle}</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td>
              <p style="color:#111827;font-size:18px;font-weight:700;margin:0 0 4px;line-height:1.3;">{title}</p>
              <p style="color:#9ca3af;font-size:12px;margin:0;">{date_str}</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>"""

    @staticmethod
    def _info_cards(left_icon, left_label, left_val, right_icon, right_label, right_val):
        return f"""
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:16px;">
          <tr>
            <td class="rp-card-cell rp-card-left" width="50%" style="padding-right:8px;vertical-align:top;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="border:1px solid #f1f3f5;border-radius:8px;background:#fafafa;">
                <tr><td style="padding:14px 16px;">
                  <p style="color:#9ca3af;font-size:10px;font-weight:600;letter-spacing:.08em;
                             text-transform:uppercase;margin:0 0 5px;">{left_icon} {left_label}</p>
                  <p style="color:#111827;font-size:14px;font-weight:600;margin:0;">{left_val}</p>
                </td></tr>
              </table>
            </td>
            <td class="rp-card-cell rp-card-right" width="50%" style="padding-left:8px;vertical-align:top;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="border:1px solid #f1f3f5;border-radius:8px;background:#fafafa;">
                <tr><td style="padding:14px 16px;">
                  <p style="color:#9ca3af;font-size:10px;font-weight:600;letter-spacing:.08em;
                             text-transform:uppercase;margin:0 0 5px;">{right_icon} {right_label}</p>
                  <p style="color:#111827;font-size:14px;font-weight:600;margin:0;">{right_val}</p>
                </td></tr>
              </table>
            </td>
          </tr>
        </table>"""

    @staticmethod
    def _description_block(text):
        return f"""
        <table width="100%" cellpadding="0" cellspacing="0" border="0"
               style="border:1px solid #f1f3f5;border-radius:8px;background:#fafafa;margin-bottom:16px;">
          <tr><td style="padding:14px 16px;">
            <p style="color:#9ca3af;font-size:10px;font-weight:600;letter-spacing:.08em;
                       text-transform:uppercase;margin:0 0 8px;">&#128203; Mô tả công việc</p>
            <p style="color:#4b5563;font-size:13px;margin:0;line-height:1.7;">{text}</p>
          </td></tr>
        </table>"""

    @staticmethod
    def _cta_block(label):
        return f"""
        <table cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="background:#e53e3e;border-radius:8px;">
              <a href="#" style="display:inline-block;padding:11px 24px;color:#ffffff;
                                 text-decoration:none;font-size:14px;font-weight:600;">
                {label} &rarr;
              </a>
            </td>
          </tr>
        </table>"""

    @staticmethod
    def _footer_block():
        return """
    <tr>
      <td class="rp-pad-ban" style="border-top:1px solid #f1f3f5;padding:14px 36px;background:#fafafa;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td><span style="color:#9ca3af;font-size:11px;">EduTask &copy; 2025</span></td>
            <td style="text-align:right;">
              <span style="color:#d1d5db;font-size:11px;">Vui lòng không trả lời email này</span>
            </td>
          </tr>
        </table>
      </td>
    </tr>"""

    @staticmethod
    def _wrap(inner_rows):
        return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <style>
    /* ── Responsive overrides for mobile clients (Gmail iOS/Android) ── */
    @media only screen and (max-width: 600px) {{

      /* Make outer wrapper full-width, remove rounded corners */
      .rp-outer {{
        width: 100% !important;
        border-radius: 0 !important;
      }}

      /* Tighten horizontal padding on main sections */
      .rp-pad-hdr {{
        padding: 20px 20px 16px !important;
      }}
      .rp-pad-body {{
        padding: 20px 20px !important;
      }}
      .rp-pad-ban {{
        padding: 12px 20px !important;
      }}
      .rp-pad-task-band {{
        padding: 14px 20px !important;
      }}

      /* Stack the 2-column info cards vertically */
      .rp-card-cell {{
        display: block !important;
        width: 100% !important;
        box-sizing: border-box !important;
      }}
      .rp-card-left {{
        padding-right: 0 !important;
        padding-bottom: 8px !important;
      }}
      .rp-card-right {{
        padding-left: 0 !important;
      }}
    }}
  </style>
</head>
<body style="margin:0;padding:16px 0;background:#f4f6f8;
             font-family:'Segoe UI',Helvetica,Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding:0 12px;">
      <table class="rp-outer" width="580" cellpadding="0" cellspacing="0" border="0"
             style="background:#ffffff;border-radius:12px;overflow:hidden;
                    box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:580px;width:100%;">
        <!-- Top accent bar -->
        <tr>
          <td height="3" style="background:#e53e3e;font-size:0;line-height:0;">&nbsp;</td>
        </tr>
        {inner_rows}
      </table>
    </td>
  </tr>
</table>

</body>
</html>"""

    # ════════════════════════════════════════════════════════════════════════
    #  1. TASK ASSIGNMENT NOTIFICATION
    # ════════════════════════════════════════════════════════════════════════
    @staticmethod
    def send_task_assignment_notification(task, specific_user_ids=None):
        creator     = task.creator
        assignments = task.assignments.all()

        recipients = []
        if creator and creator.email:
            if specific_user_ids is None or creator.id in specific_user_ids:
                recipients.append(creator.email)

        participants = []
        for a in assignments:
            if a.assignee:
                participants.append(a.assignee.full_name)
                if a.assignee.email:
                    if specific_user_ids is None or a.user_id in specific_user_ids:
                        recipients.append(a.assignee.email)

        if not recipients:
            return False, "Không có người nhận email"
        recipients = list(set(recipients))

        p_label, p_color, p_bg, p_border, p_icon = EmailService._priority(task.priority)
        creator_name = creator.full_name if creator else 'Hệ thống'
        due_str      = (task.due_date.strftime('%H:%M &middot; %d/%m/%Y')
                        if task.due_date else 'Không có thời hạn')
        description  = task.description or 'Không có mô tả chi tiết.'
        updated      = (task.updated_at.strftime('%A, %d/%m/%Y &middot; %H:%M')
                        if hasattr(task, 'updated_at') and task.updated_at else '')

        badge_palette = [
            ('#fff1f2', '#be123c', '#fecdd3'),
            ('#f0f9ff', '#0369a1', '#bae6fd'),
            ('#f5f3ff', '#6d28d9', '#ddd6fe'),
            ('#fdf4ff', '#86198f', '#f0abfc'),
            ('#f0fdf4', '#166534', '#bbf7d0'),
        ]
        if participants:
            badges = ''.join(
                f'<span style="background:{bg};color:{fg};border:1px solid {bd};'
                f'border-radius:20px;padding:4px 12px;font-size:12px;font-weight:500;'
                f'display:inline-block;margin:2px 4px 2px 0;">{name}</span>'
                for i, name in enumerate(participants)
                for bg, fg, bd in [badge_palette[i % len(badge_palette)]]
            )
        else:
            badges = '<span style="color:#9ca3af;font-size:13px;">Chỉ mình bạn</span>'

        inner = f"""
    {EmailService._header_block('Quản lý nhiệm vụ', 'Bạn có công việc mới được giao', updated)}

    <!-- Task title band -->
    <tr>
      <td class="rp-pad-task-band" style="padding:16px 36px;border-bottom:1px solid #f1f3f5;background:#fafafa;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="vertical-align:top;">
              <p style="color:#9ca3af;font-size:10px;font-weight:600;letter-spacing:.08em;
                         text-transform:uppercase;margin:0 0 5px;">Công việc #{task.id}</p>
              <p style="color:#111827;font-size:15px;font-weight:700;margin:0;line-height:1.4;">{task.title}</p>
            </td>
            <td style="vertical-align:top;text-align:right;padding-left:12px;white-space:nowrap;">
              <span style="background:{p_bg};color:{p_color};border:1px solid {p_border};
                           border-radius:20px;padding:4px 12px;font-size:12px;
                           font-weight:600;display:inline-block;">{p_icon} {p_label}</span>
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <tr>
      <td class="rp-pad-body" style="padding:24px 36px;">
        <p style="color:#4b5563;font-size:14px;margin:0 0 22px;line-height:1.7;">
          Xin chào,<br>
          Bạn vừa được giao hoặc cập nhật một công việc trong hệ thống
          <strong style="color:#111827;">EduTask</strong>.
          Vui lòng xem thông tin bên dưới và thực hiện đúng thời hạn.
        </p>

        {EmailService._info_cards('&#128100;', 'Người giao', creator_name,
                                   '&#128197;', 'Thời hạn', due_str)}

        {EmailService._description_block(description)}

        <table width="100%" cellpadding="0" cellspacing="0" border="0"
               style="border:1px solid #f1f3f5;border-radius:8px;background:#fafafa;margin-bottom:24px;">
          <tr><td style="padding:14px 16px;">
            <p style="color:#9ca3af;font-size:10px;font-weight:600;letter-spacing:.08em;
                       text-transform:uppercase;margin:0 0 10px;">&#128101; Thành viên tham gia</p>
            <div>{badges}</div>
          </td></tr>
        </table>

        {EmailService._cta_block('Xem chi tiết công việc')}
      </td>
    </tr>

    {EmailService._footer_block()}"""

        html_body = EmailService._wrap(inner)
        text_body = (
            f"Chào bạn,\n\nBạn vừa được giao công việc mới:\n\n"
            f"Công việc  : {task.title} (#{task.id})\n"
            f"Người giao : {creator_name}\n"
            f"Ưu tiên    : {p_label}\n"
            f"Thời hạn   : {task.due_date.strftime('%H:%M %d/%m/%Y') if task.due_date else 'Không có'}\n"
            f"Mô tả      : {description}\n"
            f"Tham gia   : {', '.join(participants) if participants else 'Chỉ mình bạn'}\n\n"
            f"Trân trọng,\nBan quản lý nhiệm vụ EduTask."
        )

        msg = Message(
            subject=f"[Công việc #{task.id}] {task.title}",
            recipients=recipients,
            body=text_body,
            html=html_body,
        )
        try:
            with current_app.app_context():
                mail.send(msg)
            return True, "Email công việc đã gửi thành công"
        except Exception as e:
            return False, str(e)

    # ════════════════════════════════════════════════════════════════════════
    #  2. SCHEDULE REMINDER
    # ════════════════════════════════════════════════════════════════════════
    @staticmethod
    def send_schedule_reminder(reminder):
        schedule = reminder.schedule
        user     = schedule.creator_user

        if not user or not user.email:
            return False, "Không có email người dùng"

        start_str = (schedule.start_time.strftime('%H:%M &middot; %d/%m/%Y')
                     if schedule.start_time else 'Chưa xác định')
        end_str   = (schedule.end_time.strftime('%H:%M')
                     if hasattr(schedule, 'end_time') and schedule.end_time else None)
        time_range = (f"{schedule.start_time.strftime('%H:%M')} &ndash; {end_str}"
                      if end_str else schedule.start_time.strftime('%H:%M'))
        date_str   = schedule.start_time.strftime('%A, %d/%m/%Y') if schedule.start_time else ''
        location   = schedule.location or 'Trực tuyến'
        is_online  = not schedule.location or not schedule.location.strip()
        loc_icon   = '&#127760;' if is_online else '&#128205;'
        minutes_before = getattr(reminder, 'minutes_before', 30)

        if is_online:
            tip = ('Đây là sự kiện <strong>trực tuyến</strong>. '
                   'Hãy kiểm tra kết nối mạng, thiết bị âm thanh và tài liệu trước 10 phút.')
        else:
            tip = (f'Hãy di chuyển đến <strong>{location}</strong> sớm để chuẩn bị. '
                   'Kiểm tra tài liệu trước ít nhất 10 phút.')

        inner = f"""
    {EmailService._header_block('Lịch học &amp; Sự kiện', 'Nhắc nhở lịch học sắp diễn ra', date_str)}

    <!-- Countdown banner -->
    <tr>
      <td class="rp-pad-ban" style="padding:14px 36px;border-bottom:1px solid #f1f3f5;background:#fff5f5;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="vertical-align:middle;">
              <table cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="font-size:20px;vertical-align:middle;padding-right:10px;">&#9200;</td>
                  <td style="vertical-align:middle;">
                    <p style="color:#c53030;font-size:13px;font-weight:700;margin:0 0 2px;">
                      Sự kiện bắt đầu sau {minutes_before} phút nữa
                    </p>
                    <p style="color:#9ca3af;font-size:11px;margin:0;">{date_str} &middot; {time_range}</p>
                  </td>
                </tr>
              </table>
            </td>
            <td style="text-align:right;vertical-align:middle;white-space:nowrap;padding-left:12px;">
              <span style="background:#e53e3e;color:#ffffff;border-radius:20px;
                           padding:5px 14px;font-size:12px;font-weight:700;display:inline-block;">
                {minutes_before} phút
              </span>
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <tr>
      <td class="rp-pad-body" style="padding:24px 36px;">
        <p style="color:#4b5563;font-size:14px;margin:0 0 22px;line-height:1.7;">
          Xin chào <strong style="color:#111827;">{user.full_name}</strong>,<br>
          Đây là nhắc nhở cho sự kiện sắp diễn ra trong lịch học của bạn.
        </p>

        <!-- Event info table -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0"
               style="border:1px solid #f1f3f5;border-radius:8px;overflow:hidden;margin-bottom:16px;">
          <tr>
            <td colspan="2" style="background:#fafafa;border-bottom:1px solid #f1f3f5;padding:10px 16px;">
              <span style="color:#9ca3af;font-size:10px;font-weight:600;letter-spacing:.08em;
                           text-transform:uppercase;">Thông tin sự kiện</span>
            </td>
          </tr>
          <tr>
            <td width="30%" style="padding:11px 16px;background:#fafafa;
                                   border-right:1px solid #f1f3f5;border-bottom:1px solid #f1f3f5;">
              <span style="color:#6b7280;font-size:12px;font-weight:500;">Sự kiện</span>
            </td>
            <td style="padding:11px 16px;border-bottom:1px solid #f1f3f5;">
              <span style="color:#111827;font-size:13px;font-weight:600;">{schedule.title}</span>
            </td>
          </tr>
          <tr>
            <td style="padding:11px 16px;background:#fafafa;
                       border-right:1px solid #f1f3f5;border-bottom:1px solid #f1f3f5;">
              <span style="color:#6b7280;font-size:12px;font-weight:500;">Thời gian</span>
            </td>
            <td style="padding:11px 16px;border-bottom:1px solid #f1f3f5;">
              <span style="color:#111827;font-size:13px;font-weight:600;">{time_range} &middot; {date_str}</span>
            </td>
          </tr>
          <tr>
            <td style="padding:11px 16px;background:#fafafa;border-right:1px solid #f1f3f5;">
              <span style="color:#6b7280;font-size:12px;font-weight:500;">Địa điểm</span>
            </td>
            <td style="padding:11px 16px;">
              <span style="color:#111827;font-size:13px;font-weight:600;">{loc_icon} {location}</span>
            </td>
          </tr>
        </table>

        <!-- Tip box -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0"
               style="border:1px solid #fde68a;border-radius:8px;background:#fffbeb;margin-bottom:24px;">
          <tr><td style="padding:14px 16px;">
            <table cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="font-size:18px;vertical-align:top;padding-right:12px;padding-top:2px;">&#128161;</td>
                <td style="vertical-align:top;">
                  <p style="color:#92400e;font-size:12px;font-weight:700;margin:0 0 4px;">Gợi ý chuẩn bị</p>
                  <p style="color:#78350f;font-size:13px;margin:0;line-height:1.6;">{tip}</p>
                </td>
              </tr>
            </table>
          </td></tr>
        </table>

        {EmailService._cta_block('Xem lịch của tôi')}
      </td>
    </tr>

    {EmailService._footer_block()}"""

        html_body = EmailService._wrap(inner)
        text_body = (
            f"Chào {user.full_name},\n\n"
            f"Sự kiện '{schedule.title}' sẽ bắt đầu sau {minutes_before} phút.\n\n"
            f"Thời gian : {schedule.start_time.strftime('%H:%M %d/%m/%Y') if schedule.start_time else ''}\n"
            f"Địa điểm  : {location}\n\n"
            f"Trân trọng,\nHệ thống quản lý lịch học EduTask."
        )

        msg = Message(
            subject=f"[Nhắc hẹn #{reminder.id}] {schedule.title}",
            recipients=[user.email],
            body=text_body,
            html=html_body,
        )
        try:
            with current_app.app_context():
                mail.send(msg)
            return True, "Email đã gửi thành công"
        except Exception as e:
            return False, str(e)

    # ════════════════════════════════════════════════════════════════════════
    #  3. NEW MEMBER NOTIFICATION
    # ════════════════════════════════════════════════════════════════════════
    @staticmethod
    def send_new_member_notification(task, user):
        """Sends notification to ONLY one new member."""
        if not user or not user.email:
            return False, "Người dùng không có email"

        p_label, p_color, p_bg, p_border, p_icon = EmailService._priority(task.priority)
        creator_name = task.creator.full_name if task.creator else 'Hệ thống'
        due_str      = (task.due_date.strftime('%H:%M &middot; %d/%m/%Y')
                        if task.due_date else 'Không có thời hạn')
        description  = task.description or 'Không có mô tả chi tiết.'

        inner = f"""
    {EmailService._header_block('Quản lý nhiệm vụ', 'Bạn đã được thêm vào công việc', '')}

    <!-- Approved banner -->
    <tr>
      <td class="rp-pad-ban" style="padding:14px 36px;border-bottom:1px solid #f1f3f5;background:#f0fdf4;">
        <table cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="font-size:18px;vertical-align:middle;padding-right:10px;">&#9989;</td>
            <td style="vertical-align:middle;">
              <span style="color:#166534;font-size:13px;font-weight:600;">
                Yêu cầu tham gia của bạn đã được phê duyệt thành công
              </span>
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <tr>
      <td class="rp-pad-body" style="padding:24px 36px;">
        <p style="color:#4b5563;font-size:14px;margin:0 0 22px;line-height:1.7;">
          Xin chào <strong style="color:#111827;">{user.full_name}</strong>,<br>
          Bạn chính thức là thành viên của công việc bên dưới. Truy cập hệ thống để bắt đầu ngay!
        </p>

        <!-- Task highlight -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0"
               style="border-left:3px solid #e53e3e;background:#fafafa;
                      border-radius:0 8px 8px 0;margin-bottom:16px;">
          <tr><td style="padding:14px 16px;">
            <p style="color:#9ca3af;font-size:10px;font-weight:600;letter-spacing:.08em;
                       text-transform:uppercase;margin:0 0 4px;">Công việc #{task.id}</p>
            <p style="color:#111827;font-size:15px;font-weight:700;margin:0;line-height:1.4;">{task.title}</p>
          </td></tr>
        </table>

        {EmailService._info_cards('&#128100;', 'Người giao', creator_name,
                                   '&#128197;', 'Thời hạn', due_str)}

        <!-- Priority row -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0"
               style="border:1px solid #f1f3f5;border-radius:8px;background:#fafafa;margin-bottom:16px;">
          <tr><td style="padding:14px 16px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td>
                  <span style="color:#9ca3af;font-size:10px;font-weight:600;
                               letter-spacing:.08em;text-transform:uppercase;">Độ ưu tiên</span>
                </td>
                <td style="text-align:right;">
                  <span style="background:{p_bg};color:{p_color};border:1px solid {p_border};
                               border-radius:20px;padding:4px 12px;font-size:12px;
                               font-weight:600;display:inline-block;">{p_icon} {p_label}</span>
                </td>
              </tr>
            </table>
          </td></tr>
        </table>

        {EmailService._description_block(description)}

        {EmailService._cta_block('Vào tham gia công việc')}
      </td>
    </tr>

    {EmailService._footer_block()}"""

        html_body = EmailService._wrap(inner)
        text_body = (
            f"Chào {user.full_name},\n\n"
            f"Yêu cầu tham gia của bạn đã được phê duyệt.\n\n"
            f"Công việc : {task.title} (#{task.id})\n"
            f"Người giao: {creator_name}\n"
            f"Ưu tiên   : {p_label}\n"
            f"Thời hạn  : {task.due_date.strftime('%H:%M %d/%m/%Y') if task.due_date else 'Không có'}\n"
            f"Mô tả     : {description}\n\n"
            f"Trân trọng,\nBan quản lý nhiệm vụ EduTask."
        )

        msg = Message(
            subject=f"[Công việc mới #{task.id}] {task.title}",
            recipients=[user.email],
            body=text_body,
            html=html_body,
        )
        try:
            with current_app.app_context():
                mail.send(msg)
            return True, "Email thông báo thành viên mới đã gửi thành công"
        except Exception as e:
            return False, str(e)