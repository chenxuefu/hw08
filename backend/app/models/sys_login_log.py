from app.extensions import db
from app.models.model_types import ID_TYPE


class SysLoginLog(db.Model):
    __tablename__ = "sys_login_log"
    __table_args__ = (
        db.Index("idx_sys_login_log_user_id", "user_id"),
        db.Index("idx_sys_login_log_username", "username"),
        db.Index("idx_sys_login_log_login_ip", "login_ip"),
        db.Index("idx_sys_login_log_status", "status"),
        db.Index("idx_sys_login_log_login_time", "login_time"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    user_id = db.Column(ID_TYPE)
    username = db.Column(db.String(50), nullable=False)
    login_ip = db.Column(db.String(50), nullable=False)
    login_location = db.Column(db.String(100))
    browser = db.Column(db.String(100))
    os = db.Column(db.String(100))
    status = db.Column(db.SmallInteger, nullable=False, default=1)
    message = db.Column(db.String(255))
    login_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )
