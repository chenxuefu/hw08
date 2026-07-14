import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "wheat-pest-secret-key-2026-backend-service")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "wheat-pest-jwt-secret-key-2026-backend-service")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_ERROR_MESSAGE_KEY = "message"
    JWT_TOKEN_LOCATION = ["headers", "query_string"]
    JWT_QUERY_STRING_NAME = "access_token"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        "mysql+pymysql://root:123456@127.0.0.1:3306/wheat_pest_db?charset=utf8mb4",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BCRYPT_LOG_ROUNDS = 12
    JSON_AS_ASCII = False
    PROPAGATE_EXCEPTIONS = True
    CORS_ORIGINS = [item.strip() for item in os.getenv("CORS_ORIGINS", "http://127.0.0.1:8080,http://localhost:8080").split(",") if item.strip()]
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024
    STORAGE_ROOT = BASE_DIR / "storage"
    UPLOAD_ROOT = STORAGE_ROOT / "uploads"
    RESULT_ROOT = STORAGE_ROOT / "results"
    LOG_ROOT = STORAGE_ROOT / "logs"
    ACTIVE_MODEL_CACHE_SECONDS = 30
    RTDETR_BASE_MODEL = os.getenv("RTDETR_BASE_MODEL", "PekingU/rtdetr_r50vd")


class DevelopmentConfig(BaseConfig):
    DEBUG = False
    TESTING = False


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite+pysqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False


config_mapping = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
