from flask import Blueprint, request

from app.middlewares.auth_middleware import login_required_context
from app.middlewares.permission_middleware import permission_required
from app.schemas.sys_menu_schema import MenuCreateSchema, MenuUpdateSchema
from app.services.menu_service import MenuService
from app.utils.response import success_response


menu_bp = Blueprint("menu", __name__)
menu_create_schema = MenuCreateSchema()
menu_update_schema = MenuUpdateSchema()


@menu_bp.get("/menus/tree")
@permission_required("menu:list")
def list_menu_tree():
    data = MenuService.list_tree()
    return success_response(data)


@menu_bp.get("/menus/<int:menu_id>")
@permission_required("menu:detail")
def get_menu(menu_id: int):
    data = MenuService.get_menu(menu_id)
    return success_response(data)


@menu_bp.post("/menus")
@permission_required("menu:create")
def create_menu():
    payload = menu_create_schema.load(request.get_json(silent=True) or {})
    data = MenuService.create_menu(payload)
    return success_response(data, "新增成功")


@menu_bp.put("/menus/<int:menu_id>")
@permission_required("menu:update")
def update_menu(menu_id: int):
    payload = menu_update_schema.load(request.get_json(silent=True) or {})
    data = MenuService.update_menu(menu_id, payload)
    return success_response(data, "更新成功")


@menu_bp.delete("/menus/<int:menu_id>")
@permission_required("menu:delete")
def delete_menu(menu_id: int):
    MenuService.delete_menu(menu_id)
    return success_response({}, "删除成功")


@menu_bp.get("/menus/current-user")
@login_required_context
def current_user_menus():
    data = MenuService.get_current_user_menus()
    return success_response(data)
