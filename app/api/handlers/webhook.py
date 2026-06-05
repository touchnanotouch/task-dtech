from sanic import Blueprint
from sanic.exceptions import SanicException
from sanic.response import json

from app.api import WebhookPayload


def create_webhook_bp(webhook_service):
    bp = Blueprint("webhook", url_prefix="/api/v1/webhook")

    @bp.post("/")
    async def process_webhook(request):
        if request.json is None:
            raise SanicException("Request body must be valid JSON", status_code=400)

        body = WebhookPayload(**request.json)

        result = await webhook_service.process_payment(
            transaction_id=body.transaction_id,
            account_id=body.account_id,
            user_id=body.user_id,
            amount=body.amount,
            signature=body.signature,
        )

        return json(result)

    return bp
