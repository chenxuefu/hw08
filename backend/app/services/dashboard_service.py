from datetime import datetime, timedelta

from sqlalchemy import func

from app.extensions import db
from app.models.detection_record import DetectionRecord
from app.models.detection_result import DetectionResult
from app.models.model_version import ModelVersion
from app.models.sys_user import SysUser


class DashboardService:
    @staticmethod
    def summary(filters):
        start_time, end_time = DashboardService.resolve_range(filters)
        total_detections = DetectionRecord.query.filter_by(is_deleted=0).count()
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = DetectionRecord.query.filter(
            DetectionRecord.is_deleted == 0,
            DetectionRecord.detection_time >= today_start,
        ).count()
        disease_count = DetectionResult.query.filter(
            DetectionResult.is_deleted == 0,
            DetectionResult.class_name != "healthy",
        ).count()
        active_model = ModelVersion.query.filter_by(is_deleted=0, is_active=1).first()
        active_map_50 = float(active_model.map_50) if active_model else 0
        return {
            "total_detections": total_detections,
            "total_records": total_detections,
            "today_detections": today_count,
            "today_records": today_count,
            "total_disease_count": disease_count,
            "current_model_map_50": active_map_50,
            "current_map_50": active_map_50,
            "model_version_code": active_model.version_code if active_model else None,
            "range_start": DashboardService.format_datetime(start_time),
            "range_end": DashboardService.format_datetime(end_time),
        }

    @staticmethod
    def class_distribution(filters):
        start_time, end_time = DashboardService.resolve_range(filters)
        query = (
            db.session.query(
                DetectionResult.class_name,
                DetectionResult.class_name_cn,
                func.count(DetectionResult.id).label("count"),
            )
            .join(DetectionRecord, DetectionRecord.id == DetectionResult.record_id)
            .filter(
                DetectionResult.is_deleted == 0,
                DetectionRecord.is_deleted == 0,
                DetectionRecord.detection_time >= start_time,
                DetectionRecord.detection_time <= end_time,
            )
            .group_by(DetectionResult.class_name, DetectionResult.class_name_cn)
            .order_by(func.count(DetectionResult.id).desc())
            .all()
        )
        return [
            {
                "class_name": row.class_name,
                "class_name_cn": row.class_name_cn,
                "count": row.count,
            }
            for row in query
        ]

    @staticmethod
    def trend(filters):
        start_time, end_time = DashboardService.resolve_range(filters)
        rows = (
            db.session.query(
                func.date(DetectionRecord.detection_time).label("day"),
                func.count(DetectionRecord.id).label("record_count"),
                func.coalesce(func.sum(DetectionRecord.total_detections), 0).label("detection_count"),
            )
            .filter(
                DetectionRecord.is_deleted == 0,
                DetectionRecord.detection_time >= start_time,
                DetectionRecord.detection_time <= end_time,
            )
            .group_by(func.date(DetectionRecord.detection_time))
            .order_by(func.date(DetectionRecord.detection_time).asc())
            .all()
        )
        return [
            {
                "date": str(row.day),
                "count": row.record_count,
                "record_count": row.record_count,
                "detection_count": int(row.detection_count or 0),
            }
            for row in rows
        ]

    @staticmethod
    def top_users(filters):
        start_time, end_time = DashboardService.resolve_range(filters)
        limit = min(max(int(filters.get("limit", 10)), 1), 20)
        rows = (
            db.session.query(
                DetectionRecord.user_id,
                SysUser.username,
                SysUser.real_name,
                func.count(DetectionRecord.id).label("count"),
            )
            .join(SysUser, SysUser.id == DetectionRecord.user_id)
            .filter(
                DetectionRecord.is_deleted == 0,
                DetectionRecord.detection_time >= start_time,
                DetectionRecord.detection_time <= end_time,
                SysUser.is_deleted == 0,
            )
            .group_by(DetectionRecord.user_id, SysUser.username, SysUser.real_name)
            .order_by(func.count(DetectionRecord.id).desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "user_id": row.user_id,
                "username": row.username,
                "real_name": row.real_name,
                "count": row.count,
            }
            for row in rows
        ]

    @staticmethod
    def resolve_range(filters):
        if filters.get("start_time") and filters.get("end_time"):
            start_time = datetime.strptime(filters["start_time"], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(filters["end_time"], "%Y-%m-%d %H:%M:%S")
            return start_time, end_time
        days = int(filters.get("days", 7))
        end_time = datetime.now()
        start_time = end_time - timedelta(days=max(days, 1) - 1)
        return start_time, end_time

    @staticmethod
    def format_datetime(value):
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")
