from flask_jwt_extended import get_jwt, jwt_required
from flask_restx import Resource, Namespace, fields
from backend.service.record import RecordService

record_ns = Namespace('records', description='Medical record operations')

record_create_model = record_ns.model('RecordCreate', {
    'content': fields.String(required=True, description='Medical record content')
})

record_model = record_ns.model('Record', {
    'id': fields.Integer(description='Record ID'),
    'user_id': fields.Integer(description='User ID'),
    'content': fields.String(description='Record Content'),
    'created_at': fields.DateTime(description='Timestamp'),
    'added_by_role': fields.String(description='Role of the creator')
})



@record_ns.route('/<int:user_id>')
class UserRecords(Resource):
    @record_ns.marshal_list_with(record_model)
    def get(self, user_id):
        records = RecordService.get_records_by_user_id(user_id)
        return records, 200


@record_ns.route('/create/<int:user_id>')
class CreateRecord(Resource):
    @jwt_required()
    @record_ns.expect(record_create_model, validate=True)
    @record_ns.marshal_with(record_model)
    def post(self, user_id):
        data = record_ns.payload
        jwt_claims = get_jwt()
        creator_role = jwt_claims.get("role")
        record = RecordService.create_record(user_id, data["content"], creator_role)
        return record, 201
