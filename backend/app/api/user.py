from flask import Blueprint, request

from app.middlewares.permission_middleware import permission_required
from app.schemas.sys_user_schema import UserCreateSchema, UserStatusSchema, UserUpdateSchema
from app.services.user_service import UserService
from app.utils.pagination import parse_pagination_args
from app.utils.response import success_response


user_bp = Blueprint("user", __name__)
user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()
user_status_schema = UserStatusSchema()


@user_bp.get("/users")
@permission_required("user:list")
def list_users():
    pagination = parse_pagination_args(request.args)
    filters = {
        "username": request.args.get("username"),
        "real_name": request.args.get("real_name"),
        "status": request.args.get("status"),
    }
    data = UserService.list_users(filters, pagination)
    return success_response(data)


@user_bp.get("/users/<int:user_id>")
@permission_required("user:detail")
def get_user(user_id: int):
    data = UserService.get_user(user_id)
    return success_response(data)


@user_bp.post("/users")
@permission_required("user:create")
def create_user():
    payload = user_create_schema.load(request.get_json(silent=True) or {})
    data = UserService.create_user(payload)
    return success_response(data, "新增成功")


@user_bp.put("/users/<int:user_id>")
@permission_required("user:update")
def update_user(user_id: int):
    payload = user_update_schema.load(request.get_json(silent=True) or {})
    data = UserService.update_user(user_id, payload)
    return success_response(data, "更新成功")


@user_bp.delete("/users/<int:user_id>")
@permission_required("user:delete")
def delete_user(user_id: int):
    UserService.delete_user(user_id)
    return success_response({}, "删除成功")


@user_bp.patch("/users/<int:user_id>/status")
@permission_required("user:update")
def update_user_status(user_id: int):
    payload = user_status_schema.load(request.get_json(silent=True) or {})
    data = UserService.update_status(user_id, payload["status"])
    return success_response(data, "状态更新成功")


@user_bp.post("/users/<int:user_id>/reset-password")
@permission_required("user:reset-password")
def reset_user_password(user_id: int):
    UserService.reset_password(user_id)
    return success_response({}, "重置成功")
