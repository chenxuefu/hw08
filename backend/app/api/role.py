from flask import Blueprint, request

from app.middlewares.permission_middleware import permission_required
from app.schemas.sys_role_schema import RoleCreateSchema, RoleMenuAssignSchema, RoleUpdateSchema
from app.services.role_service import RoleService
from app.utils.pagination import parse_pagination_args
from app.utils.response import success_response


role_bp = Blueprint("role", __name__)
role_create_schema = RoleCreateSchema()
role_update_schema = RoleUpdateSchema()
role_menu_schema = RoleMenuAssignSchema()


@role_bp.get("/roles")
@permission_required("role:list")
def list_roles():
    pagination = parse_pagination_args(request.args)
    filters = {
        "role_code": request.args.get("role_code"),
        "role_name": request.args.get("role_name"),
        "status": request.args.get("status"),
    }
    data = RoleService.list_roles(filters, pagination)
    return success_response(data)


@role_bp.get("/roles/<int:role_id>")
@permission_required("role:detail")
def get_role(role_id: int):
    data = RoleService.get_role(role_id)
    return success_response(data)


@role_bp.post("/roles")
@permission_required("role:create")
def create_role():
    payload = role_create_schema.load(request.get_json(silent=True) or {})
    data = RoleService.create_role(payload)
    return success_response(data, "新增成功")


@role_bp.put("/roles/<int:role_id>")
@permission_required("role:update")
def update_role(role_id: int):
    payload = role_update_schema.load(request.get_json(silent=True) or {})
    data = RoleService.update_role(role_id, payload)
    return success_response(data, "更新成功")


@role_bp.delete("/roles/<int:role_id>")
@permission_required("role:delete")
def delete_role(role_id: int):
    RoleService.delete_role(role_id)
    return success_response({}, "删除成功")


@role_bp.get("/roles/<int:role_id>/menus")
@permission_required("role:detail")
def get_role_menus(role_id: int):
    data = RoleService.get_role_menus(role_id)
    return success_response(data)


@role_bp.put("/roles/<int:role_id>/menus")
@permission_required("role:update")
def assign_role_menus(role_id: int):
    payload = role_menu_schema.load(request.get_json(silent=True) or {})
    data = RoleService.assign_role_menus(role_id, payload["menu_ids"])
    return success_response(data, "分配成功")
