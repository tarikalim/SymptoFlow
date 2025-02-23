from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from backend.config import Config
from backend.controller.auth import auth_ns
from backend.controller.chat import chat_ns
from backend.controller.record import record_ns
from backend.controller.user import user_ns
from backend.exception.error_handler import error_handler
from backend.model import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Allow CORS for specific origin and allow credentials
    CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

    api = Api(
        app,
        version="1.0",
        title="SymptoFlow API",
        description="SymptoFlow API.",
        authorizations={
            'Bearer Auth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
            },
        },
        security='Bearer Auth',
    )

    api.add_namespace(chat_ns, path="/chat")
    api.add_namespace(user_ns, path="/user")
    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(record_ns, path="/records")

    jwt = JWTManager(app)
    jwt.init_app(app)
    db.init_app(app)
    error_handler(api)
    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        from backend.middleware.seed_roles import seed_roles

        seed_roles()
    app.run(threaded=True, debug=False)
