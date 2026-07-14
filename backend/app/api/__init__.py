from app.api.auth import auth_bp
from app.api.batch import batch_bp
from app.api.dashboard import dashboard_bp
from app.api.detection import detection_bp
from app.api.disease import disease_bp
from app.api.file import file_bp
from app.api.log import log_bp
from app.api.menu import menu_bp
from app.api.model_version import model_version_bp
from app.api.role import role_bp
from app.api.user import user_bp


def register_blueprints(app) -> None:
    app.register_blueprint(auth_bp, url_prefix="/api/v1")
    app.register_blueprint(detection_bp, url_prefix="/api/v1")
    app.register_blueprint(batch_bp, url_prefix="/api/v1")
    app.register_blueprint(user_bp, url_prefix="/api/v1")
    app.register_blueprint(role_bp, url_prefix="/api/v1")
    app.register_blueprint(menu_bp, url_prefix="/api/v1")
    app.register_blueprint(dashboard_bp, url_prefix="/api/v1")
    app.register_blueprint(model_version_bp, url_prefix="/api/v1")
    app.register_blueprint(log_bp, url_prefix="/api/v1")
    app.register_blueprint(disease_bp, url_prefix="/api/v1")
    app.register_blueprint(file_bp, url_prefix="/api/v1")
