
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt import DecodeError, ExpiredSignatureError
from sqlalchemy.exc import SQLAlchemyError
from flask_restx import Api
from backend.exception.exception import ApplicationException
from backend.model import db


def error_handler(api: Api):
    @api.errorhandler(ApplicationException)
    def handle_application_exception(error):
        response = {'message': error.message}
        return response, error.status_code

    @api.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        db.session.rollback()
        return {'message': 'A database error occurred', 'details': str(error)}, 500

    @api.errorhandler(Exception)
    def handle_generic_error(error):
        if isinstance(error, (
                JWTExtendedException, DecodeError, SQLAlchemyError, ApplicationException, ExpiredSignatureError)):
            raise error
        return {'message': 'An error occurred', 'details': str(error)}, 500
