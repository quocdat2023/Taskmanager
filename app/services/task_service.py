from app.repositories.task_repository import TaskRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.models.task import TaskAssignment
from app.extensions import db, socketio
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

        # Broadcast to all Kanban board viewers
        socketio.emit('task_list_updated', {'action': 'create', 'task_id': task.id})
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
        user_role = kwargs.pop('user_role', 'student')
        
        task = self.repo.update_task(task_id, **kwargs)
        
        if task:
            self.repo.add_history(task_id, changed_by, 'update', 'Cập nhật thông tin công việc.')
            
            approval_summary = {
                'requires_admin_approval': False,
                'requested_assign_user_ids': [],
                'requested_remove_user_ids': [],
                'already_pending_assign_user_ids': [],
                'already_pending_remove_user_ids': []
            }

            # Handle assignees logic
            if assignee_ids is not None:
                assignee_ids = [int(i) for i in assignee_ids]
                existing_assignee_ids = [a.user_id for a in task.assignments]
                
                if user_role == 'admin':
                    # Admin: do it directly (add or remove)
                    for uid in existing_assignee_ids:
                        if uid not in assignee_ids:
                            TaskAssignment.query.filter_by(task_id=task.id, user_id=uid).delete()
                            req = self.repo.create_request(task_id, changed_by, 'remove', target_user_id=uid)
                            self.repo.update_request_status(req.id, 'approved', changed_by, 'Admin cập nhật thành viên trực tiếp.')
                    
                    newly_assigned_ids = []
                    for uid in assignee_ids:
                        if uid not in existing_assignee_ids:
                            assignment = TaskAssignment(task_id=task.id, user_id=uid)
                            db.session.add(assignment)
                            
                            # Notify NEW user
                            self.notification_repo.create_notification(
                                user_id=uid,
                                title='Công việc mới',
                                message=f'Bạn đã được thêm vào công việc: {task.title}',
                                notification_type='task',
                                reference_type='task',
                                reference_id=task.id
                            )
                            # Keep track of newly assigned users for email
                            newly_assigned_ids.append(uid)
                    
                    db.session.commit()
                    self.repo.add_history(task_id, changed_by, 'assigned', 'Admin cập nhật thành viên trực tiếp.')
                    
                    if newly_assigned_ids:
                        try:
                            from app.services.email_service import EmailService
                            EmailService.send_task_assignment_notification(task, specific_user_ids=newly_assigned_ids)
                        except Exception as e:
                            print("Lỗi gửi mail update_task:", str(e))
                else:
                    # Non-admin: additions and removals need approval
                    
                    # 1. Handle additions
                    for uid in assignee_ids:
                        if uid not in existing_assignee_ids:
                            pending_request = self.repo.get_pending_request(
                                task_id,
                                'assign',
                                target_user_id=uid,
                                requester_id=changed_by
                            )
                            if pending_request:
                                approval_summary['already_pending_assign_user_ids'].append(uid)
                            else:
                                self.repo.create_request(task_id, changed_by, 'assign', target_user_id=uid)
                                self.repo.add_history(task_id, changed_by, 'request_sent', f'Yêu cầu thêm thành viên {uid} vào công việc.')
                                approval_summary['requested_assign_user_ids'].append(uid)
                    
                    # 2. Handle removals
                    for uid in existing_assignee_ids:
                        if uid not in assignee_ids:
                            pending_request = self.repo.get_pending_request(
                                task_id,
                                'remove',
                                target_user_id=uid,
                                requester_id=changed_by
                            )
                            if pending_request:
                                approval_summary['already_pending_remove_user_ids'].append(uid)
                            else:
                                self.repo.create_request(task_id, changed_by, 'remove', target_user_id=uid)
                                self.repo.add_history(task_id, changed_by, 'request_sent', f'Yêu cầu xóa thành viên {uid} khỏi công việc.')
                                approval_summary['requested_remove_user_ids'].append(uid)

                    approval_summary['requires_admin_approval'] = any(approval_summary[key] for key in (
                        'requested_assign_user_ids',
                        'requested_remove_user_ids',
                        'already_pending_assign_user_ids',
                        'already_pending_remove_user_ids'
                    ))

                    # Notify admins
                    admins = self.user_repo.get_by_role('admin')
                    if admins and (
                        approval_summary['requested_assign_user_ids'] or
                        approval_summary['requested_remove_user_ids']
                    ):
                        admin_ids = [a.id for a in admins]
                        self.notification_repo.create_bulk(
                            user_ids=admin_ids,
                            title='Yêu cầu thay đổi thành viên',
                            message=f'Có yêu cầu thêm/xóa người trong task "{task.title}".',
                            notification_type='task_request',
                            reference_type='request'
                        )

            task.approval_summary = approval_summary

            # Notify assignees
            for assignment in task.assignments:
                if assignment.user_id != changed_by:
                    self.notification_repo.create_notification(
                        user_id=assignment.user_id,
                        title='Công việc được cập nhật',
                        message=f'Công việc "{task.title}" đã có thay đổi mới.',
                        notification_type='task',
                        reference_type='task',
                        reference_id=task.id
                    )
            # Broadcast to all Kanban board viewers
            socketio.emit('task_list_updated', {'action': 'update', 'task_id': task_id})
        return task

    def update_task_status(self, task_id, status, user_id):
        task = self.repo.update_task_status(task_id, status)
        if task:
            if status == 'done':
                status_add = 'Hoàn thành'
            elif status == 'in_progress':
                status_add = 'Đang làm'
            elif status == 'todo':
                status_add = 'Chưa bắt đầu'
            self.repo.add_history(task_id, user_id, 'status_change', f'Cập nhật trạng thái công việc thành {status_add}')
            # Look up the user who made the change
            changer = self.user_repo.get_by_id(user_id)
            changer_name = changer.full_name if changer else f'User {user_id}'
            status_labels = {'todo': 'Chưa bắt đầu', 'in_progress': 'Đang làm', 'done': 'Hoàn thành'}
            status_label = status_labels.get(status, status)

            # Sync all participants' personal status with global task status
            for assignment in task.assignments:
                self.repo.update_assignment_status(assignment.id, status)

            # Realtime update for board/detail - Broadcast to all for synchronization
            socketio.emit('task_updated', {'task_id': task_id, 'action': 'status_change'})
            socketio.emit('task_list_updated', {
                'task_id': task_id,
                'action': 'status_change',
                'changer_name': changer_name,
                'changer_id': user_id,
                'task_title': task.title,
                'new_status': status_label,
                'assignee_ids': [a.user_id for a in task.assignments],
                'creator_id': task.created_by
            })

            # Notify assignees
            for assignment in task.assignments:
                if assignment.user_id != user_id:
                    self.notification_repo.create_notification(
                        user_id=assignment.user_id,
                        title='Trạng thái công việc thay đổi',
                        message=f'Công việc "{task.title}" chuyển sang trạng thái: {status_add}',
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
                self.repo.add_history(task_id, user_id, 'progress_change', f'Cập nhật trạng thái cá nhân thành {status}')
                # Notify task creator
                if task.created_by != user_id:
                    self.notification_repo.create_notification(
                        user_id=task.created_by,
                        title='Tiến độ công việc mới',
                        message=f'{updated.assignee.full_name} đã cập nhật "{task.title}" thành {status}',
                        notification_type='task',
                        reference_type='task',
                        reference_id=task.id
                    )
                # Realtime update
                # Notify everyone to facilitate realtime sync
            socketio.emit('task_updated', {'task_id': task_id, 'action': 'assignment_change', 'user_id': user_id})
            socketio.emit('task_list_updated', {'action': 'assignment_change', 'task_id': task_id})
            return updated
        return None

    def request_task_deletion(self, task_id, requester_id):
        task = self.repo.get_by_id(task_id)
        if not task: return None
        req = self.repo.create_request(task_id, requester_id, 'delete')
        self.repo.add_history(task_id, requester_id, 'request_sent', 'Yêu cầu xóa công việc.')

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
        if user_id:
            self.repo.add_history(task_id, user_id, 'delete', 'Xóa công việc bởi admin.')
        result = self.repo.delete(task_id)
        # Broadcast to all Kanban board viewers
        socketio.emit('task_list_updated', {'action': 'delete', 'task_id': task_id})
        return result

    def get_task_history(self, task_id, page=1, per_page=10):
        paginated = self.repo.get_task_history(task_id, page=page, per_page=per_page)
        return {
            'history': [h.to_dict() for h in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': paginated.page,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }

    def get_pending_requests(self, page=1, per_page=20):
        paginated = self.repo.get_pending_requests(page=page, per_page=per_page)
        return {
            'requests': [r.to_dict() for r in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': paginated.page,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }

    def get_processed_requests(self, page=1, per_page=20):
        paginated = self.repo.get_processed_requests(page=page, per_page=per_page)
        return {
            'requests': [r.to_dict() for r in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': paginated.page,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }

    def process_request(self, request_id, status, admin_id, admin_note=None):
        req = self.repo.update_request_status(request_id, status, admin_id, admin_note)
        if not req: return None
        
        task = req.task
        if status == 'approved':
            if req.request_type == 'assign':
                assignment = TaskAssignment(task_id=req.task_id, user_id=req.target_user_id)
                db.session.add(assignment)
                db.session.commit()
                self.repo.add_history(req.task_id, admin_id, 'approved', f'Đã phê duyệt giao công việc cho user {req.target_user_id}')
                self.notification_repo.create_notification(
                    user_id=req.target_user_id,
                    title='Công việc mới được phê duyệt',
                    message=f'Bạn đã được giao công việc: {task.title}',
                    notification_type='task',
                    reference_type='task',
                    reference_id=task.id
                )
            elif req.request_type == 'delete':
                self.delete_task(req.task_id, admin_id)
                return True
            elif req.request_type == 'withdraw':
                TaskAssignment.query.filter_by(task_id=req.task_id, user_id=req.target_user_id).delete()
                db.session.commit()
                self.repo.add_history(req.task_id, admin_id, 'approved', f'Đã phê duyệt rút khỏi công việc cho user {req.target_user_id}')
            elif req.request_type == 'remove':
                TaskAssignment.query.filter_by(task_id=req.task_id, user_id=req.target_user_id).delete()
                db.session.commit()
                self.repo.add_history(req.task_id, admin_id, 'approved', f'Đã phê duyệt xóa thành viên {req.target_user_id} khỏi công việc')
                self.notification_repo.create_notification(
                    user_id=req.target_user_id,
                    title='Bạn đã bị xóa khỏi công việc',
                    message=f'Admin đã phê duyệt yêu cầu xóa bạn khỏi công việc: {task.title}',
                    notification_type='info'
                )
        
        elif status == 'rejected':
            self.repo.add_history(req.task_id, admin_id, 'rejected', f'Admin đã từ chối yêu cầu. Ghi chú: {admin_note or "Không có"}')

        self.notification_repo.create_notification(
            user_id=req.requester_id,
            title='Yêu cầu đã được xử lý',
            message=f'Yêu cầu "{req.request_type}" của bạn cho task "{task.title}" đã được {status}.',
            notification_type='info'
        )
        # Broadcast to all Kanban board viewers
        socketio.emit('task_list_updated', {'action': 'request_processed', 'task_id': req.task_id})
        return req

    def get_task_stats(self, user_id=None):
        return self.repo.get_task_stats(user_id)

    def get_overdue_tasks(self):
        return self.repo.get_overdue_tasks()

    # Subtasks
    def add_subtask(self, task_id, user_id, title):
        st = self.repo.create_subtask(task_id, title)
        self.repo.add_history(task_id, user_id, 'update', f'Đã thêm nhiệm vụ con: {title}')
        socketio.emit('task_updated', {'task_id': task_id, 'action': 'subtask_add'}, room=f"task_{task_id}")
        return st

    def update_subtask(self, task_id, user_id, subtask_id, **kwargs):
        st = self.repo.update_subtask(subtask_id, **kwargs)
        self.repo.add_history(task_id, user_id, 'update', f'Đã cập nhật nhiệm vụ con ID {subtask_id}')
        socketio.emit('task_updated', {'task_id': task_id, 'action': 'subtask_update'}, room=f"task_{task_id}")
        return st

    def delete_subtask(self, task_id, user_id, subtask_id):
        info = self.repo.delete_subtask(subtask_id)
        if info:
            self.repo.add_history(task_id, user_id, 'update', f'Đã xóa nhiệm vụ con ID {subtask_id}')
            socketio.emit('task_updated', {'task_id': task_id, 'action': 'subtask_delete'}, room=f"task_{task_id}")
        return info

    # Comments
    def add_comment(self, task_id, user_id, content, parent_id=None):
        c = self.repo.add_comment(task_id, user_id, content, parent_id)
        # Notify assignees and creator
        task = self.repo.get_by_id(task_id)
        receivers = {a.user_id for a in task.assignments}
        receivers.add(task.created_by)
        
        # If it's a reply, also notify the parent comment's author
        if parent_id:
            parent_comment = self.repo.get_comment(parent_id)
            if parent_comment:
                receivers.add(parent_comment.user_id)

        receivers.remove(user_id) if user_id in receivers else None
        
        for rid in receivers:
            self.notification_repo.create_notification(
                user_id=rid,
                title='Bình luận mới',
                message=f'Có thảo luận mới trong task "{task.title}"',
                notification_type='task',
                reference_type='task',
                reference_id=task.id
            )
        socketio.emit('task_updated', {'task_id': task_id, 'action': 'comment_add'}, room=f"task_{task_id}")
        return c

    def delete_comment(self, comment_id, user_id, role='student'):
        comment = self.repo.get_comment(comment_id)
        if not comment: return False
        
        # Check permission: own comment or admin
        if role != 'admin' and comment.user_id != user_id:
            return False
        
        task_id = comment.task_id
        res = self.repo.delete_comment(comment_id)
        if res:
            socketio.emit('task_updated', {'task_id': task_id, 'action': 'comment_delete'}, room=f"task_{task_id}")
        return res

    # Attachments
    def add_attachment(self, task_id, user_id, filename, file_path, file_type=None):
        a = self.repo.add_attachment(task_id, filename, file_path, file_type)
        self.repo.add_history(task_id, user_id, 'update', f'Đã đính kèm tài liệu: {filename}')
        return a

    def delete_attachment(self, task_id, user_id, attachment_id):
        info = self.repo.delete_attachment(attachment_id)
        if info:
            self.repo.add_history(task_id, user_id, 'update', f'Đã xóa tài liệu đính kèm ID {attachment_id}')
        return info
