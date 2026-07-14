from datetime import datetime

from app.models.sys_audit_log import SysAuditLog
from app.models.sys_login_log import SysLoginLog
from app.models.sys_operation_log import SysOperationLog
from app.utils.pagination import build_page_data


class LogService:
    @staticmethod
    def list_login_logs(filters, pagination):
        query = SysLoginLog.query
        query = LogService.apply_common_filters(query, SysLoginLog, filters, "login_time", "login_ip")
        return LogService.paginate(query, pagination, LogService.serialize_login_log)

    @staticmethod
    def list_operation_logs(filters, pagination):
        query = SysOperationLog.query
        query = LogService.apply_common_filters(query, SysOperationLog, filters, "operation_time", "ip")
        return LogService.paginate(query, pagination, LogService.serialize_operation_log)

    @staticmethod
    def list_audit_logs(filters, pagination):
        query = SysAuditLog.query
        query = LogService.apply_common_filters(query, SysAuditLog, filters, "audit_time", "ip")
        return LogService.paginate(query, pagination, LogService.serialize_audit_log)

    @staticmethod
    def apply_common_filters(query, model, filters, time_field_name: str, ip_field_name: str):
        if filters.get("username"):
            query = query.filter(model.username.like(f"%{filters['username']}%"))
        if filters.get("status") not in (None, "") and hasattr(model, "status"):
            query = query.filter(model.status == int(filters["status"]))
        if filters.get("ip"):
            query = query.filter(getattr(model, ip_field_name).like(f"%{filters['ip']}%"))
        start_time = LogService.parse_datetime(filters.get("start_time"))
        end_time = LogService.parse_datetime(filters.get("end_time"))
        time_column = getattr(model, time_field_name)
        if start_time is not None:
            query = query.filter(time_column >= start_time)
        if end_time is not None:
            query = query.filter(time_column <= end_time)
        return query

    @staticmethod
    def paginate(query, pagination, serializer):
        sort_map = {
            "create_time": None,
            "operation_time": getattr(query.column_descriptions[0]["entity"], "operation_time", None),
            "login_time": getattr(query.column_descriptions[0]["entity"], "login_time", None),
            "audit_time": getattr(query.column_descriptions[0]["entity"], "audit_time", None),
        }
        order_column = sort_map.get(pagination["sort_field"])
        if order_column is None:
            entity = query.column_descriptions[0]["entity"]
            order_column = (
                getattr(entity, "login_time", None)
                or getattr(entity, "operation_time", None)
                or getattr(entity, "audit_time", None)
            )
        if pagination["sort_order"] == "asc":
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
        total = query.count()
        items = (
            query.offset((pagination["page"] - 1) * pagination["page_size"])
            .limit(pagination["page_size"])
            .all()
        )
        data = [serializer(item) for item in items]
        return build_page_data(data, total, pagination["page"], pagination["page_size"])

    @staticmethod
    def serialize_login_log(log: SysLoginLog):
        return {
            "id": log.id,
            "user_id": log.user_id,
            "username": log.username,
            "login_ip": log.login_ip,
            "login_location": log.login_location,
            "browser": log.browser,
            "os": log.os,
            "status": int(log.status),
            "message": log.message,
            "login_time": LogService.format_datetime(log.login_time),
        }

    @staticmethod
    def serialize_operation_log(log: SysOperationLog):
        return {
            "id": log.id,
            "user_id": log.user_id,
            "username": log.username,
            "module": log.module,
            "operation": log.operation,
            "method": log.method,
            "request_url": log.request_url,
            "request_params": log.request_params,
            "response_code": log.response_code,
            "ip": log.ip,
            "cost_ms": log.cost_ms,
            "status": int(log.status),
            "operation_time": LogService.format_datetime(log.operation_time),
        }

    @staticmethod
    def serialize_audit_log(log: SysAuditLog):
        return {
            "id": log.id,
            "user_id": log.user_id,
            "username": log.username,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "action": log.action,
            "before_value": log.before_value,
            "after_value": log.after_value,
            "ip": log.ip,
            "audit_time": LogService.format_datetime(log.audit_time),
        }

    @staticmethod
    def parse_datetime(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

    @staticmethod
    def format_datetime(value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value
