from sanic import Blueprint
from sanic.response import json


def create_payments_bp(payment_service):
    bp = Blueprint("payments", url_prefix="/api/v1/payments")

    @bp.get("/")
    async def list_payments(request):
        user_id = request.ctx.payload["user_id"]

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        result = await payment_service.get_my_payments(
            user_id, page=page, per_page=per_page
        )

        return json(result)

    return bp
