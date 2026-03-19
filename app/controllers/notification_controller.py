from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.notification_service import NotificationService

notification_bp = Blueprint('notifications', __name__, url_prefix='/api')
notification_service = NotificationService()


@notification_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    notifications = notification_service.get_notifications(user_id)
    unread_count = notification_service.get_unread_count(user_id)
    return jsonify({
        'notifications': [n.to_dict() for n in notifications],
        'unread_count': unread_count
    }), 200


@notification_bp.route('/notifications/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    user_id = get_jwt_identity()
    count = notification_service.get_unread_count(user_id)
    return jsonify({'unread_count': count}), 200


@notification_bp.route('/notifications/unread', methods=['GET'])
@jwt_required()
def get_unread():
    user_id = get_jwt_identity()
    notifications = notification_service.get_unread(user_id)
    return jsonify({
        'notifications': [n.to_dict() for n in notifications],
        'unread_count': len(notifications)
    }), 200


@notification_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_read(notification_id):
    notification = notification_service.mark_as_read(notification_id)
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    return jsonify({'message': 'Marked as read'}), 200


@notification_bp.route('/notifications/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    user_id = get_jwt_identity()
    notification_service.mark_all_read(user_id)
    return jsonify({'message': 'All notifications marked as read'}), 200
