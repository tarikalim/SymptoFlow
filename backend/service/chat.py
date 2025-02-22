from typing import List
from backend.service.agent_pool import agent_pool
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.exc import SQLAlchemyError

from backend.exception.exception import ApplicationException, ChatNotFoundException
from backend.model import db
from backend.model.model import Chat as ChatModel, Chat
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
        chat_history = []

        # **1. Daha önceki soruları ve yanıtları chat history'ye ekle**
        for q in questions:
            chat_history.append(HumanMessage(content=q.text))
            answer = AnswerService.get_answer_by_question_id(q.id)
            if answer:
                chat_history.append(AIMessage(content=answer.text))

        # **2. Kullanıcının record'larını chat history'ye ekle**
        chat = ChatService.get_chat_by_id(chat_id)
        user_records = RecordService.get_records_by_user_id(chat.user_id)

        for record in user_records:
            chat_history.append(AIMessage(content=f"[Patient Record] {record.created_at}: {record.content}"))

        # **3. Agent'i pool'dan al ve chat history'yi ayarla**
        agent = agent_pool.get_agent()
        agent.chat_history = chat_history

        try:
            answer_content = agent.ask(question)

            new_question = QuestionService.add_question(chat_id, question)
            AnswerService.add_answer(new_question.id, answer_content)

            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise ApplicationException()
        finally:
            agent_pool.release_agent(agent)  # Agent pool'a geri bırak

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
    def get_chats_by_user_id(user_id: int) -> List[int]:
        chat_ids = db.session.query(Chat.id).filter_by(user_id=user_id).all()
        return [chat_id[0] for chat_id in chat_ids]
