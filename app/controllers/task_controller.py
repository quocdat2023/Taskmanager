from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.task_service import TaskService
from app.services.email_service import EmailService
from app.utils.decorators import role_required

task_bp = Blueprint('tasks', __name__, url_prefix='/api')
task_service = TaskService()


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
    )

    if task and role == 'admin':
        EmailService.send_task_assignment_notification(task)
        
    return jsonify({'message': 'Task đã được tạo', 'task': task.to_dict()}), 201


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
    
    # Check if this is an assignment update for non-admin
    if 'assignee_ids' in data and role != 'admin':
        # Handled inside task_service
        pass

    task = task_service.update_task(task_id, changed_by=user_id, user_role=role, **data)
    if not task:
        return jsonify({'error': 'Task không tồn tại'}), 404
        
    return jsonify({'message': 'Task đã được cập nhật', 'task': task.to_dict()}), 200


@task_bp.route('/tasks/<int:task_id>/history', methods=['GET'])
@jwt_required()
def get_task_history(task_id):
    history = task_service.get_task_history(task_id)
    return jsonify({'history': history}), 200


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

    # personalized logic: everyone updates their own assignment unless they explicitly want master update
    # for simplicity, let's say students/teachers update personal, admin can update master.
    if role == 'admin':
        task = task_service.update_task_status(task_id, status, user_id)
        if not task:
            return jsonify({'error': 'Task không tồn tại'}), 404
        return jsonify({'message': 'Trạng thái chính đã được cập nhật', 'task': task.to_dict()}), 200
    else:
        # Check if user is assigned
        assignment = task_service.update_assignment_status(task_id, user_id, status, data.get('note'))
        if not assignment:
            return jsonify({'error': 'Bạn không được giao task này để cập nhật.'}), 403
        return jsonify({'message': 'Trạng thái cá nhân đã được cập nhật', 'assignment': assignment.to_dict()}), 200


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
    requests = task_service.get_pending_requests()
    return jsonify({'requests': requests}), 200


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
