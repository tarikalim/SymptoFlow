from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields
from backend.service.chat import ChatService
from backend.exception.exception import AuthorizationException

chat_ns = Namespace("chat", description="Chat endpoints")

start_chat_model = chat_ns.model("StartChat", {
    "user_id": fields.Integer(required=True, description="ID of the user"),
})

send_question_model = chat_ns.model("SendQuestion", {
    "chat_id": fields.Integer(required=True, description="Chat ID"),
    "question": fields.String(required=True, description="Question content"),
})

chat_history_model = chat_ns.model("ChatHistory", {
    "chat_id": fields.Integer(description="Chat ID"),
    "user_id": fields.Integer(description="User ID"),
    "title": fields.String(description="Chat Title"),
    "history": fields.List(fields.Nested(chat_ns.model("ChatMessage", {
        "question": fields.String(description="Question asked"),
        "answer": fields.String(description="Answer given")
    })))
})


@chat_ns.route("/start")
class StartChat(Resource):
    @jwt_required()
    def post(self):
        """Start a new chat"""
        current_user = int(get_jwt_identity())  # String yerine integer olarak al
        result = ChatService.start_chat(current_user)
        return result, 201


@chat_ns.route("/send-question")
class SendQuestion(Resource):
    @jwt_required()
    @chat_ns.expect(send_question_model, validate=True)
    def post(self):
        """Send a question to the chat agent"""
        data = request.get_json(silent=True)
        current_user = int(get_jwt_identity())  # String yerine integer olarak al

        chat = ChatService.get_chat_by_id(data["chat_id"])
        if chat.user_id != current_user:  # current_user artık integer, .id kullanmaya gerek yok
            raise AuthorizationException("You are not authorized to access this chat.")

        result = ChatService.interact_with_agent(data["chat_id"], data["question"])
        return result, 200


@chat_ns.route("/<int:chat_id>/history")
class ChatHistory(Resource):
    @chat_ns.marshal_with(chat_history_model)
    def get(self, chat_id):
        """Retrieve chat history"""
        result = ChatService.get_chat_history(chat_id)


        return result, 200


@chat_ns.route("/chats")
class UserChatIDs(Resource):
    @jwt_required()
    def get(self):
        """Get all chat IDs for the logged-in user"""
        current_user = int(get_jwt_identity())  # String yerine integer olarak al
        chat_ids = ChatService.get_chats_by_user_id(current_user)
        return {"user_id": current_user, "chat_ids": chat_ids}, 200

