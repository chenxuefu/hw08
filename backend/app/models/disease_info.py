from app.extensions import db
from app.models.model_types import ID_TYPE


class DiseaseInfo(db.Model):
    __tablename__ = "disease_info"
    __table_args__ = (
        db.UniqueConstraint("class_name", name="uk_class_name"),
        db.Index("idx_disease_class_name", "class_name"),
        db.Index("idx_disease_chinese_name", "chinese_name"),
        db.Index("idx_disease_create_by", "create_by"),
        db.Index("idx_disease_is_deleted", "is_deleted"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    class_name = db.Column(db.String(50), nullable=False)
    chinese_name = db.Column(db.String(50), nullable=False)
    alias = db.Column(db.String(200))
    symptom = db.Column(db.Text, nullable=False)
    cause = db.Column(db.Text, nullable=False)
    prevention = db.Column(db.Text, nullable=False)
    example_image = db.Column(db.String(500))
    severity_level = db.Column(db.SmallInteger, nullable=False, default=1)
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
