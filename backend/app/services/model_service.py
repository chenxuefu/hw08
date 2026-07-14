from datetime import datetime
from decimal import Decimal

from flask import g

from app.extensions import db
from app.middlewares.log_middleware import write_audit_log
from app.models.model_version import ModelVersion
from app.utils.error_code import BusinessError, ErrorCode
from app.utils.pagination import build_page_data


class ModelService:
    @staticmethod
    def list_versions(filters, pagination):
        query = ModelVersion.query.filter_by(is_deleted=0)
        if filters.get("version_code"):
            query = query.filter(ModelVersion.version_code.like(f"%{filters['version_code']}%"))
        if filters.get("is_active") not in (None, ""):
            query = query.filter(ModelVersion.is_active == int(filters["is_active"]))

        sort_map = {
            "create_time": ModelVersion.create_time,
            "version_code": ModelVersion.version_code,
            "is_active": ModelVersion.is_active,
        }
        order_column = sort_map.get(pagination["sort_field"], ModelVersion.create_time)
        if pagination["sort_order"] == "asc":
            query = query.order_by(order_column.asc(), ModelVersion.id.asc())
        else:
            query = query.order_by(order_column.desc(), ModelVersion.id.desc())
        total = query.count()
        items = (
            query.offset((pagination["page"] - 1) * pagination["page_size"])
            .limit(pagination["page_size"])
            .all()
        )
        data = [ModelService.serialize(item) for item in items]
        return build_page_data(data, total, pagination["page"], pagination["page_size"])

    @staticmethod
    def get_version(version_id: int):
        version = ModelService.get_entity(version_id)
        return ModelService.serialize(version)

    @staticmethod
    def create_version(payload):
        ModelService.ensure_unique(payload["version_code"])
        version = ModelVersion(
            version_code=payload["version_code"],
            model_name=payload["model_name"],
            weight_path=payload["weight_path"],
            map_50=payload.get("map_50", 0),
            map_50_95=payload.get("map_50_95", 0),
            precision_rate=payload.get("precision_rate", 0),
            recall_rate=payload.get("recall_rate", 0),
            is_active=0,
            description=payload.get("description"),
            create_by=g.current_user.id,
            is_deleted=0,
        )
        db.session.add(version)
        db.session.flush()
        write_audit_log("MODEL", version.id, "CREATE", None, ModelService.get_version(version.id))
        db.session.commit()
        return ModelService.get_version(version.id)

    @staticmethod
    def update_version(version_id: int, payload):
        version = ModelService.get_entity(version_id)
        before = ModelService.get_version(version_id)
        duplicate = ModelVersion.query.filter(
            ModelVersion.id != version.id,
            ModelVersion.version_code == payload["version_code"],
            ModelVersion.is_deleted == 0,
        ).first()
        if duplicate is not None:
            raise BusinessError(ErrorCode.RESOURCE_EXISTS, "版本号已存在")
        version.version_code = payload["version_code"]
        version.model_name = payload["model_name"]
        version.weight_path = payload["weight_path"]
        version.map_50 = payload.get("map_50", version.map_50)
        version.map_50_95 = payload.get("map_50_95", version.map_50_95)
        version.precision_rate = payload.get("precision_rate", version.precision_rate)
        version.recall_rate = payload.get("recall_rate", version.recall_rate)
        version.description = payload.get("description")
        if "is_active" in payload:
            version.is_active = payload["is_active"]
        db.session.flush()
        after = ModelService.get_version(version.id)
        write_audit_log("MODEL", version.id, "UPDATE", before, after)
        db.session.commit()
        return after

    @staticmethod
    def activate_version(version_id: int):
        version = ModelService.get_entity(version_id)
        before = ModelService.get_version(version_id)
        db.session.query(ModelVersion).filter(ModelVersion.is_deleted == 0).update({"is_active": 0})
        version.is_active = 1
        db.session.flush()
        after = ModelService.get_version(version.id)
        write_audit_log("MODEL", version.id, "UPDATE", before, after)
        db.session.commit()
        return after

    @staticmethod
    def delete_version(version_id: int):
        version = ModelService.get_entity(version_id)
        before = ModelService.get_version(version_id)
        version.is_deleted = 1
        if int(version.is_active) == 1:
            version.is_active = 0
        write_audit_log("MODEL", version.id, "DELETE", before, None)
        db.session.commit()
        return True

    @staticmethod
    def get_active_version():
        version = ModelVersion.query.filter_by(is_deleted=0, is_active=1).order_by(ModelVersion.id.desc()).first()
        if version is None:
            raise BusinessError(ErrorCode.NOT_FOUND, "当前模型版本不存在")
        return version

    @staticmethod
    def ensure_unique(version_code: str):
        exists = ModelVersion.query.filter_by(version_code=version_code, is_deleted=0).first()
        if exists is not None:
            raise BusinessError(ErrorCode.RESOURCE_EXISTS, "版本号已存在")

    @staticmethod
    def get_entity(version_id: int):
        version = ModelVersion.query.filter_by(id=version_id, is_deleted=0).first()
        if version is None:
            raise BusinessError(ErrorCode.NOT_FOUND, "模型版本不存在")
        return version

    @staticmethod
    def serialize(version: ModelVersion):
        return {
            "id": version.id,
            "version_code": version.version_code,
            "model_name": version.model_name,
            "weight_path": version.weight_path,
            "map_50": ModelService.decimal_to_float(version.map_50),
            "map_50_95": ModelService.decimal_to_float(version.map_50_95),
            "precision_rate": ModelService.decimal_to_float(version.precision_rate),
            "recall_rate": ModelService.decimal_to_float(version.recall_rate),
            "is_active": int(version.is_active),
            "description": version.description,
            "create_by": version.create_by,
            "create_time": ModelService.format_datetime(version.create_time),
            "update_time": ModelService.format_datetime(version.update_time),
        }

    @staticmethod
    def decimal_to_float(value):
        if isinstance(value, Decimal):
            return float(value)
        return value

    @staticmethod
    def format_datetime(value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value
