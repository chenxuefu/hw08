from datetime import datetime

from app.extensions import db
from app.middlewares.log_middleware import write_audit_log
from app.models.sys_menu import SysMenu
from app.models.sys_role import SysRole
from app.models.sys_role_menu import SysRoleMenu
from app.models.sys_role_permission import SysRolePermission
from app.models.sys_user_role import SysUserRole
from app.utils.error_code import BusinessError, ErrorCode
from app.utils.pagination import build_page_data


class RoleService:
    @staticmethod
    def list_roles(filters, pagination):
        query = SysRole.query.filter_by(is_deleted=0)
        if filters.get("role_code"):
            query = query.filter(SysRole.role_code.like(f"%{filters['role_code']}%"))
        if filters.get("role_name"):
            query = query.filter(SysRole.role_name.like(f"%{filters['role_name']}%"))
        if filters.get("status") not in (None, ""):
            query = query.filter(SysRole.status == int(filters["status"]))

        sort_map = {
            "create_time": SysRole.create_time,
            "role_code": SysRole.role_code,
            "role_name": SysRole.role_name,
            "status": SysRole.status,
        }
        order_column = sort_map.get(pagination["sort_field"], SysRole.create_time)
        if pagination["sort_order"] == "asc":
            query = query.order_by(order_column.asc(), SysRole.id.asc())
        else:
            query = query.order_by(order_column.desc(), SysRole.id.desc())

        total = query.count()
        roles = (
            query.offset((pagination["page"] - 1) * pagination["page_size"])
            .limit(pagination["page_size"])
            .all()
        )
        data = [RoleService.serialize_role(role) for role in roles]
        return build_page_data(data, total, pagination["page"], pagination["page_size"])

    @staticmethod
    def get_role(role_id: int):
        role = RoleService.get_role_entity(role_id)
        data = RoleService.serialize_role(role)
        data["menu_ids"] = RoleService.get_role_menu_ids(role.id)
        return data

    @staticmethod
    def create_role(payload):
        RoleService.ensure_unique(payload["role_code"], payload["role_name"])
        role = SysRole(
            role_code=payload["role_code"],
            role_name=payload["role_name"],
            data_scope=payload["data_scope"],
            description=payload.get("description"),
            status=payload.get("status", 1),
            is_deleted=0,
        )
        db.session.add(role)
        db.session.flush()
        write_audit_log("ROLE", role.id, "CREATE", None, RoleService.get_role(role.id))
        db.session.commit()
        return RoleService.get_role(role.id)

    @staticmethod
    def update_role(role_id: int, payload):
        role = RoleService.get_role_entity(role_id)
        before = RoleService.get_role(role_id)
        exists = SysRole.query.filter(
            SysRole.id != role.id,
            SysRole.is_deleted == 0,
            db.or_(
                SysRole.role_code == payload["role_code"],
                SysRole.role_name == payload["role_name"],
            ),
        ).first()
        if exists is not None:
            raise BusinessError(ErrorCode.RESOURCE_EXISTS, "角色编码或名称已存在")
        role.role_code = payload["role_code"]
        role.role_name = payload["role_name"]
        role.data_scope = payload["data_scope"]
        role.description = payload.get("description")
        role.status = payload.get("status", role.status)
        db.session.flush()
        after = RoleService.get_role(role.id)
        write_audit_log("ROLE", role.id, "UPDATE", before, after)
        db.session.commit()
        return after

    @staticmethod
    def delete_role(role_id: int):
        role = RoleService.get_role_entity(role_id)
        before = RoleService.get_role(role_id)
        role.is_deleted = 1
        db.session.query(SysRoleMenu).filter(
            SysRoleMenu.role_id == role.id,
            SysRoleMenu.is_deleted == 0,
        ).update({"is_deleted": 1})
        db.session.query(SysRolePermission).filter(
            SysRolePermission.role_id == role.id,
            SysRolePermission.is_deleted == 0,
        ).update({"is_deleted": 1})
        db.session.query(SysUserRole).filter(
            SysUserRole.role_id == role.id,
            SysUserRole.is_deleted == 0,
        ).update({"is_deleted": 1})
        write_audit_log("ROLE", role.id, "DELETE", before, None)
        db.session.commit()
        return True

    @staticmethod
    def get_role_menus(role_id: int):
        RoleService.get_role_entity(role_id)
        menu_ids = RoleService.get_role_menu_ids(role_id)
        return {"role_id": role_id, "menu_ids": menu_ids}

    @staticmethod
    def assign_role_menus(role_id: int, menu_ids: list[int]):
        RoleService.get_role_entity(role_id)
        RoleService.ensure_menu_ids_valid(menu_ids)
        unique_ids = sorted(set(menu_ids))
        db.session.query(SysRoleMenu).filter(
            SysRoleMenu.role_id == role_id,
            SysRoleMenu.is_deleted == 0,
        ).update({"is_deleted": 1})
        for menu_id in unique_ids:
            db.session.add(SysRoleMenu(role_id=role_id, menu_id=menu_id, is_deleted=0))
        db.session.commit()
        return RoleService.get_role_menus(role_id)

    @staticmethod
    def ensure_menu_ids_valid(menu_ids: list[int]):
        if not menu_ids:
            return
        count = SysMenu.query.filter(SysMenu.id.in_(menu_ids), SysMenu.is_deleted == 0).count()
        if count != len(set(menu_ids)):
            raise BusinessError(ErrorCode.NOT_FOUND, "菜单不存在")

    @staticmethod
    def ensure_unique(role_code: str, role_name: str):
        exists = SysRole.query.filter(
            SysRole.is_deleted == 0,
            db.or_(SysRole.role_code == role_code, SysRole.role_name == role_name),
        ).first()
        if exists is not None:
            raise BusinessError(ErrorCode.RESOURCE_EXISTS, "角色编码或名称已存在")

    @staticmethod
    def get_role_entity(role_id: int):
        role = SysRole.query.filter_by(id=role_id, is_deleted=0).first()
        if role is None:
            raise BusinessError(ErrorCode.NOT_FOUND, "角色不存在")
        return role

    @staticmethod
    def get_role_menu_ids(role_id: int):
        rows = (
            db.session.query(SysRoleMenu.menu_id)
            .filter(SysRoleMenu.role_id == role_id, SysRoleMenu.is_deleted == 0)
            .all()
        )
        return [row[0] for row in rows]

    @staticmethod
    def serialize_role(role: SysRole):
        return {
            "id": role.id,
            "role_code": role.role_code,
            "role_name": role.role_name,
            "data_scope": role.data_scope,
            "description": role.description,
            "status": int(role.status),
            "create_time": RoleService.format_datetime(role.create_time),
            "update_time": RoleService.format_datetime(role.update_time),
        }

    @staticmethod
    def format_datetime(value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value
