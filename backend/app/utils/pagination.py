from app.utils.error_code import BusinessError, ErrorCode


def parse_pagination_args(args):
    try:
        page = max(int(args.get("page", 1)), 1)
        page_size = min(max(int(args.get("page_size", 10)), 1), 100)
    except (TypeError, ValueError) as exc:
        raise BusinessError(ErrorCode.PARAM_ERROR, "分页参数错误") from exc
    sort_field = args.get("sort_field", "create_time")
    sort_order = args.get("sort_order", "desc").lower()
    if sort_order not in {"asc", "desc"}:
        raise BusinessError(ErrorCode.PARAM_ERROR, "排序参数错误")
    return {
        "page": page,
        "page_size": page_size,
        "sort_field": sort_field,
        "sort_order": sort_order,
    }


def build_page_data(items, total: int, page: int, page_size: int):
    return {
        "list": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
