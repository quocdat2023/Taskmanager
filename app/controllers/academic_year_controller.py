from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.academic_year import AcademicYear
from app.extensions import db
from app.utils.decorators import role_required

academic_year_bp = Blueprint('academic_years', __name__, url_prefix='/api')


@academic_year_bp.route('/academic-years', methods=['GET'])
@jwt_required()
def get_academic_years():
    """Lấy danh sách tất cả năm học"""
    years = AcademicYear.query.order_by(AcademicYear.start_year.desc()).all()
    return jsonify({'academic_years': [y.to_dict() for y in years]}), 200


@academic_year_bp.route('/academic-years/active', methods=['GET'])
@jwt_required()
def get_active_academic_year():
    """Lấy năm học đang hoạt động"""
    year = AcademicYear.query.filter_by(is_active=True).first()
    if not year:
        return jsonify({'academic_year': None}), 200
    return jsonify({'academic_year': year.to_dict()}), 200


@academic_year_bp.route('/academic-years', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_academic_year():
    """Tạo mới năm học (chỉ admin)"""
    data = request.get_json()

    start_year = data.get('start_year')
    end_year = data.get('end_year')

    if not start_year or not end_year:
        return jsonify({'error': 'Vui lòng nhập năm bắt đầu và năm kết thúc'}), 400

    try:
        start_year = int(start_year)
        end_year = int(end_year)
    except (ValueError, TypeError):
        return jsonify({'error': 'Năm học không hợp lệ'}), 400

    if end_year != start_year + 1:
        return jsonify({'error': 'Năm kết thúc phải bằng năm bắt đầu + 1'}), 400

    name = f"{start_year}-{end_year}"

    # Kiểm tra trùng lặp
    existing = AcademicYear.query.filter_by(name=name).first()
    if existing:
        return jsonify({'error': f'Năm học {name} đã tồn tại'}), 409

    user_id = get_jwt_identity()

    # Nếu set is_active=True, tắt các năm học đang active khác
    is_active = data.get('is_active', False)
    if is_active:
        AcademicYear.query.filter_by(is_active=True).update({'is_active': False})
        db.session.flush()

    year = AcademicYear(
        name=name,
        start_year=start_year,
        end_year=end_year,
        is_active=is_active,
        description=data.get('description', ''),
        created_by=user_id
    )
    db.session.add(year)
    db.session.commit()

    return jsonify({'message': f'Đã tạo năm học {name}', 'academic_year': year.to_dict()}), 201


@academic_year_bp.route('/academic-years/<int:year_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_academic_year(year_id):
    """Cập nhật năm học"""
    year = AcademicYear.query.get(year_id)
    if not year:
        return jsonify({'error': 'Không tìm thấy năm học'}), 404

    data = request.get_json()

    # Nếu set is_active=True, tắt các năm học đang active khác
    if data.get('is_active'):
        AcademicYear.query.filter(AcademicYear.id != year_id, AcademicYear.is_active == True).update({'is_active': False})
        db.session.flush()
        year.is_active = True
    elif 'is_active' in data:
        year.is_active = data['is_active']

    if 'description' in data:
        year.description = data['description']

    db.session.commit()
    return jsonify({'message': 'Đã cập nhật năm học', 'academic_year': year.to_dict()}), 200


@academic_year_bp.route('/academic-years/<int:year_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_academic_year(year_id):
    """Xóa năm học"""
    year = AcademicYear.query.get(year_id)
    if not year:
        return jsonify({'error': 'Không tìm thấy năm học'}), 404

    if year.is_active:
        return jsonify({'error': 'Không thể xóa năm học đang hoạt động. Hãy chọn năm học khác trước.'}), 400
    
    # Save name before deleting for response message
    year_name = year.name
    
    db.session.delete(year)
    db.session.commit()
    return jsonify({'message': f'Đã xóa năm học {year_name}'}), 200


@academic_year_bp.route('/academic-years/<int:year_id>/set-active', methods=['PUT'])
@jwt_required()
@role_required('admin')
def set_active_academic_year(year_id):
    """Đặt năm học làm năm học hiện tại"""
    year = AcademicYear.query.get(year_id)
    if not year:
        return jsonify({'error': 'Không tìm thấy năm học'}), 404

    # Tắt tất cả năm học đang active bằng cách lấy objects và chuyển trạng thái
    # (Tránh lỗi synchronization của bulk update)
    active_years = AcademicYear.query.filter_by(is_active=True).all()
    for ay in active_years:
        ay.is_active = False
    
    db.session.flush()

    year.is_active = True
    db.session.commit()

    return jsonify({'message': f'Đã đặt {year.name} là năm học hiện tại', 'academic_year': year.to_dict()}), 200
