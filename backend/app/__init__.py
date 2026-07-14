from flask import Flask
from marshmallow import ValidationError

from app.api import register_blueprints
from app.config import config_mapping
from app.extensions import init_extensions
from app.services.batch_service import init_batch_worker
from app.services.auth_service import register_jwt_callbacks
from app.middlewares.log_middleware import register_request_logging
from app.utils.error_code import BusinessError, ErrorCode
from app.utils.response import error_response


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_mapping[config_name or "development"])
    init_extensions(app)
    register_jwt_callbacks()
    register_blueprints(app)
    init_batch_worker(app)
    register_request_logging(app)
    register_error_handlers(app)
    return app


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(BusinessError)
    def handle_business_error(error: BusinessError):
        return error_response(error.error_code, message=error.message, data=error.data)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        return error_response(ErrorCode.VALIDATION_ERROR, data=error.messages)

    @app.errorhandler(404)
    def handle_not_found(_error):
        return error_response(ErrorCode.NOT_FOUND)

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return error_response(ErrorCode.PARAM_ERROR, message="请求方法不支持")

    @app.errorhandler(500)
    def handle_internal_error(_error):
        return error_response(ErrorCode.SERVER_ERROR)
