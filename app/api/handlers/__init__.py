from sanic.exceptions import SanicException


def parse_pagination(
    request, default_page: int = 1, default_per_page: int = 10,
) -> tuple[int, int]:
    page_raw = request.args.get("page", default_page)
    per_page_raw = request.args.get("per_page", default_per_page)

    try:
        page = int(page_raw)
        per_page = int(per_page_raw)
    except (ValueError, TypeError):
        raise SanicException("Invalid pagination parameter", status_code=422)

    if page < 1 or per_page < 1 or per_page > 100:
        raise SanicException("Invalid pagination parameter", status_code=422)

    return page, per_page
