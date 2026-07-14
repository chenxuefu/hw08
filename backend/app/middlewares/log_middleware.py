import json
import time
from datetime import datetime

from flask import g, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.extensions import db
from app.models.sys_audit_log import SysAuditLog
from app.models.sys_operation_log import SysOperationLog


SENSITIVE_KEYS = {"password", "token", "access_token", "refresh_token", "old_password", "new_password", "confirm_password"}


def register_request_logging(app):
    @app.before_request
    def before_request_logging():
        g.request_start_time = time.perf_counter()

    @app.after_request
    def after_request_logging(response):
        if not request.path.startswith("/api/"):
            return response
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return response
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except Exception:
            user_id = None
        username = None
        if user_id is not None:
            from app.models.sys_user import SysUser

            user = SysUser.query.filter_by(id=int(user_id), is_deleted=0).first()
            username = user.username if user else None
        module_name = request.path.strip("/").split("/")[2] if len(request.path.strip("/").split("/")) >= 3 else "system"
        try:
            payload = request.get_json(silent=True)
        except Exception:
            payload = None
        if payload is None and request.form:
            payload = request.form.to_dict()
        request_params = json.dumps(mask_payload(payload or {}), ensure_ascii=False)
        response_payload = response.get_json(silent=True) or {}
        db.session.add(
            SysOperationLog(
                user_id=int(user_id or 0),
                username=username or "anonymous",
                module=module_name,
                operation=request.path,
                method=request.method,
                request_url=request.path,
                request_params=request_params,
                response_code=response_payload.get("code", response.status_code),
                ip=request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1"),
                cost_ms=int((time.perf_counter() - g.get("request_start_time", time.perf_counter())) * 1000),
                status=1 if response.status_code < 400 else 0,
            )
        )
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
        return response


def write_audit_log(target_type: str, target_id: int, action: str, before_value, after_value):
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except Exception:
        user_id = None
    username = None
    if user_id is not None:
        from app.models.sys_user import SysUser

        user = SysUser.query.filter_by(id=int(user_id), is_deleted=0).first()
        username = user.username if user else None
    db.session.add(
        SysAuditLog(
            user_id=int(user_id or 0),
            username=username or "anonymous",
            target_type=target_type,
            target_id=target_id,
            action=action,
            before_value=json.dumps(before_value, ensure_ascii=False) if before_value is not None else None,
            after_value=json.dumps(after_value, ensure_ascii=False) if after_value is not None else None,
            ip=request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1"),
        )
    )


def mask_payload(value):
    if isinstance(value, dict):
        return {key: ("******" if key in SENSITIVE_KEYS else mask_payload(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [mask_payload(item) for item in value]
    return value
