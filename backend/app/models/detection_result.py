from app.extensions import db
from app.models.model_types import ID_TYPE


class DetectionResult(db.Model):
    __tablename__ = "detection_result"
    __table_args__ = (
        db.Index("idx_record_id", "record_id"),
        db.Index("idx_class_id", "class_id"),
        db.Index("idx_detection_result_is_deleted", "is_deleted"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    record_id = db.Column(ID_TYPE, db.ForeignKey("detection_record.id"), nullable=False)
    class_id = db.Column(db.Integer, nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    class_name_cn = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Numeric(5, 4), nullable=False)
    bbox_x = db.Column(db.Numeric(10, 2), nullable=False)
    bbox_y = db.Column(db.Numeric(10, 2), nullable=False)
    bbox_w = db.Column(db.Numeric(10, 2), nullable=False)
    bbox_h = db.Column(db.Numeric(10, 2), nullable=False)
    create_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )
    is_deleted = db.Column(db.SmallInteger, nullable=False, default=0)
