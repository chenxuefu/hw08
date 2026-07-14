from marshmallow import Schema, fields, validate


class RoleCreateSchema(Schema):
    role_code = fields.String(required=True, validate=validate.Length(min=3, max=50))
    role_name = fields.String(required=True, validate=validate.Length(min=2, max=50))
    data_scope = fields.String(required=True, validate=validate.OneOf(["DATA_ALL", "DATA_SELF"]))
    description = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))
    status = fields.Integer(load_default=1, validate=validate.OneOf([0, 1]))


class RoleUpdateSchema(RoleCreateSchema):
    pass


class RoleMenuAssignSchema(Schema):
    menu_ids = fields.List(fields.Integer(), required=True)
