from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.document_service import DocumentService
from app.utils.decorators import role_required

document_bp = Blueprint('documents', __name__, url_prefix='/api')
document_service = DocumentService()


@document_bp.route('/documents', methods=['POST'])
@jwt_required()
@role_required('admin', 'teacher')
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    title = request.form.get('title', file.filename)
    user_id = get_jwt_identity()

    doc, error = document_service.upload_document(
        file=file,
        title=title,
        uploaded_by=user_id,
        description=request.form.get('description'),
        course_name=request.form.get('course_name'),
        course_code=request.form.get('course_code'),
        class_group=request.form.get('class_group'),
        category=request.form.get('category', 'general'),
    )

    if error:
        return jsonify({'error': error}), 400

    return jsonify({'message': 'Document uploaded', 'document': doc.to_dict()}), 201


@document_bp.route('/documents', methods=['GET'])
@jwt_required()
def get_documents():
    documents = document_service.get_all_documents()
    return jsonify({'documents': [d.to_dict() for d in documents]}), 200


@document_bp.route('/documents/<int:doc_id>', methods=['GET'])
@jwt_required()
def get_document(doc_id):
    doc = document_service.get_document(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    return jsonify({'document': doc.to_dict()}), 200


@document_bp.route('/documents/<int:doc_id>/download', methods=['GET'])
@jwt_required()
def download_document(doc_id):
    doc, file_path = document_service.download_document(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        doc.file_path,
        as_attachment=True,
        download_name=doc.file_name
    )


@document_bp.route('/documents/search', methods=['GET'])
@jwt_required()
def search_documents():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    documents = document_service.search_documents(query)
    return jsonify({'documents': [d.to_dict() for d in documents]}), 200


@document_bp.route('/documents/<int:doc_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin', 'teacher')
def delete_document(doc_id):
    result = document_service.delete_document(doc_id)
    if not result:
        return jsonify({'error': 'Document not found'}), 404
    return jsonify({'message': 'Document deleted'}), 200
