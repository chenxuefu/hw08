from app.extensions import db
from app.models.model_types import ID_TYPE


class SysAuditLog(db.Model):
    __tablename__ = "sys_audit_log"
    __table_args__ = (
        db.Index("idx_sys_audit_log_user_id", "user_id"),
        db.Index("idx_sys_audit_log_target_type", "target_type"),
        db.Index("idx_sys_audit_log_target_id", "target_id"),
        db.Index("idx_sys_audit_log_action", "action"),
        db.Index("idx_sys_audit_log_time", "audit_time"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    user_id = db.Column(ID_TYPE, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(ID_TYPE, nullable=False)
    action = db.Column(db.String(50), nullable=False)
    before_value = db.Column(db.Text)
    after_value = db.Column(db.Text)
    ip = db.Column(db.String(50), nullable=False)
    audit_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )
