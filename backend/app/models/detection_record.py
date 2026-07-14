from app.extensions import db
from app.models.model_types import ID_TYPE


class DetectionRecord(db.Model):
    __tablename__ = "detection_record"
    __table_args__ = (
        db.Index("idx_user_id", "user_id"),
        db.Index("idx_batch_id", "batch_id"),
        db.Index("idx_detection_record_status", "status"),
        db.Index("idx_detection_time", "detection_time"),
        db.Index("idx_model_version_id", "model_version_id"),
        db.Index("idx_detection_record_is_deleted", "is_deleted"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    user_id = db.Column(ID_TYPE, db.ForeignKey("sys_user.id"), nullable=False)
    batch_id = db.Column(ID_TYPE, db.ForeignKey("detection_batch.id"))
    image_path = db.Column(db.String(500), nullable=False)
    result_image_path = db.Column(db.String(500))
    image_name = db.Column(db.String(255), nullable=False)
    image_size = db.Column(db.BigInteger, nullable=False, default=0)
    image_width = db.Column(db.Integer, nullable=False, default=0)
    image_height = db.Column(db.Integer, nullable=False, default=0)
    total_detections = db.Column(db.Integer, nullable=False, default=0)
    avg_confidence = db.Column(db.Numeric(5, 4), nullable=False, default=0)
    inference_time_ms = db.Column(db.Integer, nullable=False, default=0)
    model_version_id = db.Column(
        ID_TYPE,
        db.ForeignKey("model_version.id"),
        nullable=False,
    )
    status = db.Column(db.SmallInteger, nullable=False, default=0)
    error_message = db.Column(db.String(500))
    detection_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )
    create_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )
    update_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )
    is_deleted = db.Column(db.SmallInteger, nullable=False, default=0)
