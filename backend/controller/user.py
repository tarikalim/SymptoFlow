from flask_restx import Resource, Namespace, fields
from backend.service.user import UserService
from backend.exception.exception import DatabaseOperationException

user_ns = Namespace('user', description='User operations')

user_model = user_ns.model('User', {
    'id': fields.Integer(description='User ID'),
    'first_name': fields.String(description='First Name'),
    'last_name': fields.String(description='Last Name'),
    'role_id': fields.Integer(description='Role ID (1=Doctor, 2=Patient)')
})


@user_ns.route('/<int:user_id>')
class UserResource(Resource):
    @user_ns.marshal_with(user_model)
    def get(self, user_id):
        try:
            user = UserService.get_user(user_id)
            return user
        except DatabaseOperationException as e:
            return {'message': str(e)}, 404
