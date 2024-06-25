from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(load_only=True)


class StoreSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
