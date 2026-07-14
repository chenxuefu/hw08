from functools import wraps

from flask import g
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.middlewares.auth_middleware import load_current_identity
from app.models.sys_permission import SysPermission
from app.models.sys_role_permission import SysRolePermission
from app.utils.constants import DATA_SELF
from app.utils.error_code import BusinessError, ErrorCode


def get_role_permission_codes(role_id: int) -> set[str]:
    rows = (
        db.session.query(SysPermission.perm_code)
        .join(
            SysRolePermission,
            db.and_(
                SysRolePermission.permission_id == SysPermission.id,
                SysRolePermission.is_deleted == 0,
            ),
        )
        .filter(
            SysRolePermission.role_id == role_id,
            SysPermission.is_deleted == 0,
        )
        .all()
    )
    return {row[0] for row in rows}


def permission_required(permission_code: str):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user, role = load_current_identity()
            permissions = get_role_permission_codes(role.id)
            if permission_code not in permissions:
                raise BusinessError(ErrorCode.FORBIDDEN)
            g.current_user = user
            g.current_role = role
            g.current_permissions = permissions
            return func(*args, **kwargs)

        return wrapper

    return decorator


def apply_data_scope(query, user_column):
    role = getattr(g, "current_role", None)
    user = getattr(g, "current_user", None)
    if role is None or user is None:
        raise BusinessError(ErrorCode.UNAUTHORIZED)
    if role.data_scope == DATA_SELF:
        return query.filter(user_column == user.id)
    return query
