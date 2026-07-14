from datetime import datetime
from pathlib import Path

from flask import g
from PIL import UnidentifiedImageError

from app.core.image_io import image_size
from app.core.rtdetr_detector import RTDETRDetector
from app.core.visualizer import draw_detections
from app.extensions import db
from app.middlewares.permission_middleware import apply_data_scope
from app.models.detection_record import DetectionRecord
from app.models.detection_result import DetectionResult
from app.models.model_version import ModelVersion
from app.models.sys_user import SysUser
from app.services.file_service import FileService
from app.services.model_service import ModelService
from app.utils.constants import CLASS_NAME_TO_CN
from app.utils.error_code import BusinessError, ErrorCode
from app.utils.pagination import build_page_data


class DetectionService:
    @staticmethod
    def single_detect(file_storage, confidence_threshold: float):
        saved = FileService.save_upload(file_storage, {"jpg", "jpeg", "png", "bmp"}, 10 * 1024 * 1024)
        return DetectionService.detect_saved_image(
            user_id=g.current_user.id,
            relative_path=saved["relative_path"],
            image_name=file_storage.filename or Path(saved["relative_path"]).name,
            image_size_bytes=saved["file_size"],
            confidence_threshold=confidence_threshold,
            batch_id=None,
            raise_on_error=True,
        )

    @staticmethod
    def detect_saved_image(
        user_id: int,
        relative_path: str,
        image_name: str,
        image_size_bytes: int,
        confidence_threshold: float,
        batch_id=None,
        raise_on_error: bool = True,
    ):
        absolute_path = FileService.resolve_relative_path(relative_path)
        try:
            width, height = image_size(absolute_path)
        except UnidentifiedImageError as exc:
            raise BusinessError(ErrorCode.FILE_TYPE_ERROR) from exc

        active_model = ModelService.get_active_version()
        record = DetectionRecord(
            user_id=user_id,
            batch_id=batch_id,
            image_path=relative_path,
            image_name=image_name,
            image_size=image_size_bytes,
            image_width=width,
            image_height=height,
            total_detections=0,
            avg_confidence=0,
            inference_time_ms=0,
            model_version_id=active_model.id,
            status=0,
            is_deleted=0,
        )
        db.session.add(record)
        db.session.flush()
        try:
            output = RTDETRDetector.predict(str(absolute_path), confidence_threshold)
            results = output["results"]
            extension = Path(image_name).suffix.lower().lstrip(".") or "jpg"
            result_bytes = draw_detections(absolute_path, results, extension=extension)
            result_image_path = FileService.save_bytes(result_bytes, extension if extension in {"jpg", "jpeg", "png", "bmp"} else "jpg", result=True)
            for item in results:
                db.session.add(
                    DetectionResult(
                        record_id=record.id,
                        class_id=item["class_id"],
                        class_name=item["class_name"],
                        class_name_cn=item["class_name_cn"],
                        confidence=item["confidence"],
                        bbox_x=item["bbox_x"],
                        bbox_y=item["bbox_y"],
                        bbox_w=item["bbox_w"],
                        bbox_h=item["bbox_h"],
                        is_deleted=0,
                    )
                )
            record.result_image_path = result_image_path
            record.total_detections = len(results)
            record.avg_confidence = round(sum(item["confidence"] for item in results) / len(results), 4) if results else 0
            record.inference_time_ms = output["inference_time_ms"]
            record.status = 1
            record.error_message = None
            db.session.commit()
            return DetectionService.serialize_single_result(record, results)
        except BusinessError as error:
            record.status = 2
            record.error_message = error.message
            db.session.commit()
            if raise_on_error:
                raise error
            return None
        except Exception as error:
            record.status = 2
            record.error_message = str(error)
            db.session.commit()
            wrapped = BusinessError(ErrorCode.MODEL_INFERENCE_ERROR, "模型推理失败")
            if raise_on_error:
                raise wrapped from error
            return None

    @staticmethod
    def list_records(filters, pagination, batch_id=None):
        query = (
            db.session.query(DetectionRecord, SysUser.username)
            .join(SysUser, SysUser.id == DetectionRecord.user_id)
            .filter(DetectionRecord.is_deleted == 0, SysUser.is_deleted == 0)
        )
        query = apply_data_scope(query, DetectionRecord.user_id)
        if batch_id is not None:
            query = query.filter(DetectionRecord.batch_id == batch_id)
        if filters.get("username"):
            query = query.filter(SysUser.username.like(f"%{filters['username']}%"))
        if filters.get("status") not in (None, ""):
            query = query.filter(DetectionRecord.status == int(filters["status"]))
        if filters.get("start_time"):
            query = query.filter(DetectionRecord.detection_time >= datetime.strptime(filters["start_time"], "%Y-%m-%d %H:%M:%S"))
        if filters.get("end_time"):
            query = query.filter(DetectionRecord.detection_time <= datetime.strptime(filters["end_time"], "%Y-%m-%d %H:%M:%S"))
        if filters.get("class_name"):
            class_name = filters["class_name"]
            class_name = DetectionService.normalize_class_name(class_name)
            query = query.join(
                DetectionResult,
                db.and_(
                    DetectionResult.record_id == DetectionRecord.id,
                    DetectionResult.is_deleted == 0,
                    DetectionResult.class_name == class_name,
                ),
            )
        sort_map = {
            "create_time": DetectionRecord.create_time,
            "detection_time": DetectionRecord.detection_time,
            "status": DetectionRecord.status,
            "total_detections": DetectionRecord.total_detections,
        }
        order_column = sort_map.get(pagination["sort_field"], DetectionRecord.create_time)
        if pagination["sort_order"] == "asc":
            query = query.order_by(order_column.asc(), DetectionRecord.id.asc())
        else:
            query = query.order_by(order_column.desc(), DetectionRecord.id.desc())
        total = query.count()
        rows = (
            query.offset((pagination["page"] - 1) * pagination["page_size"])
            .limit(pagination["page_size"])
            .all()
        )
        data = [DetectionService.serialize_record_item(record, username) for record, username in rows]
        return build_page_data(data, total, pagination["page"], pagination["page_size"])

    @staticmethod
    def get_record(record_id: int):
        row = (
            db.session.query(DetectionRecord, SysUser.username)
            .join(SysUser, SysUser.id == DetectionRecord.user_id)
            .filter(DetectionRecord.id == record_id, DetectionRecord.is_deleted == 0, SysUser.is_deleted == 0)
            .first()
        )
        if row is None:
            raise BusinessError(ErrorCode.DETECTION_NOT_FOUND)
        record, username = row
        DetectionService.ensure_record_access(record)
        results = (
            DetectionResult.query.filter_by(record_id=record.id, is_deleted=0)
            .order_by(DetectionResult.confidence.desc(), DetectionResult.id.asc())
            .all()
        )
        payload = DetectionService.serialize_record_item(record, username)
        version = None
        if record.model_version_id:
            version = ModelVersion.query.filter_by(id=record.model_version_id, is_deleted=0).first()
        payload["results"] = [DetectionService.serialize_result_item(item) for item in results]
        payload["image_url"] = f"/api/v1/files/{record.image_path}" if record.image_path else None
        payload["result_image_url"] = f"/api/v1/detection/records/{record.id}/download" if record.result_image_path else None
        payload["version_code"] = version.version_code if version else None
        return payload

    @staticmethod
    def delete_record(record_id: int):
        record = DetectionRecord.query.filter_by(id=record_id, is_deleted=0).first()
        if record is None:
            raise BusinessError(ErrorCode.DETECTION_NOT_FOUND)
        DetectionService.ensure_record_access(record, delete=True)
        record.is_deleted = 1
        db.session.query(DetectionResult).filter(
            DetectionResult.record_id == record.id,
            DetectionResult.is_deleted == 0,
        ).update({"is_deleted": 1})
        db.session.commit()
        return True

    @staticmethod
    def get_result_image_path(record_id: int):
        record = DetectionRecord.query.filter_by(id=record_id, is_deleted=0).first()
        if record is None:
            raise BusinessError(ErrorCode.DETECTION_NOT_FOUND)
        DetectionService.ensure_record_access(record)
        if not record.result_image_path:
            raise BusinessError(ErrorCode.NOT_FOUND, "结果图不存在")
        return FileService.resolve_relative_path(record.result_image_path)

    @staticmethod
    def ensure_record_access(record: DetectionRecord, delete: bool = False):
        role = g.current_role
        user = g.current_user
        if role.data_scope == "DATA_SELF" and record.user_id != user.id:
            raise BusinessError(ErrorCode.DATA_FORBIDDEN)
        if delete and role.data_scope == "DATA_SELF" and record.user_id != user.id:
            raise BusinessError(ErrorCode.DATA_FORBIDDEN)

    @staticmethod
    def serialize_single_result(record: DetectionRecord, results: list[dict]):
        return {
            "record_id": record.id,
            "image_name": record.image_name,
            "image_width": record.image_width,
            "image_height": record.image_height,
            "total_detections": record.total_detections,
            "avg_confidence": float(record.avg_confidence),
            "inference_time_ms": record.inference_time_ms,
            "result_image_url": f"/api/v1/detection/records/{record.id}/download" if record.result_image_path else None,
            "results": results,
        }

    @staticmethod
    def serialize_record_item(record: DetectionRecord, username: str):
        return {
            "id": record.id,
            "user_id": record.user_id,
            "username": username,
            "batch_id": record.batch_id,
            "image_name": record.image_name,
            "image_size": record.image_size,
            "image_width": record.image_width,
            "image_height": record.image_height,
            "image_path": record.image_path,
            "image_url": f"/api/v1/files/{record.image_path}" if record.image_path else None,
            "result_image_path": record.result_image_path,
            "result_image_url": f"/api/v1/detection/records/{record.id}/download" if record.result_image_path else None,
            "model_version_id": record.model_version_id,
            "total_detections": record.total_detections,
            "avg_confidence": float(record.avg_confidence),
            "inference_time_ms": record.inference_time_ms,
            "status": int(record.status),
            "error_message": record.error_message,
            "detection_time": DetectionService.format_datetime(record.detection_time),
            "create_time": DetectionService.format_datetime(record.create_time),
        }

    @staticmethod
    def serialize_result_item(item: DetectionResult):
        return {
            "id": item.id,
            "class_id": item.class_id,
            "class_name": item.class_name,
            "class_name_cn": item.class_name_cn,
            "confidence": float(item.confidence),
            "bbox_x": float(item.bbox_x),
            "bbox_y": float(item.bbox_y),
            "bbox_w": float(item.bbox_w),
            "bbox_h": float(item.bbox_h),
        }

    @staticmethod
    def normalize_class_name(value: str):
        if value in CLASS_NAME_TO_CN:
            return value
        reverse = {label: code for code, label in CLASS_NAME_TO_CN.items()}
        return reverse.get(value, value)

    @staticmethod
    def format_datetime(value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value
