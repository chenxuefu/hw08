from app.extensions import db
from app.models.model_types import ID_TYPE


class SysRoleMenu(db.Model):
    __tablename__ = "sys_role_menu"
    __table_args__ = (
        db.UniqueConstraint("role_id", "menu_id", name="uk_role_menu"),
        db.Index("idx_sys_role_menu_role_id", "role_id"),
        db.Index("idx_sys_role_menu_menu_id", "menu_id"),
        db.Index("idx_sys_role_menu_is_deleted", "is_deleted"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    role_id = db.Column(ID_TYPE, db.ForeignKey("sys_role.id"), nullable=False)
    menu_id = db.Column(ID_TYPE, db.ForeignKey("sys_menu.id"), nullable=False)
    create_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )
    is_deleted = db.Column(db.SmallInteger, nullable=False, default=0)
