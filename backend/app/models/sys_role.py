from app.extensions import db
from app.models.model_types import ID_TYPE


class SysRole(db.Model):
    __tablename__ = "sys_role"
    __table_args__ = (
        db.UniqueConstraint("role_code", name="uk_role_code"),
        db.UniqueConstraint("role_name", name="uk_role_name"),
        db.Index("idx_sys_role_status", "status"),
        db.Index("idx_sys_role_is_deleted", "is_deleted"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    role_code = db.Column(db.String(50), nullable=False)
    role_name = db.Column(db.String(50), nullable=False)
    data_scope = db.Column(db.String(20), nullable=False, default="DATA_SELF")
    description = db.Column(db.String(255))
    status = db.Column(db.SmallInteger, nullable=False, default=1)
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
