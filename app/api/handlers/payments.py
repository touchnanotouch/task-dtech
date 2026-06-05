from sanic import Blueprint
from sanic.response import json

from app.api.handlers import parse_pagination


def create_payments_bp(payment_service):
    bp = Blueprint("payments", url_prefix="/api/v1/payments")

    @bp.get("/")
    async def list_payments(request):
        user_id = request.ctx.payload["user_id"]

        page, per_page = parse_pagination(request)

        result = await payment_service.get_my_payments(
            user_id, page=page, per_page=per_page
        )

        return json(result)

    return bp
