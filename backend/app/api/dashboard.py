from flask import Blueprint, request

from app.middlewares.permission_middleware import permission_required
from app.services.dashboard_service import DashboardService
from app.utils.response import success_response


dashboard_bp = Blueprint("dashboard", __name__)


def build_dashboard_filters():
    return {
        "days": request.args.get("days", 7),
        "limit": request.args.get("limit", 10),
        "start_time": request.args.get("start_time"),
        "end_time": request.args.get("end_time"),
    }


@dashboard_bp.get("/dashboard/summary")
@permission_required("dashboard:view")
def dashboard_summary():
    data = DashboardService.summary(build_dashboard_filters())
    return success_response(data)


@dashboard_bp.get("/dashboard/class-distribution")
@permission_required("dashboard:view")
def dashboard_class_distribution():
    data = DashboardService.class_distribution(build_dashboard_filters())
    return success_response(data)


@dashboard_bp.get("/dashboard/trend")
@permission_required("dashboard:view")
def dashboard_trend():
    data = DashboardService.trend(build_dashboard_filters())
    return success_response(data)


@dashboard_bp.get("/dashboard/top-users")
@permission_required("dashboard:view")
def dashboard_top_users():
    data = DashboardService.top_users(build_dashboard_filters())
    return success_response(data)
