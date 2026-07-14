from flask import Blueprint, request, send_file

from app.middlewares.permission_middleware import permission_required
from app.schemas.detection_schema import DetectionSingleSchema
from app.services.detection_service import DetectionService
from app.utils.pagination import parse_pagination_args
from app.utils.response import success_response


detection_bp = Blueprint("detection", __name__)
detection_single_schema = DetectionSingleSchema()


@detection_bp.post("/detection/single")
@permission_required("detection:single:execute")
def single_detection():
    payload = detection_single_schema.load(request.form.to_dict() if request.form else {})
    image_file = request.files.get("file")
    if image_file is None:
        from app.utils.error_code import BusinessError, ErrorCode

        raise BusinessError(ErrorCode.PARAM_ERROR, "请上传图片文件")
    data = DetectionService.single_detect(image_file, payload["confidence_threshold"])
    return success_response(data, "检测完成")


@detection_bp.get("/detection/records")
@permission_required("detection:record:list")
def list_detection_records():
    pagination = parse_pagination_args(request.args)
    filters = {
        "username": request.args.get("username"),
        "class_name": request.args.get("class_name"),
        "status": request.args.get("status"),
        "start_time": request.args.get("start_time"),
        "end_time": request.args.get("end_time"),
    }
    data = DetectionService.list_records(filters, pagination)
    return success_response(data)


@detection_bp.get("/detection/records/<int:record_id>")
@permission_required("detection:record:detail")
def get_detection_record(record_id: int):
    data = DetectionService.get_record(record_id)
    return success_response(data)


@detection_bp.delete("/detection/records/<int:record_id>")
@permission_required("detection:record:delete")
def delete_detection_record(record_id: int):
    DetectionService.delete_record(record_id)
    return success_response({}, "删除成功")


@detection_bp.get("/detection/records/<int:record_id>/download")
@permission_required("detection:record:download")
def download_detection_result(record_id: int):
    path = DetectionService.get_result_image_path(record_id)
    return send_file(path, as_attachment=True, download_name=path.name)
