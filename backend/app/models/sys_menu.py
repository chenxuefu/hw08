from app.extensions import db
from app.models.model_types import ID_TYPE


class SysMenu(db.Model):
    __tablename__ = "sys_menu"
    __table_args__ = (
        db.Index("idx_parent_id", "parent_id"),
        db.Index("idx_sys_menu_path", "menu_path"),
        db.Index("idx_sys_menu_is_deleted", "is_deleted"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    parent_id = db.Column(ID_TYPE, nullable=False, default=0)
    menu_name = db.Column(db.String(50), nullable=False)
    menu_path = db.Column(db.String(200), nullable=False)
    menu_icon = db.Column(db.String(100))
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    visible = db.Column(db.SmallInteger, nullable=False, default=1)
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
