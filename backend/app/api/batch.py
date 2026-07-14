import io

from flask import Blueprint, request, send_file

from app.middlewares.permission_middleware import permission_required
from app.schemas.batch_schema import BatchUploadSchema
from app.services.batch_service import BatchService
from app.utils.pagination import parse_pagination_args
from app.utils.response import success_response


batch_bp = Blueprint("batch", __name__)
batch_upload_schema = BatchUploadSchema()


@batch_bp.post("/batch/upload")
@permission_required("detection:batch:execute")
def upload_batch():
    payload = batch_upload_schema.load(request.form.to_dict() if request.form else {})
    files = request.files.getlist("files")
    if not files:
        single = request.files.get("file")
        if single is not None:
            files = [single]
    data = BatchService.submit_batch(payload["batch_name"], files, payload["confidence_threshold"])
    return success_response(data, "批量任务已提交")


@batch_bp.get("/batch/list")
@permission_required("detection:batch:list")
def list_batches():
    data = BatchService.list_batches(parse_pagination_args(request.args))
    return success_response(data)


@batch_bp.get("/batch/<int:batch_id>")
@permission_required("detection:batch:detail")
def get_batch(batch_id: int):
    data = BatchService.get_batch(batch_id)
    return success_response(data)


@batch_bp.get("/batch/<int:batch_id>/records")
@permission_required("detection:batch:detail")
def get_batch_records(batch_id: int):
    data = BatchService.get_batch_records(batch_id, parse_pagination_args(request.args))
    return success_response(data)


@batch_bp.get("/batch/<int:batch_id>/report")
@permission_required("detection:batch:download")
def download_batch_report(batch_id: int):
    content = BatchService.build_report(batch_id)
    return send_file(
        io.BytesIO(content),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"batch_{batch_id}_report.csv",
    )


@batch_bp.delete("/batch/<int:batch_id>")
@permission_required("detection:batch:delete")
def delete_batch(batch_id: int):
    BatchService.delete_batch(batch_id)
    return success_response({}, "删除成功")
