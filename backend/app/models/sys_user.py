from app.extensions import db
from app.models.model_types import ID_TYPE


class SysUser(db.Model):
    __tablename__ = "sys_user"
    __table_args__ = (
        db.UniqueConstraint("username", name="uk_username"),
        db.Index("idx_email", "email"),
        db.Index("idx_phone", "phone"),
        db.Index("idx_status", "status"),
        db.Index("idx_is_deleted", "is_deleted"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    real_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(255))
    status = db.Column(db.SmallInteger, nullable=False, default=1)
    last_login_time = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(50))
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
