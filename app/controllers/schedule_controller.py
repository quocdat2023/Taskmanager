from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.schedule_service import ScheduleService
from app.utils.decorators import role_required

schedule_bp = Blueprint('schedules', __name__, url_prefix='/api')
schedule_service = ScheduleService()


@schedule_bp.route('/schedules', methods=['POST'])
@jwt_required()
@role_required('admin', 'teacher')
def create_schedule():
    data = request.get_json()
    required = ['title', 'start_time', 'end_time']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    user_id = get_jwt_identity()
    schedule = schedule_service.create_schedule(
        title=data['title'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        created_by=user_id,
        description=data.get('description'),
        event_type=data.get('event_type', 'class'),
        course_name=data.get('course_name'),
        course_code=data.get('course_code'),
        class_group=data.get('class_group'),
        location=data.get('location'),
        color=data.get('color', '#4A90D9'),
    )

    return jsonify({'message': 'Schedule created', 'schedule': schedule.to_dict()}), 201


@schedule_bp.route('/schedules', methods=['GET'])
@jwt_required()
def get_schedules():
    start = request.args.get('start')
    end = request.args.get('end')
    user_id_param = request.args.get('user_id')
    
    if not user_id_param:
        user_id = get_jwt_identity()
    elif user_id_param == 'all':
        user_id = None
    else:
        user_id = user_id_param

    if start and end:
        schedules = schedule_service.get_schedules_by_range(start, end, user_id)
    else:
        if user_id:
            schedules = schedule_service.get_schedules_by_creator(user_id)
        else:
            schedules = schedule_service.get_all_schedules()

    return jsonify({'schedules': [s.to_dict() for s in schedules]}), 200


@schedule_bp.route('/schedules/<int:schedule_id>', methods=['GET'])
@jwt_required()
def get_schedule(schedule_id):
    schedule = schedule_service.get_schedule(schedule_id)
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404
    return jsonify({'schedule': schedule.to_dict()}), 200


@schedule_bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'teacher')
def update_schedule(schedule_id):
    data = request.get_json()
    schedule = schedule_service.update_schedule(schedule_id, **data)
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404
    return jsonify({'message': 'Schedule updated', 'schedule': schedule.to_dict()}), 200


@schedule_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin', 'teacher')
def delete_schedule(schedule_id):
    result = schedule_service.delete_schedule(schedule_id)
    if not result:
        return jsonify({'error': 'Schedule not found'}), 404
    return jsonify({'message': 'Schedule deleted'}), 200


@schedule_bp.route('/schedules/upcoming', methods=['GET'])
@jwt_required()
def upcoming_schedules():
    limit = request.args.get('limit', 10, type=int)
    schedules = schedule_service.get_upcoming(limit)
    return jsonify({'schedules': [s.to_dict() for s in schedules]}), 200
