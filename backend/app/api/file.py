from flask import Blueprint, send_file

from app.middlewares.auth_middleware import login_required_context
from app.services.file_service import FileService


file_bp = Blueprint("file", __name__)


@file_bp.get("/files/<path:relative_path>")
@login_required_context
def get_file(relative_path: str):
    path = FileService.resolve_relative_path(relative_path)
    return send_file(path)
