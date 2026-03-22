from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.user_service import UserService
from app.utils.decorators import role_required
from sqlalchemy import text
import os

user_manage_bp = Blueprint('user_management', __name__, url_prefix='/api/admin')
user_service = UserService()

@user_manage_bp.route('/system/health', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_system_health():
    # 1. Check Database
    try:
        from app.extensions import db
        db.session.execute(text('SELECT 1'))
        db_status = 'online'
    except Exception as e:
        print(f"Health check DB error: {e}")
        db_status = 'offline'

    # 2. Check Storage
    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    storage_healthy = os.path.exists(upload_dir) and os.access(upload_dir, os.W_OK)
    storage_status = 'healthy' if storage_healthy else 'error'

    # 3. Check Mail Configuration & Connection
    from app.extensions import mail
    mail_server = current_app.config.get('MAIL_SERVER')
    if not mail_server:
        mail_status = 'not_configured'
    else:
        try:
            # Try to connect to SMTP server
            with mail.connect() as conn:
                mail_status = 'online'
        except Exception as e:
            print(f"Mail connection health check failed: {e}")
            mail_status = 'connection_error'

    return jsonify({
        'database': db_status,
        'storage': storage_status,
        'mail': mail_status,
        'api': 'online'
    }), 200

@user_manage_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_all_users():
    query = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    if query:
        paginated = user_service.search_users(query, page=page, per_page=per_page)
    else:
        paginated = user_service.get_all_users(page=page, per_page=per_page)

    return jsonify({
        'users': [u.to_dict() for u in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
        'per_page': paginated.per_page,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev
    }), 200

@user_manage_bp.route('/users', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password', '123456') # Default password if not provided
    full_name = data.get('full_name')
    role = data.get('role', 'student')
    
    if not username or not email or not full_name:
        return jsonify({'error': 'Username, email, and full name are required'}), 400
        
    user, error = user_service.register(
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        role=role,
        department=data.get('department'),
        phone=data.get('phone'),
        student_id=data.get('student_id')
    )
    
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201

@user_manage_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_user(user_id):
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()}), 200

@user_manage_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_user(user_id):
    data = request.get_json()
    user = user_service.update_user(user_id, **data)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': 'User updated successfully', 'user': user.to_dict()}), 200

@user_manage_bp.route('/users/<int:user_id>/toggle-active', methods=['PUT'])
@jwt_required()
@role_required('admin')
def toggle_user_active(user_id):
    user = user_service.toggle_active(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    status = 'activated' if user.is_active else 'deactivated'
    return jsonify({'message': f'User {status} successfully', 'is_active': user.is_active}), 200

@user_manage_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_user(user_id):
    print(f"DEBUG: DELETE request for user_id: {user_id}")
    # Prevent admin from deleting themselves
    current_user_id = get_jwt_identity()
    if int(current_user_id) == int(user_id):
        return jsonify({'error': 'Bạn không thể tự xóa chính mình'}), 400
        
    try:
        result = user_service.delete_user(user_id)
        if not result:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        print(f"Error in delete_user: {str(e)}")
        return jsonify({'error': f'Không thể xóa người dùng: {str(e)}'}), 400
@user_manage_bp.route('/users/<int:user_id>/toggle-approve', methods=['PUT'])
@jwt_required()
@role_required('admin')
def toggle_user_approval(user_id):
    user = user_service.toggle_approved(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Notify user if approved
    if user.is_approved:
        try:
            from app.models.notification import Notification
            from app.extensions import db
            notif = Notification(
                user_id=user.id,
                title='Tài khoản đã được phê duyệt',
                message='Chúc mừng! Tài khoản của bạn đã được quản trị viên phê duyệt. Bạn có thể sử dụng đầy đủ tính năng ngay bây giờ.',
                notification_type='info'
            )
            db.session.add(notif)
            db.session.commit()
        except Exception as e:
            print(f"Error creating approval notification: {e}")

    status = 'approved' if user.is_approved else 'unapproved'
    return jsonify({'message': f'User {status} successfully', 'is_approved': user.is_approved}), 200
