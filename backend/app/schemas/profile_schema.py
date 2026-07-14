from marshmallow import Schema, fields, validate


phone_validator = validate.Regexp(r"^\d{11}$")


class ProfileUpdateSchema(Schema):
    real_name = fields.String(required=True, validate=validate.Length(min=2, max=50))
    email = fields.Email(load_default=None, allow_none=True)
    phone = fields.String(load_default=None, allow_none=True, validate=phone_validator)


class PasswordChangeSchema(Schema):
    old_password = fields.String(required=True, validate=validate.Length(min=6, max=50))
    new_password = fields.String(required=True, validate=validate.Length(min=6, max=20))
    confirm_password = fields.String(required=True, validate=validate.Length(min=6, max=20))
