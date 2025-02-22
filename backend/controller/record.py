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
    'created_at': fields.DateTime(description='Timestamp')
})


@record_ns.route('/<int:user_id>')
class UserRecords(Resource):
    @record_ns.marshal_list_with(record_model)
    def get(self, user_id):
        records = RecordService.get_records_by_user_id(user_id)
        return records, 200


@record_ns.route('/create/<int:user_id>')
class CreateRecord(Resource):
    @record_ns.expect(record_create_model, validate=True)
    @record_ns.marshal_with(record_model)
    def post(self, user_id):
        data = record_ns.payload
        record = RecordService.create_record(user_id, data["content"])
        return record, 201


