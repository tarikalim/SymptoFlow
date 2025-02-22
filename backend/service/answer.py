from sqlalchemy.exc import SQLAlchemyError
from backend.exception.exception import AnswerCreationFailedException
from backend.model import db
from backend.model.model import Answer
from typing import Optional


class AnswerService:
    @staticmethod
    def add_answer(question_id: int, text: str) -> Answer:

        try:
            new_answer = Answer(text=text, question_id=question_id)
            db.session.add(new_answer)
            db.session.commit()
            return new_answer
        except SQLAlchemyError:
            db.session.rollback()
            raise AnswerCreationFailedException()

    @staticmethod
    def get_answer_by_question_id(question_id: int) -> Optional[Answer]:
        return Answer.query.filter_by(question_id=question_id).first()