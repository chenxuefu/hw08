from flask import Blueprint, request

from app.middlewares.permission_middleware import permission_required
from app.schemas.model_version_schema import ModelVersionCreateSchema, ModelVersionUpdateSchema
from app.services.model_service import ModelService
from app.utils.pagination import parse_pagination_args
from app.utils.response import success_response


model_version_bp = Blueprint("model_version", __name__)
model_version_create_schema = ModelVersionCreateSchema()
model_version_update_schema = ModelVersionUpdateSchema()


@model_version_bp.get("/model-versions")
@permission_required("model:list")
def list_model_versions():
    pagination = parse_pagination_args(request.args)
    filters = {
        "version_code": request.args.get("version_code"),
        "is_active": request.args.get("is_active"),
    }
    data = ModelService.list_versions(filters, pagination)
    return success_response(data)


@model_version_bp.get("/model-versions/<int:version_id>")
@permission_required("model:detail")
def get_model_version(version_id: int):
    data = ModelService.get_version(version_id)
    return success_response(data)


@model_version_bp.post("/model-versions")
@permission_required("model:create")
def create_model_version():
    payload = model_version_create_schema.load(request.get_json(silent=True) or {})
    data = ModelService.create_version(payload)
    return success_response(data, "新增成功")


@model_version_bp.put("/model-versions/<int:version_id>")
@permission_required("model:update")
def update_model_version(version_id: int):
    payload = model_version_update_schema.load(request.get_json(silent=True) or {})
    data = ModelService.update_version(version_id, payload)
    return success_response(data, "更新成功")


@model_version_bp.patch("/model-versions/<int:version_id>/activate")
@permission_required("model:activate")
def activate_model_version(version_id: int):
    data = ModelService.activate_version(version_id)
    return success_response(data, "启用成功")


@model_version_bp.delete("/model-versions/<int:version_id>")
@permission_required("model:delete")
def delete_model_version(version_id: int):
    ModelService.delete_version(version_id)
    return success_response({}, "删除成功")
