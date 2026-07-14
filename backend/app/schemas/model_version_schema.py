from marshmallow import Schema, fields, validate


metric_validator = validate.Range(min=0, max=1)


class ModelVersionCreateSchema(Schema):
    version_code = fields.String(required=True, validate=validate.Length(min=1, max=50))
    model_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    weight_path = fields.String(required=True, validate=validate.Length(min=1, max=500))
    map_50 = fields.Decimal(load_default=0, as_string=False, validate=metric_validator)
    map_50_95 = fields.Decimal(load_default=0, as_string=False, validate=metric_validator)
    precision_rate = fields.Decimal(load_default=0, as_string=False, validate=metric_validator)
    recall_rate = fields.Decimal(load_default=0, as_string=False, validate=metric_validator)
    description = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=500))


class ModelVersionUpdateSchema(ModelVersionCreateSchema):
    is_active = fields.Integer(load_default=0, validate=validate.OneOf([0, 1]))
