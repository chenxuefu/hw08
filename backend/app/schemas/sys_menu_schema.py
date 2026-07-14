from marshmallow import Schema, fields, validate


class MenuCreateSchema(Schema):
    parent_id = fields.Integer(load_default=0)
    menu_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    menu_path = fields.String(required=True, validate=validate.Length(min=1, max=200))
    menu_icon = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=100))
    sort_order = fields.Integer(load_default=0)
    visible = fields.Integer(load_default=1, validate=validate.OneOf([0, 1]))


class MenuUpdateSchema(MenuCreateSchema):
    pass
