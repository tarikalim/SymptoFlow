from typing import List

from backend.chatbot.agent.title_agent import TitleGenerator
from backend.service.agent_pool import agent_pool
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.exc import SQLAlchemyError

from backend.exception.exception import ApplicationException, ChatNotFoundException
from backend.model import db
from backend.model.model import Chat as ChatModel, Chat, User
from backend.service.answer import AnswerService
from backend.service.question import QuestionService
from backend.service.record import RecordService  # RecordService import edildi


class ChatService:
    _documents_cache = None

    @staticmethod
    def start_chat(user_id: int):
        new_chat = ChatModel(user_id=user_id)
        db.session.add(new_chat)
        db.session.commit()
        return {"message": "Chat started successfully", "chat_id": new_chat.id}

    @staticmethod
    def interact_with_agent(chat_id: int, question: str):
        questions = QuestionService.get_questions_by_chat_id(chat_id)
        is_first_message = len(questions) == 0

        chat_history = []

        for q in questions:
            chat_history.append(HumanMessage(content=q.text))
            answer = AnswerService.get_answer_by_question_id(q.id)
            if answer:
                chat_history.append(AIMessage(content=answer.text))

        chat = ChatService.get_chat_by_id(chat_id)

        patient = User.query.filter_by(id=chat.user_id).first()

        user_records = RecordService.get_records_by_user_id(chat.user_id)
        for record in user_records:
            chat_history.append(
                AIMessage(
                    content=f"[Patient Record] {record.created_at} - Added by {record.added_by_role}: {record.content}"
                )
            )

        if patient:
            directive = f"Please address the patient by their first name: {patient.first_name}."
            chat_history.insert(0, AIMessage(content=directive))

        agent = agent_pool.get_agent()
        agent.chat_history = chat_history

        try:
            answer_content = agent.ask(question)

            new_question = QuestionService.add_question(chat_id, question)
            AnswerService.add_answer(new_question.id, answer_content)

            if is_first_message:
                title_agent = TitleGenerator()
                generated_title = title_agent.generate_title(question)
                chat.title = generated_title

            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise ApplicationException()
        finally:
            agent_pool.release_agent(agent)

        return {"question": question, "answer": answer_content}

    @staticmethod
    def get_chat_by_id(chat_id: int):
        chat = Chat.query.filter_by(id=chat_id).first()
        if not chat:
            raise ChatNotFoundException()
        return chat

    @staticmethod
    def get_chat_history(chat_id: int):
        chat = ChatService.get_chat_by_id(chat_id)

        questions = QuestionService.get_questions_by_chat_id(chat_id)
        history = []
        for question in questions:
            answer = AnswerService.get_answer_by_question_id(question.id)
            history.append({
                "question": question.text,
                "answer": answer.text if answer else None
            })

        return {
            "chat_id": chat_id,
            "user_id": chat.user_id,
            "title": chat.title,
            "history": history
        }

    @staticmethod
    def get_chats_by_user_id(user_id: int) -> List[dict]:
        chats = db.session.query(Chat.id, Chat.title).filter_by(user_id=user_id).all()
        return [{"chat_id": chat[0], "title": chat[1]} for chat in chats]
