from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.task_service import TaskService
from app.services.email_service import EmailService
from app.utils.decorators import role_required
import os
from werkzeug.utils import secure_filename
from datetime import datetime

task_bp = Blueprint('tasks', __name__, url_prefix='/api')
task_service = TaskService()


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar', 'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@task_bp.route('/tasks', methods=['POST'])
@jwt_required()
@role_required('admin', 'teacher')
def create_task():
    data = request.get_json()
    if not data.get('title'):
        return jsonify({'error': 'Tiêu đề là bắt buộc'}), 400

    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'student')

    assignee_ids = data.pop('assignee_ids', [])

    task = task_service.create_task(
        title=data['title'],
        description=data.get('description', ''),
        created_by=user_id,
        assignee_ids=assignee_ids,
        user_role=role,
        priority=data.get('priority', 'medium'),
        due_date=data.get('due_date'),
        course_name=data.get('course_name'),
        course_code=data.get('course_code'),
        class_group=data.get('class_group'),
        semester=data.get('semester'),
        academic_year=data.get('academic_year'),
        progress=data.get('progress', 0),
        estimated_time=data.get('estimated_time'),
        actual_time=data.get('actual_time'),
    )

    email_sent = False
    email_error = None
    if task and role == 'admin':
        try:
            success, msg = EmailService.send_task_assignment_notification(task)
            email_sent = success
            if not success:
                email_error = msg
        except Exception as e:
            email_error = str(e)

    return jsonify({
        'message': 'Task đã được tạo',
        'task': task.to_dict(),
        'email_sent': email_sent,
        'email_error': email_error
    }), 201


@task_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'student')

    semester      = request.args.get('semester')
    academic_year = request.args.get('academic_year')
    status        = request.args.get('status')
    search        = request.args.get('search')
    page          = request.args.get('page', 1, type=int)
    per_page      = request.args.get('per_page', 12, type=int)

    paginated = task_service.get_tasks_for_user(
        user_id, role, semester, academic_year,
        status=status, search=search,
        page=page, per_page=per_page
    )

    return jsonify({
        'tasks': [t.to_dict() for t in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
        'per_page': paginated.per_page,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev
    }), 200


@task_bp.route('/tasks/all', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_all_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    paginated = task_service.get_all_tasks(page=page, per_page=per_page)

    return jsonify({
        'tasks': [t.to_dict() for t in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
        'per_page': paginated.per_page,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev
    }), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    task = task_service.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task không tồn tại'}), 404
    return jsonify({'task': task.to_dict()}), 200


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    data = request.get_json()
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'student')

    data['user_role'] = role
    task = task_service.update_task(task_id, changed_by=user_id, **data)
    if not task:
        return jsonify({'error': 'Task không tồn tại'}), 404

    approval_summary = getattr(task, 'approval_summary', None) or {}
    approval_pending = bool(approval_summary.get('requires_admin_approval'))

    message = 'Task đã được cập nhật'
    if approval_pending and role != 'admin':
        if approval_summary.get('requested_remove_user_ids') or approval_summary.get('already_pending_remove_user_ids'):
            message = 'Yêu cầu xóa thành viên đã được gửi, vui lòng chờ Admin phê duyệt.'
        else:
            message = 'Yêu cầu thay đổi thành viên đã được gửi, vui lòng chờ Admin phê duyệt.'

    return jsonify({
        'message': message,
        'task': task.to_dict(),
        'approval_pending': approval_pending,
        'approval_summary': approval_summary
    }), 200


@task_bp.route('/tasks/<int:task_id>/history', methods=['GET'])
@jwt_required()
def get_task_history(task_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    result = task_service.get_task_history(task_id, page=page, per_page=per_page)
    return jsonify(result), 200


@task_bp.route('/tasks/<int:task_id>/status', methods=['PUT'])
@jwt_required()
def update_task_status(task_id):
    data = request.get_json()
    status = data.get('status')
    if status not in ('todo', 'in_progress', 'done'):
        return jsonify({'error': 'Trạng thái không hợp lệ'}), 400

    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'student')

    # Admin can always update task status
    if role == 'admin':
        task = task_service.update_task_status(task_id, status, user_id)
        if not task:
            return jsonify({'error': 'Task không tồn tại'}), 404
        return jsonify({'message': 'Trạng thái đã được cập nhật', 'task': task.to_dict()}), 200

    # Non-admin: check if user is assigned to this task
    task = task_service.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task không tồn tại'}), 404

    assigned_user_ids = [a.user_id for a in task.assignments]
    if user_id in assigned_user_ids or task.created_by == user_id:
        # Assigned user or task creator can update the global task status (drag-drop on Kanban)
        updated_task = task_service.update_task_status(task_id, status, user_id)
        if not updated_task:
            return jsonify({'error': 'Không thể cập nhật trạng thái'}), 500
        return jsonify({'message': 'Trạng thái đã được cập nhật', 'task': updated_task.to_dict()}), 200
    else:
        return jsonify({'error': 'Bạn không được giao task này để cập nhật.'}), 403


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'student')

    if role == 'admin':
        result = task_service.delete_task(task_id, user_id)
        if not result:
            return jsonify({'error': 'Task không tồn tại'}), 404
        return jsonify({'message': 'Task đã được xóa vĩnh viễn'}), 200
    else:
        if role == 'student':
            return jsonify({'error': 'Sinh viên không được phép yêu cầu xóa công việc.'}), 403
        # Request deletion (for teachers)
        req = task_service.request_task_deletion(task_id, user_id)
        return jsonify({'message': 'Yêu cầu xóa đã được gửi cho Admin phê duyệt.', 'request': req.to_dict()}), 202


@task_bp.route('/tasks/<int:task_id>/withdraw', methods=['POST'])
@jwt_required()
def withdraw_task(task_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'student')

    if role == 'student':
        return jsonify({'error': 'Sinh viên không được phép rút khỏi công việc.'}), 403

    req = task_service.request_task_withdrawal(task_id, user_id)
    return jsonify({'message': 'Yêu cầu rút khỏi công việc đã được gửi.', 'request': req.to_dict()}), 202


@task_bp.route('/tasks/requests', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_requests():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    result = task_service.get_pending_requests(page=page, per_page=per_page)
    return jsonify(result), 200


@task_bp.route('/tasks/requests/history', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_requests_history():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    result = task_service.get_processed_requests(page=page, per_page=per_page)
    return jsonify(result), 200


@task_bp.route('/tasks/requests/<int:request_id>/process', methods=['POST'])
@jwt_required()
@role_required('admin')
def process_request(request_id):
    data = request.get_json()
    status = data.get('status') # 'approved' or 'rejected'
    note = data.get('note')

    admin_id = get_jwt_identity()
    result = task_service.process_request(request_id, status, admin_id, note)

    if result is True:
        return jsonify({'message': 'Yêu cầu đã được phê duyệt và task đã được xóa.'}), 200
    if not result:
        return jsonify({'error': 'Yêu cầu không tồn tại'}), 404

    return jsonify({'message': 'Yêu cầu đã được xử lý thành công.', 'request': result.to_dict()}), 200


@task_bp.route('/tasks/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'student')

    if role == 'admin':
        stats = task_service.get_task_stats()
    else:
        stats = task_service.get_task_stats(user_id)

    return jsonify({'stats': stats}), 200


# Subtasks Endpoints
@task_bp.route('/tasks/<int:task_id>/subtasks', methods=['POST'])
@jwt_required()
def add_subtask(task_id):
    data = request.get_json()
    user_id = get_jwt_identity()
    st = task_service.add_subtask(task_id, user_id, data.get('title'))
    return jsonify({'subtask': st.to_dict()}), 201


@task_bp.route('/tasks/<int:task_id>/subtasks/<int:subtask_id>', methods=['PUT'])
@jwt_required()
def update_subtask(task_id, subtask_id):
    data = request.get_json()
    user_id = get_jwt_identity()
    st = task_service.update_subtask(task_id, user_id, subtask_id, **data)
    return jsonify({'subtask': st.to_dict()}), 200


@task_bp.route('/tasks/<int:task_id>/subtasks/<int:subtask_id>', methods=['DELETE'])
@jwt_required()
def delete_subtask(task_id, subtask_id):
    user_id = get_jwt_identity()
    task_service.delete_subtask(task_id, user_id, subtask_id)
    return jsonify({'message': 'Đã xóa nhiệm vụ con'}), 200


# Comments Endpoints
@task_bp.route('/tasks/<int:task_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(task_id):
    data = request.get_json()
    user_id = get_jwt_identity()
    parent_id = data.get('parent_id')
    c = task_service.add_comment(task_id, user_id, data.get('content'), parent_id)
    return jsonify({'comment': c.to_dict()}), 201


@task_bp.route('/tasks/<int:task_id>/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(task_id, comment_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'student')

    success = task_service.delete_comment(comment_id, user_id, role)
    if not success:
        return jsonify({'error': 'Bạn không có quyền xóa thảo luận này'}), 403

    return jsonify({'message': 'Đã xóa thảo luận'}), 200


# Attachments Endpoints
@task_bp.route('/tasks/<int:task_id>/attachments', methods=['POST'])
@jwt_required()
def add_attachment(task_id):
    if 'file' not in request.files:
        return jsonify({'error': 'Không tìm thấy file'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Chưa chọn file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Unique name
        unique_name = f"{datetime.utcnow().timestamp()}_{filename}"
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, unique_name)
        file.save(file_path)

        user_id = get_jwt_identity()
        a = task_service.add_attachment(task_id, user_id, filename, unique_name, file.content_type)
        return jsonify({'attachment': a.to_dict()}), 201

    return jsonify({'error': 'Định dạng file không được hỗ trợ'}), 400


@task_bp.route('/tasks/<int:task_id>/attachments/<int:attachment_id>', methods=['DELETE'])
@jwt_required()
def delete_attachment(task_id, attachment_id):
    user_id = get_jwt_identity()
    task_service.delete_attachment(task_id, user_id, attachment_id)
    return jsonify({'message': 'Đã xóa file đính kèm'}), 200
