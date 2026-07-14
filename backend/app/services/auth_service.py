from datetime import datetime, timedelta

from flask import current_app, g, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
)

from app.extensions import bcrypt, db, jwt
from app.models.sys_login_log import SysLoginLog
from app.models.sys_role import SysRole
from app.models.sys_user import SysUser
from app.models.sys_user_role import SysUserRole
from app.utils.error_code import BusinessError, ErrorCode


class AuthService:
    login_failures: dict[str, dict] = {}
    token_blacklist: dict[str, datetime] = {}

    @classmethod
    def login(cls, username: str, password: str):
        cls.cleanup_state()
        cls.ensure_not_locked(username)

        user, role = cls.get_user_role_by_username(username)
        if user is None or role is None:
            cls.record_login_failure(username, None, "账号或密码错误")
            raise BusinessError(ErrorCode.LOGIN_FAILED)

        if int(user.status) != 1:
            cls.write_login_log(user.id, username, 0, "账号被禁用")
            raise BusinessError(ErrorCode.ACCOUNT_DISABLED)

        if not bcrypt.check_password_hash(user.password, password):
            cls.record_login_failure(username, user.id, "账号或密码错误")
            raise BusinessError(ErrorCode.LOGIN_FAILED)

        cls.login_failures.pop(username, None)
        user.last_login_time = datetime.now()
        user.last_login_ip = cls.request_ip()

        claims = {
            "user_id": user.id,
            "username": user.username,
            "role_code": role.role_code,
            "data_scope": role.data_scope,
        }
        access_token = create_access_token(identity=str(user.id), additional_claims=claims)
        refresh_token = create_refresh_token(identity=str(user.id), additional_claims=claims)
        cls.write_login_log(user.id, username, 1, "登录成功")
        db.session.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": int(current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds()),
            "user_info": cls.serialize_user_info(user, role),
        }

    @classmethod
    def refresh(cls):
        cls.cleanup_state()
        user_id = get_jwt_identity()
        user, role = cls.get_user_role_by_user_id(int(user_id))
        if user is None or role is None or int(user.status) != 1:
            raise BusinessError(ErrorCode.UNAUTHORIZED)

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "user_id": user.id,
                "username": user.username,
                "role_code": role.role_code,
                "data_scope": role.data_scope,
            },
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={
                "user_id": user.id,
                "username": user.username,
                "role_code": role.role_code,
                "data_scope": role.data_scope,
            },
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": int(current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds()),
        }

    @classmethod
    def logout(cls):
        payload = get_jwt()
        exp = payload.get("exp")
        if exp:
            cls.token_blacklist[payload["jti"]] = datetime.fromtimestamp(exp)
        return True

    @classmethod
    def get_current_user_info(cls):
        cls.cleanup_state()
        user_id = int(get_jwt_identity())
        user, role = cls.get_user_role_by_user_id(user_id)
        if user is None or role is None or int(user.status) != 1:
            raise BusinessError(ErrorCode.UNAUTHORIZED)
        data = cls.serialize_user_info(user, role)
        data["data_scope"] = role.data_scope
        data["email"] = user.email
        data["phone"] = user.phone
        data["avatar_url"] = f"/api/v1/files/{user.avatar}" if user.avatar else None
        return data

    @classmethod
    def update_profile(cls, payload, avatar_file=None):
        user_id = int(get_jwt_identity())
        user, role = cls.get_user_role_by_user_id(user_id)
        if user is None or role is None or int(user.status) != 1:
            raise BusinessError(ErrorCode.UNAUTHORIZED)
        user.real_name = payload["real_name"]
        user.email = payload.get("email")
        user.phone = payload.get("phone")
        if avatar_file is not None:
            from app.services.file_service import FileService

            saved = FileService.save_upload(avatar_file, {"jpg", "jpeg", "png"}, 2 * 1024 * 1024)
            user.avatar = saved["relative_path"]
        db.session.commit()
        return cls.get_current_user_info()

    @classmethod
    def change_password(cls, old_password: str, new_password: str, confirm_password: str):
        if new_password != confirm_password:
            raise BusinessError(ErrorCode.VALIDATION_ERROR, "两次输入的新密码不一致")
        user_id = int(get_jwt_identity())
        user, role = cls.get_user_role_by_user_id(user_id)
        if user is None or role is None or int(user.status) != 1:
            raise BusinessError(ErrorCode.UNAUTHORIZED)
        if not bcrypt.check_password_hash(user.password, old_password):
            raise BusinessError(ErrorCode.LOGIN_FAILED, "旧密码错误")
        user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        db.session.commit()
        return True

    @classmethod
    def get_user_role_by_username(cls, username: str):
        row = (
            db.session.query(SysUser, SysRole)
            .join(
                SysUserRole,
                db.and_(
                    SysUserRole.user_id == SysUser.id,
                    SysUserRole.is_deleted == 0,
                ),
            )
            .join(
                SysRole,
                db.and_(
                    SysRole.id == SysUserRole.role_id,
                    SysRole.is_deleted == 0,
                ),
            )
            .filter(SysUser.username == username, SysUser.is_deleted == 0)
            .first()
        )
        return row if row else (None, None)

    @classmethod
    def get_user_role_by_user_id(cls, user_id: int):
        row = (
            db.session.query(SysUser, SysRole)
            .join(
                SysUserRole,
                db.and_(
                    SysUserRole.user_id == SysUser.id,
                    SysUserRole.is_deleted == 0,
                ),
            )
            .join(
                SysRole,
                db.and_(
                    SysRole.id == SysUserRole.role_id,
                    SysRole.is_deleted == 0,
                ),
            )
            .filter(SysUser.id == user_id, SysUser.is_deleted == 0)
            .first()
        )
        return row if row else (None, None)

    @classmethod
    def serialize_user_info(cls, user: SysUser, role: SysRole):
        return {
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "role_code": role.role_code,
            "role_name": role.role_name,
            "avatar": user.avatar,
        }

    @classmethod
    def request_ip(cls) -> str:
        return request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1")

    @classmethod
    def request_browser(cls) -> str | None:
        return request.user_agent.browser

    @classmethod
    def request_os(cls) -> str | None:
        return request.user_agent.platform

    @classmethod
    def write_login_log(cls, user_id, username: str, status: int, message: str):
        db.session.add(
            SysLoginLog(
                user_id=user_id,
                username=username,
                login_ip=cls.request_ip(),
                login_location=None,
                browser=cls.request_browser(),
                os=cls.request_os(),
                status=status,
                message=message,
            )
        )

    @classmethod
    def record_login_failure(cls, username: str, user_id, message: str):
        item = cls.login_failures.get(username, {"count": 0, "until": None})
        item["count"] += 1
        if item["count"] >= 5:
            item["until"] = datetime.now() + timedelta(minutes=10)
        cls.login_failures[username] = item
        cls.write_login_log(user_id, username, 0, message if item["until"] is None else "账号已锁定，请10分钟后再试")
        db.session.commit()

    @classmethod
    def ensure_not_locked(cls, username: str):
        lock_state = cls.login_failures.get(username)
        if not lock_state:
            return
        until = lock_state.get("until")
        if until and until > datetime.now():
            raise BusinessError(ErrorCode.LOGIN_FAILED, "账号已锁定，请10分钟后再试")
        if until and until <= datetime.now():
            cls.login_failures.pop(username, None)

    @classmethod
    def cleanup_state(cls):
        now = datetime.now()
        cls.token_blacklist = {
            token_id: expire_at
            for token_id, expire_at in cls.token_blacklist.items()
            if expire_at > now
        }
        cls.login_failures = {
            username: state
            for username, state in cls.login_failures.items()
            if state.get("until") is None or state["until"] > now
        }

    @classmethod
    def is_token_revoked(cls, payload: dict) -> bool:
        cls.cleanup_state()
        return payload.get("jti") in cls.token_blacklist


def register_jwt_callbacks() -> None:
    @jwt.token_in_blocklist_loader
    def token_in_blocklist(_jwt_header, jwt_payload):
        return AuthService.is_token_revoked(jwt_payload)

    @jwt.unauthorized_loader
    def unauthorized_callback(_reason):
        from app.utils.response import error_response

        return error_response(ErrorCode.UNAUTHORIZED)

    @jwt.invalid_token_loader
    def invalid_token_callback(_reason):
        from app.utils.response import error_response

        return error_response(ErrorCode.TOKEN_INVALID)

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        from app.utils.response import error_response

        return error_response(ErrorCode.TOKEN_EXPIRED)

    @jwt.revoked_token_loader
    def revoked_token_callback(_jwt_header, _jwt_payload):
        from app.utils.response import error_response

        return error_response(ErrorCode.UNAUTHORIZED)
