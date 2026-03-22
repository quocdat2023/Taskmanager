from app.repositories.base_repository import BaseRepository
from app.models.document import Document
from app.extensions import db


class DocumentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Document)

    def get_by_uploader(self, user_id):
        return Document.query.filter_by(uploaded_by=user_id).order_by(Document.created_at.desc()).all()

    def get_by_course(self, course_code):
        return Document.query.filter_by(course_code=course_code).order_by(Document.created_at.desc()).all()

    def get_by_category(self, category):
        return Document.query.filter_by(category=category).order_by(Document.created_at.desc()).all()

    def search(self, query_text):
        search = f'%{query_text}%'
        return Document.query.filter(
            db.or_(
                Document.title.ilike(search),
                Document.course_name.ilike(search),
                Document.course_code.ilike(search),
                Document.class_group.ilike(search),
                Document.description.ilike(search),
            )
        ).order_by(Document.created_at.desc()).all()

    def increment_download(self, doc_id):
        doc = self.get_by_id(doc_id)
        if doc:
            doc.download_count += 1
            db.session.commit()
        return doc

    def create_document(self, title, file_name, file_path, uploaded_by, **kwargs):
        doc = Document(
            title=title,
            file_name=file_name,
            file_path=file_path,
            uploaded_by=uploaded_by,
            **kwargs
        )
        db.session.add(doc)
        db.session.commit()
        return doc
