from datetime import datetime

from flask import g

from app.extensions import db
from app.models.sys_menu import SysMenu
from app.models.sys_role_menu import SysRoleMenu
from app.utils.error_code import BusinessError, ErrorCode


class MenuService:
    @staticmethod
    def list_tree():
        menus = (
            SysMenu.query.filter_by(is_deleted=0)
            .order_by(SysMenu.sort_order.asc(), SysMenu.id.asc())
            .all()
        )
        return MenuService.build_tree(menus)

    @staticmethod
    def get_menu(menu_id: int):
        menu = MenuService.get_menu_entity(menu_id)
        return MenuService.serialize_menu(menu)

    @staticmethod
    def create_menu(payload):
        menu = SysMenu(
            parent_id=payload.get("parent_id", 0),
            menu_name=payload["menu_name"],
            menu_path=payload["menu_path"],
            menu_icon=payload.get("menu_icon"),
            sort_order=payload.get("sort_order", 0),
            visible=payload.get("visible", 1),
            is_deleted=0,
        )
        db.session.add(menu)
        db.session.commit()
        return MenuService.get_menu(menu.id)

    @staticmethod
    def update_menu(menu_id: int, payload):
        menu = MenuService.get_menu_entity(menu_id)
        menu.parent_id = payload.get("parent_id", 0)
        menu.menu_name = payload["menu_name"]
        menu.menu_path = payload["menu_path"]
        menu.menu_icon = payload.get("menu_icon")
        menu.sort_order = payload.get("sort_order", 0)
        menu.visible = payload.get("visible", 1)
        db.session.commit()
        return MenuService.get_menu(menu.id)

    @staticmethod
    def delete_menu(menu_id: int):
        menu = MenuService.get_menu_entity(menu_id)
        menu.is_deleted = 1
        db.session.query(SysRoleMenu).filter(
            SysRoleMenu.menu_id == menu.id,
            SysRoleMenu.is_deleted == 0,
        ).update({"is_deleted": 1})
        db.session.commit()
        return True

    @staticmethod
    def get_current_user_menus():
        role = g.current_role
        menu_id_select = (
            db.select(SysRoleMenu.menu_id)
            .filter(SysRoleMenu.role_id == role.id, SysRoleMenu.is_deleted == 0)
        )
        menus = (
            SysMenu.query.filter(SysMenu.id.in_(menu_id_select), SysMenu.is_deleted == 0, SysMenu.visible == 1)
            .order_by(SysMenu.sort_order.asc(), SysMenu.id.asc())
            .all()
        )
        return MenuService.build_tree(menus)

    @staticmethod
    def build_tree(menus):
        nodes = {}
        roots = []
        for menu in menus:
            item = MenuService.serialize_menu(menu)
            item["children"] = []
            nodes[menu.id] = item
        for menu in menus:
            item = nodes[menu.id]
            if menu.parent_id and menu.parent_id in nodes:
                nodes[menu.parent_id]["children"].append(item)
            else:
                roots.append(item)
        return roots

    @staticmethod
    def get_menu_entity(menu_id: int):
        menu = SysMenu.query.filter_by(id=menu_id, is_deleted=0).first()
        if menu is None:
            raise BusinessError(ErrorCode.NOT_FOUND, "菜单不存在")
        return menu

    @staticmethod
    def serialize_menu(menu: SysMenu):
        return {
            "id": menu.id,
            "parent_id": menu.parent_id,
            "menu_name": menu.menu_name,
            "menu_path": menu.menu_path,
            "menu_icon": menu.menu_icon,
            "sort_order": menu.sort_order,
            "visible": int(menu.visible),
            "create_time": MenuService.format_datetime(menu.create_time),
            "update_time": MenuService.format_datetime(menu.update_time),
        }

    @staticmethod
    def format_datetime(value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value
