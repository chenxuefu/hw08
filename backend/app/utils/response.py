from datetime import datetime

from flask import jsonify

from app.utils.error_code import ErrorCode


def current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def success_response(data=None, message: str = "操作成功", http_status: int = 200):
    payload = {
        "code": ErrorCode.SUCCESS.code,
        "message": message,
        "data": {} if data is None else data,
        "timestamp": current_timestamp(),
    }
    response = jsonify(payload)
    response.status_code = http_status
    return response


def error_response(error_code: ErrorCode, message: str | None = None, data=None):
    payload = {
        "code": error_code.code,
        "message": message or error_code.message,
        "data": {} if data is None else data,
        "timestamp": current_timestamp(),
    }
    response = jsonify(payload)
    response.status_code = error_code.http_status
    return response
