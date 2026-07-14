import mimetypes
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import current_app

from app.utils.error_code import BusinessError, ErrorCode
from app.utils.file_validator import validate_file_bytes


class FileService:
    @staticmethod
    def save_upload(file_storage, allowed_extensions: set[str], max_size: int):
        data = file_storage.read()
        file_storage.seek(0)
        extension = validate_file_bytes(file_storage.filename or "", data, allowed_extensions, max_size)
        now = datetime.now()
        relative_path = Path("uploads") / now.strftime("%Y") / now.strftime("%m") / now.strftime("%d") / f"{uuid4().hex}.{extension}"
        absolute_path = FileService.storage_root() / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_bytes(data)
        return {
            "relative_path": relative_path.as_posix(),
            "absolute_path": str(absolute_path),
            "file_size": len(data),
            "extension": extension,
            "mime_type": mimetypes.guess_type(file_storage.filename or "")[0],
        }

    @staticmethod
    def save_bytes(data: bytes, extension: str, result: bool = False):
        now = datetime.now()
        top_dir = "results" if result else "uploads"
        relative_path = Path(top_dir) / now.strftime("%Y") / now.strftime("%m") / now.strftime("%d") / f"{uuid4().hex}.{extension}"
        absolute_path = FileService.storage_root() / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_bytes(data)
        return relative_path.as_posix()

    @staticmethod
    def storage_root() -> Path:
        return Path(current_app.config["STORAGE_ROOT"])

    @staticmethod
    def resolve_relative_path(relative_path: str) -> Path:
        base = FileService.storage_root().resolve()
        target = (base / relative_path).resolve()
        if base not in target.parents and target != base:
            raise BusinessError(ErrorCode.NOT_FOUND, "文件不存在")
        if not target.exists() or not target.is_file():
            raise BusinessError(ErrorCode.NOT_FOUND, "文件不存在")
        return target
