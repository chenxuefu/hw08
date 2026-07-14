from marshmallow import Schema, fields, validate


class DetectionSingleSchema(Schema):
    confidence_threshold = fields.Float(load_default=0.25, validate=validate.Range(min=0.05, max=0.95))
