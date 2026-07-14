from functools import wraps

from flask import g
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.auth_service import AuthService
from app.utils.error_code import BusinessError, ErrorCode


def load_current_identity():
    user_id = get_jwt_identity()
    if user_id is None:
        raise BusinessError(ErrorCode.UNAUTHORIZED)
    user, role = AuthService.get_user_role_by_user_id(int(user_id))
    if user is None or role is None or int(user.status) != 1 or int(role.status) != 1:
        raise BusinessError(ErrorCode.UNAUTHORIZED)
    g.current_user = user
    g.current_role = role
    return user, role


def login_required_context(func):
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        load_current_identity()
        return func(*args, **kwargs)

    return wrapper
