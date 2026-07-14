from datetime import datetime

from app.extensions import bcrypt, db
from app.middlewares.log_middleware import write_audit_log
from app.models.sys_role import SysRole
from app.models.sys_user import SysUser
from app.models.sys_user_role import SysUserRole
from app.utils.error_code import BusinessError, ErrorCode
from app.utils.pagination import build_page_data


class UserService:
    @staticmethod
    def list_users(filters, pagination):
        query = (
            db.session.query(SysUser, SysRole)
            .outerjoin(
                SysUserRole,
                db.and_(
                    SysUserRole.user_id == SysUser.id,
                    SysUserRole.is_deleted == 0,
                ),
            )
            .outerjoin(
                SysRole,
                db.and_(
                    SysRole.id == SysUserRole.role_id,
                    SysRole.is_deleted == 0,
                ),
            )
            .filter(SysUser.is_deleted == 0)
        )

        if filters.get("username"):
            query = query.filter(SysUser.username.like(f"%{filters['username']}%"))
        if filters.get("real_name"):
            query = query.filter(SysUser.real_name.like(f"%{filters['real_name']}%"))
        if filters.get("status") not in (None, ""):
            query = query.filter(SysUser.status == int(filters["status"]))

        sort_map = {
            "create_time": SysUser.create_time,
            "last_login_time": SysUser.last_login_time,
            "username": SysUser.username,
            "status": SysUser.status,
        }
        order_column = sort_map.get(pagination["sort_field"], SysUser.create_time)
        if pagination["sort_order"] == "asc":
            query = query.order_by(order_column.asc(), SysUser.id.asc())
        else:
            query = query.order_by(order_column.desc(), SysUser.id.desc())

        total = query.count()
        rows = (
            query.offset((pagination["page"] - 1) * pagination["page_size"])
            .limit(pagination["page_size"])
            .all()
        )
        data = [UserService.serialize_user(user, role) for user, role in rows]
        return build_page_data(data, total, pagination["page"], pagination["page_size"])

    @staticmethod
    def get_user(user_id: int):
        row = (
            db.session.query(SysUser, SysRole)
            .outerjoin(
                SysUserRole,
                db.and_(
                    SysUserRole.user_id == SysUser.id,
                    SysUserRole.is_deleted == 0,
                ),
            )
            .outerjoin(
                SysRole,
                db.and_(
                    SysRole.id == SysUserRole.role_id,
                    SysRole.is_deleted == 0,
                ),
            )
            .filter(SysUser.id == user_id, SysUser.is_deleted == 0)
            .first()
        )
        if row is None:
            raise BusinessError(ErrorCode.USER_NOT_FOUND)
        return UserService.serialize_user(row[0], row[1])

    @staticmethod
    def create_user(payload):
        UserService.ensure_username_unique(payload["username"])
        role = UserService.get_active_role(payload["role_id"])
        user = SysUser(
            username=payload["username"],
            password=bcrypt.generate_password_hash(payload["password"]).decode("utf-8"),
            real_name=payload["real_name"],
            email=payload.get("email"),
            phone=payload.get("phone"),
            status=payload.get("status", 1),
            is_deleted=0,
        )
        db.session.add(user)
        db.session.flush()
        db.session.add(SysUserRole(user_id=user.id, role_id=role.id, is_deleted=0))
        write_audit_log("USER", user.id, "CREATE", None, UserService.get_user(user.id))
        db.session.commit()
        return UserService.get_user(user.id)

    @staticmethod
    def update_user(user_id: int, payload):
        user = UserService.get_user_entity(user_id)
        before = UserService.get_user(user_id)
        role = UserService.get_active_role(payload["role_id"])
        user.real_name = payload["real_name"]
        user.email = payload.get("email")
        user.phone = payload.get("phone")
        user.status = payload["status"]
        UserService.replace_user_role(user.id, role.id)
        db.session.flush()
        after = UserService.get_user(user.id)
        write_audit_log("USER", user.id, "UPDATE", before, after)
        db.session.commit()
        return after

    @staticmethod
    def delete_user(user_id: int):
        user = UserService.get_user_entity(user_id)
        before = UserService.get_user(user_id)
        user.is_deleted = 1
        db.session.query(SysUserRole).filter(
            SysUserRole.user_id == user.id,
            SysUserRole.is_deleted == 0,
        ).update({"is_deleted": 1})
        write_audit_log("USER", user.id, "DELETE", before, None)
        db.session.commit()
        return True

    @staticmethod
    def update_status(user_id: int, status: int):
        user = UserService.get_user_entity(user_id)
        user.status = status
        db.session.commit()
        return UserService.get_user(user.id)

    @staticmethod
    def reset_password(user_id: int):
        user = UserService.get_user_entity(user_id)
        user.password = bcrypt.generate_password_hash("123456").decode("utf-8")
        db.session.commit()
        return True

    @staticmethod
    def get_user_entity(user_id: int):
        user = SysUser.query.filter_by(id=user_id, is_deleted=0).first()
        if user is None:
            raise BusinessError(ErrorCode.USER_NOT_FOUND)
        return user

    @staticmethod
    def get_active_role(role_id: int):
        role = SysRole.query.filter_by(id=role_id, is_deleted=0).first()
        if role is None:
            raise BusinessError(ErrorCode.NOT_FOUND, "角色不存在")
        return role

    @staticmethod
    def ensure_username_unique(username: str):
        exists = SysUser.query.filter_by(username=username, is_deleted=0).first()
        if exists is not None:
            raise BusinessError(ErrorCode.RESOURCE_EXISTS, "用户名已存在")

    @staticmethod
    def replace_user_role(user_id: int, role_id: int):
        existing = (
            SysUserRole.query.filter(
                SysUserRole.user_id == user_id,
                SysUserRole.role_id == role_id,
            )
            .order_by(SysUserRole.id.desc())
            .first()
        )
        current = SysUserRole.query.filter_by(user_id=user_id, is_deleted=0).first()
        if current is not None and current.role_id == role_id:
            return
        db.session.query(SysUserRole).filter(
            SysUserRole.user_id == user_id,
            SysUserRole.is_deleted == 0,
        ).update({"is_deleted": 1})
        if existing is not None:
            existing.is_deleted = 0
            return
        db.session.add(SysUserRole(user_id=user_id, role_id=role_id, is_deleted=0))

    @staticmethod
    def serialize_user(user: SysUser, role: SysRole | None):
        return {
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "email": user.email,
            "phone": user.phone,
            "avatar": user.avatar,
            "status": int(user.status),
            "last_login_time": UserService.format_datetime(user.last_login_time),
            "create_time": UserService.format_datetime(user.create_time),
            "role_id": role.id if role else None,
            "role_code": role.role_code if role else None,
            "role_name": role.role_name if role else None,
        }

    @staticmethod
    def format_datetime(value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value
