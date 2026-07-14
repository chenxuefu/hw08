from app.extensions import db
from app.models.model_types import ID_TYPE


class DetectionBatch(db.Model):
    __tablename__ = "detection_batch"
    __table_args__ = (
        db.Index("idx_detection_batch_user_id", "user_id"),
        db.Index("idx_detection_batch_status", "status"),
        db.Index("idx_detection_batch_create_time", "create_time"),
        db.Index("idx_detection_batch_is_deleted", "is_deleted"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    user_id = db.Column(ID_TYPE, db.ForeignKey("sys_user.id"), nullable=False)
    batch_name = db.Column(db.String(100), nullable=False)
    total_images = db.Column(db.Integer, nullable=False, default=0)
    processed_images = db.Column(db.Integer, nullable=False, default=0)
    success_images = db.Column(db.Integer, nullable=False, default=0)
    failed_images = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.SmallInteger, nullable=False, default=0)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
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
