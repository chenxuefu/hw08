from marshmallow import Schema, fields, validate


phone_validator = validate.Regexp(r"^\d{11}$")


class UserCreateSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    real_name = fields.String(required=True, validate=validate.Length(min=2, max=50))
    password = fields.String(required=True, validate=validate.Length(min=6, max=20))
    email = fields.Email(load_default=None, allow_none=True)
    phone = fields.String(load_default=None, allow_none=True, validate=phone_validator)
    role_id = fields.Integer(required=True)
    status = fields.Integer(load_default=1, validate=validate.OneOf([0, 1]))


class UserUpdateSchema(Schema):
    real_name = fields.String(required=True, validate=validate.Length(min=2, max=50))
    email = fields.Email(load_default=None, allow_none=True)
    phone = fields.String(load_default=None, allow_none=True, validate=phone_validator)
    role_id = fields.Integer(required=True)
    status = fields.Integer(required=True, validate=validate.OneOf([0, 1]))


class UserStatusSchema(Schema):
    status = fields.Integer(required=True, validate=validate.OneOf([0, 1]))
