import html
from datetime import datetime

from flask import g

from app.extensions import db
from app.middlewares.log_middleware import write_audit_log
from app.services.file_service import FileService
from app.models.disease_info import DiseaseInfo
from app.utils.error_code import BusinessError, ErrorCode
from app.utils.pagination import build_page_data


class DiseaseService:
    @staticmethod
    def list_diseases(filters, pagination):
        query = DiseaseInfo.query.filter_by(is_deleted=0)
        if filters.get("keyword"):
            keyword = filters["keyword"]
            query = query.filter(
                db.or_(
                    DiseaseInfo.class_name.like(f"%{keyword}%"),
                    DiseaseInfo.chinese_name.like(f"%{keyword}%"),
                )
            )
        if filters.get("severity_level") not in (None, ""):
            query = query.filter(DiseaseInfo.severity_level == int(filters["severity_level"]))

        sort_map = {
            "create_time": DiseaseInfo.create_time,
            "severity_level": DiseaseInfo.severity_level,
            "class_name": DiseaseInfo.class_name,
        }
        order_column = sort_map.get(pagination["sort_field"], DiseaseInfo.create_time)
        if pagination["sort_order"] == "asc":
            query = query.order_by(order_column.asc(), DiseaseInfo.id.asc())
        else:
            query = query.order_by(order_column.desc(), DiseaseInfo.id.desc())

        total = query.count()
        items = (
            query.offset((pagination["page"] - 1) * pagination["page_size"])
            .limit(pagination["page_size"])
            .all()
        )
        data = [DiseaseService.serialize(item) for item in items]
        return build_page_data(data, total, pagination["page"], pagination["page_size"])

    @staticmethod
    def get_disease(disease_id: int):
        disease = DiseaseService.get_entity(disease_id)
        return DiseaseService.serialize(disease)

    @staticmethod
    def create_disease(payload, example_image):
        disease = DiseaseInfo.query.filter(DiseaseInfo.class_name == payload["class_name"]).first()
        if disease is not None and int(disease.is_deleted) == 0:
            raise BusinessError(ErrorCode.RESOURCE_EXISTS, "鐥呭绫诲埆宸插瓨鍦?")
        was_deleted = disease is not None and int(disease.is_deleted) == 1
        if disease is None:
            disease = DiseaseInfo(class_name=payload["class_name"], create_by=g.current_user.id, is_deleted=0)
            db.session.add(disease)
        disease.class_name = payload["class_name"]
        disease.chinese_name = html.escape(payload["chinese_name"])
        disease.alias = html.escape(payload.get("alias") or "") or None
        disease.symptom = html.escape(payload["symptom"])
        disease.cause = html.escape(payload["cause"])
        disease.prevention = html.escape(payload["prevention"])
        disease.severity_level = payload["severity_level"]
        disease.create_by = g.current_user.id
        disease.is_deleted = 0
        if example_image is not None:
            saved = FileService.save_upload(example_image, {"jpg", "jpeg", "png"}, 5 * 1024 * 1024)
            disease.example_image = saved["relative_path"]
        elif was_deleted:
            disease.example_image = None
        db.session.flush()
        write_audit_log("DISEASE", disease.id, "CREATE", None, DiseaseService.get_disease(disease.id))
        db.session.commit()
        return DiseaseService.get_disease(disease.id)

    @staticmethod
    def update_disease(disease_id: int, payload, example_image):
        disease = DiseaseService.get_entity(disease_id)
        before = DiseaseService.get_disease(disease_id)
        duplicate = DiseaseInfo.query.filter(
            DiseaseInfo.id != disease.id,
            DiseaseInfo.class_name == payload["class_name"],
            DiseaseInfo.is_deleted == 0,
        ).first()
        if duplicate is not None:
            raise BusinessError(ErrorCode.RESOURCE_EXISTS, "病害类别已存在")
        disease.class_name = payload["class_name"]
        disease.chinese_name = html.escape(payload["chinese_name"])
        disease.alias = html.escape(payload.get("alias") or "") or None
        disease.symptom = html.escape(payload["symptom"])
        disease.cause = html.escape(payload["cause"])
        disease.prevention = html.escape(payload["prevention"])
        disease.severity_level = payload["severity_level"]
        if example_image is not None:
            saved = FileService.save_upload(example_image, {"jpg", "jpeg", "png"}, 5 * 1024 * 1024)
            disease.example_image = saved["relative_path"]
        db.session.flush()
        after = DiseaseService.get_disease(disease.id)
        write_audit_log("DISEASE", disease.id, "UPDATE", before, after)
        db.session.commit()
        return after

    @staticmethod
    def delete_disease(disease_id: int):
        disease = DiseaseService.get_entity(disease_id)
        before = DiseaseService.get_disease(disease_id)
        disease.is_deleted = 1
        write_audit_log("DISEASE", disease.id, "DELETE", before, None)
        db.session.commit()
        return True

    @staticmethod
    def ensure_unique(class_name: str):
        exists = DiseaseInfo.query.filter_by(class_name=class_name, is_deleted=0).first()
        if exists is not None:
            raise BusinessError(ErrorCode.RESOURCE_EXISTS, "病害类别已存在")

    @staticmethod
    def get_entity(disease_id: int):
        disease = DiseaseInfo.query.filter_by(id=disease_id, is_deleted=0).first()
        if disease is None:
            raise BusinessError(ErrorCode.DISEASE_NOT_FOUND)
        return disease

    @staticmethod
    def serialize(disease: DiseaseInfo):
        image_url = f"/api/v1/files/{disease.example_image}" if disease.example_image else None
        return {
            "id": disease.id,
            "class_name": disease.class_name,
            "chinese_name": disease.chinese_name,
            "alias": disease.alias,
            "symptom": disease.symptom,
            "cause": disease.cause,
            "prevention": disease.prevention,
            "example_image": disease.example_image,
            "example_image_url": image_url,
            "severity_level": int(disease.severity_level),
            "create_by": disease.create_by,
            "create_time": DiseaseService.format_datetime(disease.create_time),
            "update_time": DiseaseService.format_datetime(disease.update_time),
        }

    @staticmethod
    def format_datetime(value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value
