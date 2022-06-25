from marshmallow import Schema, fields

class VehicleSchema(Schema):
    id = fields.Integer()
    name = fields.String()

class RecordSchema(Schema):
    id = fields.Integer()
    latitude = fields.Float()
    longitude = fields.Float()
    altitude = fields.Float()
    speed = fields.Float()
    datetime = fields.DateTime()
    direction = fields.Float()
    vehicle_id = fields.Integer()
    event = fields.String()
    ignition = fields.Boolean()
    battery = fields.Float()
    backup_battery = fields.Float()

class LastRecordSchema(RecordSchema):
    vehicle_name = fields.String()

class RecordQuerySchema(Schema):
    vehicle_name = fields.String()
    start = fields.DateTime()
    end = fields.DateTime()

vehicle_schema = VehicleSchema()
record_schema = RecordSchema()
last_record_schema = LastRecordSchema()
record_query_schema = RecordQuerySchema()
