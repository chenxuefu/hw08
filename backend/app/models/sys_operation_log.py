from app.extensions import db
from app.models.model_types import ID_TYPE


class SysOperationLog(db.Model):
    __tablename__ = "sys_operation_log"
    __table_args__ = (
        db.Index("idx_sys_operation_log_user_id", "user_id"),
        db.Index("idx_sys_operation_log_module", "module"),
        db.Index("idx_sys_operation_log_status", "status"),
        db.Index("idx_sys_operation_log_time", "operation_time"),
    )

    id = db.Column(ID_TYPE, primary_key=True, autoincrement=True)
    user_id = db.Column(ID_TYPE, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    module = db.Column(db.String(50), nullable=False)
    operation = db.Column(db.String(100), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    request_url = db.Column(db.String(500), nullable=False)
    request_params = db.Column(db.Text)
    response_code = db.Column(db.Integer, nullable=False, default=0)
    ip = db.Column(db.String(50), nullable=False)
    cost_ms = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.SmallInteger, nullable=False, default=1)
    operation_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )
