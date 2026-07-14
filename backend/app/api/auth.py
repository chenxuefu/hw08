from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.schemas.auth_schema import LoginSchema
from app.schemas.profile_schema import PasswordChangeSchema, ProfileUpdateSchema
from app.services.auth_service import AuthService
from app.utils.response import success_response


auth_bp = Blueprint("auth", __name__)
login_schema = LoginSchema()
profile_update_schema = ProfileUpdateSchema()
password_change_schema = PasswordChangeSchema()


@auth_bp.post("/auth/login")
def login():
    payload = login_schema.load(request.get_json(silent=True) or {})
    data = AuthService.login(payload["username"], payload["password"])
    return success_response(data, "登录成功")


@auth_bp.post("/auth/logout")
@jwt_required()
def logout():
    AuthService.logout()
    return success_response({}, "退出成功")


@auth_bp.post("/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    data = AuthService.refresh()
    return success_response(data, "刷新成功")


@auth_bp.get("/auth/user-info")
@jwt_required()
def user_info():
    data = AuthService.get_current_user_info()
    return success_response(data, "获取成功")


@auth_bp.put("/auth/user-info")
@jwt_required()
def update_user_info():
    payload = profile_update_schema.load(request.form.to_dict() if request.form else (request.get_json(silent=True) or {}))
    avatar_file = request.files.get("avatar")
    data = AuthService.update_profile(payload, avatar_file)
    return success_response(data, "更新成功")


@auth_bp.patch("/auth/password")
@jwt_required()
def update_password():
    payload = password_change_schema.load(request.get_json(silent=True) or {})
    AuthService.change_password(payload["old_password"], payload["new_password"], payload["confirm_password"])
    return success_response({}, "修改成功")
