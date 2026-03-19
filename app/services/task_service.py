from app.repositories.task_repository import TaskRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.models.task import TaskAssignment
from datetime import datetime


class TaskService:
    def __init__(self):
        self.repo = TaskRepository()
        self.notification_repo = NotificationRepository()
        self.user_repo = UserRepository()

    def create_task(self, title, description, created_by, assignee_ids=None, user_role='student', **kwargs):
        # Parse due_date string if provided
        due_date = kwargs.get('due_date')
        if due_date and isinstance(due_date, str):
            try:
                kwargs['due_date'] = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                kwargs['due_date'] = None

        if user_role == 'admin':
            # Admin can create directly with assignees
            task = self.repo.create_task(
                title=title,
                description=description,
                created_by=created_by,
                assignee_ids=assignee_ids,
                **kwargs
            )
            # Add history
            self.repo.add_history(task.id, created_by, 'create', f'Admin đã tạo công việc với {len(assignee_ids) if assignee_ids else 0} người thực hiện.')
            
            # Send notifications to assignees
            if assignee_ids:
                for uid in assignee_ids:
                    self.notification_repo.create_notification(
                        user_id=uid,
                        title='Công việc mới',
                        message=f'Bạn được giao công việc: {title}',
                        notification_type='task',
                        reference_type='task',
                        reference_id=task.id
                    )
            
            # Notify all students about the record creation
            students = self.user_repo.get_students()
            student_ids = [s.id for s in students]
            if student_ids:
                self.notification_repo.create_bulk(
                    user_ids=student_ids,
                    title='Công việc hệ thống mới',
                    message=f'Công việc "{title}" vừa được thêm vào hệ thống.',
                    notification_type='task',
                    reference_type='task',
                    reference_id=task.id
                )
        else:
            # Teachers/Students must request for each assignee
            # Create task with NO assignees first
            task = self.repo.create_task(
                title=title,
                description=description,
                created_by=created_by,
                assignee_ids=None,
                **kwargs
            )
            # Add history
            self.repo.add_history(task.id, created_by, 'create', 'Người dùng tạo công việc. Yêu cầu giao việc đang chờ phê duyệt.')
            
            # Create requests for each assignee
            if assignee_ids:
                for uid in assignee_ids:
                    self.repo.create_request(task.id, created_by, 'assign', target_user_id=uid)
                    self.repo.add_history(task.id, created_by, 'request_sent', f'Yêu cầu giao công việc cho user {uid}')
                
                # Notify all admins about new requests
                admins = self.user_repo.get_by_role('admin')
                if admins:
                    admin_ids = [a.id for a in admins]
                    self.notification_repo.create_bulk(
                        user_ids=admin_ids,
                        title='Yêu cầu phê duyệt giao việc',
                        message=f'{created_by} muốn giao việc cho {len(assignee_ids)} người.',
                        notification_type='task_request',
                        reference_type='request'
                    )

        return task

    def get_task(self, task_id):
        return self.repo.get_by_id(task_id)

    def get_tasks_for_user(self, user_id, role, semester=None, academic_year=None, status=None, search=None, page=1, per_page=20):
        if role == 'admin':
            return self.repo.get_all_tasks(semester, academic_year, status=status, search=search, page=page, per_page=per_page)
        elif role == 'teacher':
            return self.repo.get_tasks_by_creator_or_assignee(user_id, semester, academic_year, status=status, search=search, page=page, per_page=per_page)
        else:
            return self.repo.get_tasks_by_assignee(user_id, semester, academic_year, status=status, search=search, page=page, per_page=per_page)

    def get_all_tasks(self, page=1, per_page=20):
        return self.repo.get_paginated(page=page, per_page=per_page)

    def update_task(self, task_id, changed_by, **kwargs):
        due_date = kwargs.get('due_date')
        if due_date and isinstance(due_date, str):
            try:
                kwargs['due_date'] = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                kwargs['due_date'] = None
        
        assignee_ids = kwargs.pop('assignee_ids', None)
        task = self.repo.update_task(task_id, **kwargs)
        
        if task:
            self.repo.add_history(task_id, changed_by, 'update', 'Cập nhật thông tin công việc.')
            
            # Handle assignees logic
            if assignee_ids is not None:
                existing_assignee_ids = [a.user_id for a in task.assignments]
                user_role = kwargs.get('user_role', 'student')
                
                if user_role == 'admin':
                    # Admin: do it directly (add or remove)
                    for uid in existing_assignee_ids:
                        if uid not in assignee_ids:
                            TaskAssignment.query.filter_by(task_id=task.id, user_id=uid).delete()
                    
                    for uid in assignee_ids:
                        if uid not in existing_assignee_ids:
                            assignment = TaskAssignment(task_id=task.id, user_id=uid)
                            from app.extensions import db
                            db.session.add(assignment)
                            
                            # Notify NEW user (Bell + Email)
                            self.notification_repo.create_notification(
                                user_id=uid,
                                title='Công việc mới',
                                message=f'Bạn đã được thêm vào công việc: {task.title}',
                                notification_type='task',
                                reference_type='task',
                                reference_id=task.id
                            )
                            from app.services.email_service import EmailService
                            from app.repositories.user_repository import UserRepository
                            user = UserRepository().get_by_id(uid)
                            if user:
                                EmailService.send_new_member_notification(task, user)
                    
                    from app.extensions import db
                    db.session.commit()
                    self.repo.add_history(task_id, changed_by, 'assigned', 'Admin cập nhật thành viên trực tiếp.')
                else:
                    # Non-admin: additions need approval
                    for uid in assignee_ids:
                        if uid not in existing_assignee_ids:
                            self.repo.create_request(task_id, changed_by, 'assign', target_user_id=uid)
                            self.repo.add_history(task_id, changed_by, 'request_sent', f'Yêu cầu thêm thành viên {uid} vào công việc.')
                    
                    # Notify all admins about new requests
                    admins = self.user_repo.get_by_role('admin')
                    if admins:
                        admin_ids = [a.id for a in admins]
                        self.notification_repo.create_bulk(
                            user_ids=admin_ids,
                            title='Yêu cầu thêm thành viên mới',
                            message=f'Có yêu cầu thêm người vào task "{task.title}".',
                            notification_type='task_request',
                            reference_type='request'
                        )

            # Notify all current assignees about task update
            for assignment in task.assignments:
                self.notification_repo.create_notification(
                    user_id=assignment.user_id,
                    title='Công việc được cập nhật',
                    message=f'Công việc "{task.title}" đã có thay đổi mới.',
                    notification_type='task',
                    reference_type='task',
                    reference_id=task.id
                )

            # Notify all students about task update
            students = self.user_repo.get_students()
            student_ids = [s.id for s in students]
            if student_ids:
                self.notification_repo.create_bulk(
                    user_ids=student_ids,
                    title='Cập nhật công việc',
                    message=f'Công việc "{task.title}" vừa có cập nhật mới.',
                    notification_type='task',
                    reference_type='task',
                    reference_id=task.id
                )
        return task

    def update_task_status(self, task_id, status, user_id):
        # This handles the OVERALL task status (usually by admin or creator)
        task = self.repo.update_task_status(task_id, status)
        if task:
            self.repo.add_history(task_id, user_id, 'status_change', f'Cập nhật trạng thái công việc thành {status}')
            # Notify all assignees about overall status change
            for assignment in task.assignments:
                self.notification_repo.create_notification(
                    user_id=assignment.user_id,
                    title='Trạng thái công việc thay đổi',
                    message=f'Công việc "{task.title}" chuyển sang trạng thái: {status}',
                    notification_type='task',
                    reference_type='task',
                    reference_id=task.id
                )

            # Notify all students about status change
            students = self.user_repo.get_students()
            student_ids = [s.id for s in students]
            if student_ids:
                self.notification_repo.create_bulk(
                    user_ids=student_ids,
                    title='Trạng thái công việc thay đổi',
                    message=f'Công việc "{task.title}" vừa được chuyển sang: {status}',
                    notification_type='task',
                    reference_type='task',
                    reference_id=task.id
                )
        return task

    def update_assignment_status(self, task_id, user_id, status, note=None):
        assignment = self.repo.get_assignment(task_id, user_id)
        if assignment:
            updated = self.repo.update_assignment_status(assignment.id, status, note)
            if updated:
                task = updated.task
                self.repo.add_history(task_id, user_id, 'progress_change', f'Cập nhật trạng thái thành {status}')
                # Notify task creator about assignment status update
                self.notification_repo.create_notification(
                    user_id=task.created_by,
                    title='Tiến độ công việc mới',
                    message=f'{updated.assignee.full_name} đã cập nhật "{task.title}" thành {status}',
                    notification_type='task',
                    reference_type='task',
                    reference_id=task.id
                )
            return updated
        return None

    def request_task_deletion(self, task_id, requester_id):
        task = self.repo.get_by_id(task_id)
        if not task: return None
        req = self.repo.create_request(task_id, requester_id, 'delete')
        self.repo.add_history(task_id, requester_id, 'request_sent', 'Yêu cầu xóa công việc.')

        # Notify admins
        admins = self.user_repo.get_by_role('admin')
        if admins:
            self.notification_repo.create_bulk(
                user_ids=[a.id for a in admins],
                title='Yêu cầu xóa công việc',
                message=f'Có yêu cầu xóa công việc "{task.title}".',
                notification_type='task_request',
                reference_type='request'
            )
        return req

    def request_task_withdrawal(self, task_id, requester_id):
        task = self.repo.get_by_id(task_id)
        if not task: return None
        req = self.repo.create_request(task_id, requester_id, 'withdraw', target_user_id=requester_id)
        self.repo.add_history(task_id, requester_id, 'request_sent', 'Yêu cầu rút khỏi công việc.')

        # Notify admins
        admins = self.user_repo.get_by_role('admin')
        if admins:
            self.notification_repo.create_bulk(
                user_ids=[a.id for a in admins],
                title='Yêu cầu rút khỏi công việc',
                message=f'Người dùng yêu cầu rút khỏi task "{task.title}".',
                notification_type='task_request',
                reference_type='request'
            )
        return req

    def delete_task(self, task_id, user_id=None):
        # Admin direct delete
        if user_id:
            self.repo.add_history(task_id, user_id, 'delete', 'Xóa công việc bởi admin.')
        return self.repo.delete(task_id)

    def get_task_history(self, task_id):
        return [h.to_dict() for h in self.repo.get_task_history(task_id)]

    def get_pending_requests(self):
        return [r.to_dict() for r in self.repo.get_pending_requests()]

    def process_request(self, request_id, status, admin_id, admin_note=None):
        req = self.repo.update_request_status(request_id, status, admin_id, admin_note)
        if not req: return None
        
        task = req.task
        
        if status == 'approved':
            if req.request_type == 'assign':
                # Add assignment
                assignment = TaskAssignment(task_id=req.task_id, user_id=req.target_user_id)
                from app.extensions import db
                db.session.add(assignment)
                db.session.commit()
                self.repo.add_history(req.task_id, admin_id, 'approved', f'Đã phê duyệt giao công việc cho user {req.target_user_id}')
                
                # Notify user
                self.notification_repo.create_notification(
                    user_id=req.target_user_id,
                    title='Công việc mới được phê duyệt',
                    message=f'Bạn đã được giao công việc: {task.title}',
                    notification_type='task',
                    reference_type='task',
                    reference_id=task.id
                )
                
                # Send email ONLY to the new member
                from app.services.email_service import EmailService
                from app.repositories.user_repository import UserRepository
                user = UserRepository().get_by_id(req.target_user_id)
                if user:
                    EmailService.send_new_member_notification(task, user)
            elif req.request_type == 'delete':
                # Delete task
                self.delete_task(req.task_id, admin_id)
                return True
            elif req.request_type == 'withdraw':
                # Remove assignment
                TaskAssignment.query.filter_by(task_id=req.task_id, user_id=req.target_user_id).delete()
                from app.extensions import db
                db.session.commit()
                self.repo.add_history(req.task_id, admin_id, 'approved', f'Đã phê duyệt rút khỏi công việc cho user {req.target_user_id}')
        
        elif status == 'rejected':
            self.repo.add_history(req.task_id, admin_id, 'rejected', f'Admin đã từ chối yêu cầu. Ghi chú: {admin_note or "Không có"}')

        # Notify requester
        self.notification_repo.create_notification(
            user_id=req.requester_id,
            title='Yêu cầu đã được xử lý',
            message=f'Yêu cầu "{req.request_type}" của bạn cho task "{task.title}" đã được {status}.',
            notification_type='info'
        )
            
        return req

    def get_task_stats(self, user_id=None):
        return self.repo.get_task_stats(user_id)

    def get_overdue_tasks(self):
        return self.repo.get_overdue_tasks()
