from marshmallow import Schema, fields, validate


class BatchUploadSchema(Schema):
    batch_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    confidence_threshold = fields.Float(load_default=0.25, validate=validate.Range(min=0.05, max=0.95))
