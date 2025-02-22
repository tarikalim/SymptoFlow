from backend.exception.exception import DatabaseOperationException
from backend.model.model import User


class UserService:
    @staticmethod
    def get_user(user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise DatabaseOperationException("User not found")
        return user
