from pathlib import Path

from app.utils.error_code import BusinessError, ErrorCode


MAGIC_HEADERS = {
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "png": [b"\x89PNG\r\n\x1a\n"],
    "bmp": [b"BM"],
    "zip": [b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"],
}


def validate_file_bytes(filename: str, data: bytes, allowed_extensions: set[str], max_size: int):
    extension = Path(filename).suffix.lower().lstrip(".")
    if extension not in allowed_extensions:
        raise BusinessError(ErrorCode.FILE_TYPE_ERROR)
    if len(data) > max_size:
        raise BusinessError(ErrorCode.FILE_SIZE_ERROR)
    headers = MAGIC_HEADERS.get(extension, [])
    if not headers or not any(data.startswith(header) for header in headers):
        raise BusinessError(ErrorCode.FILE_TYPE_ERROR)
    return extension
