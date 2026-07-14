from app.extensions import db
from app.models.model_types import ID_TYPE


class SysPermission(db.Model):
    __tablename__ = "sys_permission"
    __table_args__ = (
        db.UniqueConstraint("perm_code", name="uk_perm_code"),
        db.Index("idx_perm_code", "perm_code"),
        db.Index("idx_perm_type", "perm_type"),
        db.Index("idx_sys_permission_is_deleted", "is_deleted"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    perm_code = db.Column(db.String(100), nullable=False)
    perm_name = db.Column(db.String(100), nullable=False)
    perm_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(255))
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
