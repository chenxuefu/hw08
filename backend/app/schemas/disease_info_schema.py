from marshmallow import Schema, fields, validate


class DiseaseCreateSchema(Schema):
    class_name = fields.String(required=True, validate=validate.OneOf(["rust", "smut", "healthy", "aphid"]))
    chinese_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    alias = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=200))
    symptom = fields.String(required=True, validate=validate.Length(min=5, max=2000))
    cause = fields.String(required=True, validate=validate.Length(min=5, max=2000))
    prevention = fields.String(required=True, validate=validate.Length(min=5, max=2000))
    severity_level = fields.Integer(required=True, validate=validate.OneOf([1, 2, 3]))


class DiseaseUpdateSchema(DiseaseCreateSchema):
    pass
