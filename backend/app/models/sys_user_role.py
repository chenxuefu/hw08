from app.extensions import db
from app.models.model_types import ID_TYPE


class SysUserRole(db.Model):
    __tablename__ = "sys_user_role"
    __table_args__ = (
        db.UniqueConstraint("user_id", "role_id", name="uk_user_role"),
        db.Index("idx_sys_user_role_user_id", "user_id"),
        db.Index("idx_sys_user_role_role_id", "role_id"),
        db.Index("idx_sys_user_role_is_deleted", "is_deleted"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    user_id = db.Column(ID_TYPE, db.ForeignKey("sys_user.id"), nullable=False)
    role_id = db.Column(ID_TYPE, db.ForeignKey("sys_role.id"), nullable=False)
    create_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )
    is_deleted = db.Column(db.SmallInteger, nullable=False, default=0)
