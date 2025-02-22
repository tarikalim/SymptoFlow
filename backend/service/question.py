from sqlalchemy.exc import SQLAlchemyError
from backend.model import db
from backend.model.model import Question
from backend.exception.exception import QuestionCreationFailed
from typing import List


class QuestionService:
    @staticmethod
    def add_question(chat_id: int, text: str) -> Question:

        try:
            new_question = Question(text=text, chat_id=chat_id)
            db.session.add(new_question)
            db.session.commit()
            return new_question
        except SQLAlchemyError:
            db.session.rollback()
            raise QuestionCreationFailed()

    @staticmethod
    def get_questions_by_chat_id(chat_id: int) -> List[Question]:

        questions = Question.query.filter_by(chat_id=chat_id).all()
        return questions if questions else []
