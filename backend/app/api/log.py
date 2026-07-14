from flask import Blueprint, request

from app.middlewares.permission_middleware import permission_required
from app.services.log_service import LogService
from app.utils.pagination import parse_pagination_args
from app.utils.response import success_response


log_bp = Blueprint("log", __name__)


def build_log_filters():
    return {
        "username": request.args.get("username"),
        "status": request.args.get("status"),
        "ip": request.args.get("ip"),
        "start_time": request.args.get("start_time"),
        "end_time": request.args.get("end_time"),
    }


@log_bp.get("/logs/login")
@permission_required("log:login:list")
def list_login_logs():
    data = LogService.list_login_logs(build_log_filters(), parse_pagination_args(request.args))
    return success_response(data)


@log_bp.get("/logs/operation")
@permission_required("log:operation:list")
def list_operation_logs():
    data = LogService.list_operation_logs(build_log_filters(), parse_pagination_args(request.args))
    return success_response(data)


@log_bp.get("/logs/audit")
@permission_required("log:audit:list")
def list_audit_logs():
    data = LogService.list_audit_logs(build_log_filters(), parse_pagination_args(request.args))
    return success_response(data)
