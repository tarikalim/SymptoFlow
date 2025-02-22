from flask_restx import Resource, Namespace, fields
from flask import request
from backend.service.auth import AuthService

auth_ns = Namespace('auth', description='Authentication operations')

user_registration_model = auth_ns.model('UserRegistration', {
    'first_name': fields.String(required=True, description='First Name'),
    'last_name': fields.String(required=True, description='Last Name'),
    'role_id': fields.Integer(required=True, description='Role ID (1=Doctor, 2=Patient)'),
    'password': fields.String(required=True, description='Password')
})

user_login_model = auth_ns.model('UserLogin', {
    'user_id': fields.Integer(required=True, description='User ID'),
    'password': fields.String(required=True, description='Password')
})


@auth_ns.route('/register')
class UserRegistration(Resource):
    @auth_ns.expect(user_registration_model, validate=True)
    def post(self):
        data = request.json
        user = AuthService.register_user(
            first_name=data['first_name'],
            last_name=data['last_name'],
            role_id=data['role_id'],
            password=data['password']
        )
        return {
            "message": "User registered successfully",
            "user_id": user.id
        }, 201


@auth_ns.route('/login')
class UserLogin(Resource):
    @auth_ns.expect(user_login_model, validate=True)
    def post(self):
        data = request.json
        token = AuthService.login_user(
            user_id=data['user_id'],
            password=data['password']
        )
        return {"token": token}, 200
