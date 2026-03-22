import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from app.repositories.document_repository import DocumentRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository


class DocumentService:
    def __init__(self):
        self.repo = DocumentRepository()
        self.notification_repo = NotificationRepository()
        self.user_repo = UserRepository()

    def upload_document(self, file, title, uploaded_by, **kwargs):
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        if ext not in current_app.config.get('ALLOWED_EXTENSIONS', set()):
            return None, 'File type not allowed'

        # Generate unique filename
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, unique_name)
        file.save(file_path)

        file_size = os.path.getsize(file_path)

        doc = self.repo.create_document(
            title=title,
            file_name=filename,
            file_path=unique_name,
            file_size=file_size,
            file_type=ext,
            uploaded_by=uploaded_by,
            **kwargs
        )
        
        if doc:
            # Notify all students about new document
            students = self.user_repo.get_students()
            student_ids = [s.id for s in students]
            if student_ids:
                self.notification_repo.create_bulk(
                    user_ids=student_ids,
                    title='Tài liệu mới',
                    message=f'Tài liệu "{title}" đã được tải lên.',
                    notification_type='document',
                    reference_type='document',
                    reference_id=doc.id
                )
        return doc, None

    def get_document(self, doc_id):
        return self.repo.get_by_id(doc_id)

    def get_all_documents(self):
        return self.repo.get_all()

    def get_documents_by_uploader(self, user_id):
        return self.repo.get_by_uploader(user_id)

    def search_documents(self, query):
        return self.repo.search(query)

    def download_document(self, doc_id):
        doc = self.repo.increment_download(doc_id)
        if doc:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.file_path)
            if os.path.exists(file_path):
                return doc, file_path
        return None, None

    def delete_document(self, doc_id):
        doc = self.repo.get_by_id(doc_id)
        if doc:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        return self.repo.delete(doc_id)
