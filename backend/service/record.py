from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from backend.exception.exception import DatabaseOperationException
from backend.model import db
from backend.model.model import Record


class RecordService:
    @staticmethod
    def create_record(user_id, content, creator_role):
        new_record = Record(
            user_id=user_id,
            content=content,
            created_at=datetime.utcnow(),
            added_by_role=creator_role
        )

        try:
            db.session.add(new_record)
            db.session.commit()
        except SQLAlchemyError:
            raise DatabaseOperationException()
        return new_record

    @staticmethod
    def get_records_by_user_id(user_id):
        try:
            records = Record.query.filter_by(user_id=user_id).all()
            return records
        except SQLAlchemyError:
            raise DatabaseOperationException()
