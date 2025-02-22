from flask_jwt_extended import create_access_token
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from backend.exception.exception import DatabaseOperationException, InvalidCredentialsException
from backend.model import db
from backend.model.model import User


class AuthService:
    @staticmethod
    def register_user(first_name, last_name, role_id, password):
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            role_id=role_id,
            password=generate_password_hash(password)
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except SQLAlchemyError:
            raise DatabaseOperationException()
        return new_user

    @staticmethod
    def login_user(user_id, password):
        user = User.query.filter_by(id=user_id).first()
        if user and check_password_hash(user.password, password):
            access_token = create_access_token(identity=str(user.id))

            return access_token

        raise InvalidCredentialsException()
