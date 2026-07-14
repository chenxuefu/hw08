import csv
import io
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from flask import g

from app.extensions import db
from app.middlewares.permission_middleware import apply_data_scope
from app.models.detection_batch import DetectionBatch
from app.models.detection_record import DetectionRecord
from app.services.detection_service import DetectionService
from app.services.file_service import FileService
from app.utils.error_code import BusinessError, ErrorCode
from app.utils.file_validator import validate_file_bytes
from app.utils.pagination import build_page_data


class BatchService:
    _executor = None
    _lock = threading.Lock()
    _app = None

    @classmethod
    def init_app(cls, app):
        with cls._lock:
            if cls._executor is None:
                cls._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="wheat-batch")
            cls._app = app

    @classmethod
    def submit_batch(cls, batch_name: str, files, confidence_threshold: float):
        tasks = cls.normalize_input_files(files)
        batch = DetectionBatch(
            user_id=g.current_user.id,
            batch_name=batch_name,
            total_images=len(tasks),
            processed_images=0,
            success_images=0,
            failed_images=0,
            status=0,
            is_deleted=0,
        )
        db.session.add(batch)
        db.session.commit()
        if cls._executor is None or cls._app is None:
            raise BusinessError(ErrorCode.SERVER_ERROR, "批量任务执行器未初始化")
        cls._executor.submit(cls.process_batch, batch.id, g.current_user.id, tasks, confidence_threshold)
        return cls.get_batch(batch.id)

    @classmethod
    def process_batch(cls, batch_id: int, user_id: int, tasks: list[dict], confidence_threshold: float):
        with cls._app.app_context():
            batch = DetectionBatch.query.get(batch_id)
            if batch is None or int(batch.is_deleted) == 1:
                return
            batch.status = 1
            batch.start_time = datetime.now()
            db.session.commit()
            success_count = 0
            failed_count = 0
            for item in tasks:
                result = DetectionService.detect_saved_image(
                    user_id=user_id,
                    relative_path=item["relative_path"],
                    image_name=item["image_name"],
                    image_size_bytes=item["image_size"],
                    confidence_threshold=confidence_threshold,
                    batch_id=batch.id,
                    raise_on_error=False,
                )
                batch.processed_images += 1
                if result is None:
                    failed_count += 1
                else:
                    success_count += 1
                batch.success_images = success_count
                batch.failed_images = failed_count
                db.session.commit()
            batch.end_time = datetime.now()
            if success_count == len(tasks):
                batch.status = 2
            elif success_count > 0:
                batch.status = 3
            else:
                batch.status = 4
            db.session.commit()

    @classmethod
    def list_batches(cls, pagination):
        query = DetectionBatch.query.filter_by(is_deleted=0)
        query = apply_data_scope(query, DetectionBatch.user_id)
        sort_map = {
            "create_time": DetectionBatch.create_time,
            "status": DetectionBatch.status,
            "batch_name": DetectionBatch.batch_name,
        }
        order_column = sort_map.get(pagination["sort_field"], DetectionBatch.create_time)
        if pagination["sort_order"] == "asc":
            query = query.order_by(order_column.asc(), DetectionBatch.id.asc())
        else:
            query = query.order_by(order_column.desc(), DetectionBatch.id.desc())
        total = query.count()
        items = (
            query.offset((pagination["page"] - 1) * pagination["page_size"])
            .limit(pagination["page_size"])
            .all()
        )
        data = [cls.serialize_batch(item) for item in items]
        return build_page_data(data, total, pagination["page"], pagination["page_size"])

    @classmethod
    def get_batch(cls, batch_id: int):
        batch = DetectionBatch.query.filter_by(id=batch_id, is_deleted=0).first()
        if batch is None:
            raise BusinessError(ErrorCode.NOT_FOUND, "批量任务不存在")
        cls.ensure_batch_access(batch)
        return cls.serialize_batch(batch)

    @classmethod
    def get_batch_records(cls, batch_id: int, pagination):
        cls.get_batch(batch_id)
        return DetectionService.list_records({}, pagination, batch_id=batch_id)

    @classmethod
    def delete_batch(cls, batch_id: int):
        batch = DetectionBatch.query.filter_by(id=batch_id, is_deleted=0).first()
        if batch is None:
            raise BusinessError(ErrorCode.NOT_FOUND, "批量任务不存在")
        cls.ensure_batch_access(batch)
        batch.is_deleted = 1
        db.session.query(DetectionRecord).filter(
            DetectionRecord.batch_id == batch.id,
            DetectionRecord.is_deleted == 0,
        ).update({"is_deleted": 1})
        db.session.commit()
        return True

    @classmethod
    def build_report(cls, batch_id: int):
        cls.get_batch(batch_id)
        records = (
            DetectionRecord.query.filter_by(batch_id=batch_id, is_deleted=0)
            .order_by(DetectionRecord.id.asc())
            .all()
        )
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["record_id", "image_name", "status", "total_detections", "avg_confidence", "inference_time_ms", "error_message"])
        for record in records:
            writer.writerow(
                [
                    record.id,
                    record.image_name,
                    record.status,
                    record.total_detections,
                    float(record.avg_confidence),
                    record.inference_time_ms,
                    record.error_message or "",
                ]
            )
        return buffer.getvalue().encode("utf-8-sig")

    @classmethod
    def ensure_batch_access(cls, batch: DetectionBatch):
        role = g.current_role
        user = g.current_user
        if role.data_scope == "DATA_SELF" and batch.user_id != user.id:
            raise BusinessError(ErrorCode.DATA_FORBIDDEN)

    @classmethod
    def serialize_batch(cls, batch: DetectionBatch):
        return {
            "id": batch.id,
            "user_id": batch.user_id,
            "batch_name": batch.batch_name,
            "total_images": batch.total_images,
            "processed_images": batch.processed_images,
            "success_images": batch.success_images,
            "failed_images": batch.failed_images,
            "status": int(batch.status),
            "start_time": cls.format_datetime(batch.start_time),
            "end_time": cls.format_datetime(batch.end_time),
            "create_time": cls.format_datetime(batch.create_time),
            "update_time": cls.format_datetime(batch.update_time),
        }

    @classmethod
    def normalize_input_files(cls, files):
        file_list = [item for item in files if item and item.filename]
        if not file_list:
            raise BusinessError(ErrorCode.PARAM_ERROR, "请上传图片或 ZIP 文件")
        if len(file_list) == 1 and Path(file_list[0].filename).suffix.lower() == ".zip":
            return cls.extract_zip_tasks(file_list[0])
        if len(file_list) > 500:
            raise BusinessError(ErrorCode.PARAM_ERROR, "单批次图片数不能超过 500")
        tasks = []
        for file_storage in file_list:
            saved = FileService.save_upload(file_storage, {"jpg", "jpeg", "png", "bmp"}, 10 * 1024 * 1024)
            tasks.append(
                {
                    "relative_path": saved["relative_path"],
                    "image_name": file_storage.filename or Path(saved["relative_path"]).name,
                    "image_size": saved["file_size"],
                }
            )
        return tasks

    @classmethod
    def extract_zip_tasks(cls, file_storage):
        data = file_storage.read()
        file_storage.seek(0)
        validate_file_bytes(file_storage.filename or "", data, {"zip"}, 200 * 1024 * 1024)
        try:
            archive = zipfile.ZipFile(io.BytesIO(data))
        except zipfile.BadZipFile as exc:
            raise BusinessError(ErrorCode.FILE_TYPE_ERROR) from exc
        tasks = []
        for info in archive.infolist():
            if info.is_dir():
                continue
            raw = archive.read(info)
            ext = validate_file_bytes(info.filename, raw, {"jpg", "jpeg", "png", "bmp"}, 10 * 1024 * 1024)
            relative_path = FileService.save_bytes(raw, ext, result=False)
            tasks.append(
                {
                    "relative_path": relative_path,
                    "image_name": Path(info.filename).name,
                    "image_size": len(raw),
                }
            )
            if len(tasks) > 500:
                raise BusinessError(ErrorCode.PARAM_ERROR, "单批次图片数不能超过 500")
        if not tasks:
            raise BusinessError(ErrorCode.PARAM_ERROR, "ZIP 中没有可用图片")
        return tasks

    @classmethod
    def format_datetime(cls, value):
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")


def init_batch_worker(app):
    BatchService.init_app(app)
