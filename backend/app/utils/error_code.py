from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class ErrorDefinition:
    code: int
    message: str
    http_status: int


class BusinessError(Exception):
    def __init__(self, error_code, message: str | None = None, data=None):
        super().__init__(message or error_code.message)
        self.error_code = error_code
        self.message = message or error_code.message
        self.data = {} if data is None else data


class ErrorCode(Enum):
    SUCCESS = ErrorDefinition(0, "操作成功", 200)
    PARAM_ERROR = ErrorDefinition(1000, "请求参数错误", 400)
    VALIDATION_ERROR = ErrorDefinition(1001, "参数校验失败", 400)
    FILE_TYPE_ERROR = ErrorDefinition(1002, "文件格式不支持", 400)
    FILE_SIZE_ERROR = ErrorDefinition(1003, "文件大小超限", 400)
    UNAUTHORIZED = ErrorDefinition(2000, "未登录或 Token 失效", 401)
    TOKEN_EXPIRED = ErrorDefinition(2001, "Token 已过期", 401)
    TOKEN_INVALID = ErrorDefinition(2002, "Token 非法", 401)
    LOGIN_FAILED = ErrorDefinition(2003, "账号或密码错误", 401)
    ACCOUNT_DISABLED = ErrorDefinition(2004, "账号被禁用", 401)
    FORBIDDEN = ErrorDefinition(3000, "无权限访问", 403)
    DATA_FORBIDDEN = ErrorDefinition(3001, "数据权限不足", 403)
    NOT_FOUND = ErrorDefinition(4000, "资源不存在", 404)
    USER_NOT_FOUND = ErrorDefinition(4001, "用户不存在", 404)
    DETECTION_NOT_FOUND = ErrorDefinition(4002, "检测记录不存在", 404)
    DISEASE_NOT_FOUND = ErrorDefinition(4003, "病害记录不存在", 404)
    RESOURCE_EXISTS = ErrorDefinition(5000, "资源已存在", 409)
    SERVER_ERROR = ErrorDefinition(6000, "服务器内部错误", 500)
    MODEL_INFERENCE_ERROR = ErrorDefinition(6001, "模型推理失败", 500)
    DATABASE_ERROR = ErrorDefinition(6002, "数据库异常", 500)
    FILE_STORAGE_ERROR = ErrorDefinition(6003, "文件存储失败", 500)

    @property
    def code(self) -> int:
        return self.value.code

    @property
    def message(self) -> str:
        return self.value.message

    @property
    def http_status(self) -> int:
        return self.value.http_status
