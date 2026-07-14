from app.extensions import db
from app.models.model_types import ID_TYPE


class ModelVersion(db.Model):
    __tablename__ = "model_version"
    __table_args__ = (
        db.UniqueConstraint("version_code", name="uk_version_code"),
        db.Index("idx_model_version_code", "version_code"),
        db.Index("idx_model_version_is_active", "is_active"),
        db.Index("idx_model_version_create_by", "create_by"),
        db.Index("idx_model_version_is_deleted", "is_deleted"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    version_code = db.Column(db.String(50), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    weight_path = db.Column(db.String(500), nullable=False)
    map_50 = db.Column(db.Numeric(5, 4), nullable=False, default=0)
    map_50_95 = db.Column(db.Numeric(5, 4), nullable=False, default=0)
    precision_rate = db.Column(db.Numeric(5, 4), nullable=False, default=0)
    recall_rate = db.Column(db.Numeric(5, 4), nullable=False, default=0)
    is_active = db.Column(db.SmallInteger, nullable=False, default=0)
    description = db.Column(db.String(500))
    create_by = db.Column(ID_TYPE, db.ForeignKey("sys_user.id"), nullable=False)
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
