from functools import wraps
from flask import request
from flask_jwt_extended import decode_token
from backend.exception.exception import AuthorizationException


def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.cookies.get("jwt")

            decoded_token = decode_token(token)
            user_role = decoded_token.get("role")

            if user_role != required_role:
                raise AuthorizationException(f"Access denied for role: {user_role}. Required: {required_role}")

            return func(*args, **kwargs)

        return wrapper

    return decorator