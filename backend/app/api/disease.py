from flask import Blueprint, request

from app.middlewares.permission_middleware import permission_required
from app.schemas.disease_info_schema import DiseaseCreateSchema, DiseaseUpdateSchema
from app.services.disease_service import DiseaseService
from app.utils.pagination import parse_pagination_args
from app.utils.response import success_response


disease_bp = Blueprint("disease", __name__)
disease_create_schema = DiseaseCreateSchema()
disease_update_schema = DiseaseUpdateSchema()


def parse_disease_payload(schema):
    raw = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
    payload = schema.load(raw)
    example_image = request.files.get("example_image")
    return payload, example_image


@disease_bp.get("/diseases")
@permission_required("disease:list")
def list_diseases():
    pagination = parse_pagination_args(request.args)
    filters = {
        "keyword": request.args.get("keyword"),
        "severity_level": request.args.get("severity_level"),
    }
    data = DiseaseService.list_diseases(filters, pagination)
    return success_response(data)


@disease_bp.get("/diseases/<int:disease_id>")
@permission_required("disease:detail")
def get_disease(disease_id: int):
    data = DiseaseService.get_disease(disease_id)
    return success_response(data)


@disease_bp.post("/diseases")
@permission_required("disease:create")
def create_disease():
    payload, example_image = parse_disease_payload(disease_create_schema)
    data = DiseaseService.create_disease(payload, example_image)
    return success_response(data, "新增成功")


@disease_bp.put("/diseases/<int:disease_id>")
@permission_required("disease:update")
def update_disease(disease_id: int):
    payload, example_image = parse_disease_payload(disease_update_schema)
    data = DiseaseService.update_disease(disease_id, payload, example_image)
    return success_response(data, "更新成功")


@disease_bp.delete("/diseases/<int:disease_id>")
@permission_required("disease:delete")
def delete_disease(disease_id: int):
    DiseaseService.delete_disease(disease_id)
    return success_response({}, "删除成功")
