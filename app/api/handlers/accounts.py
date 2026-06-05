from sanic import Blueprint
from sanic.response import json


def create_accounts_bp(account_service):
    bp = Blueprint("accounts", url_prefix="/api/v1/accounts")

    @bp.get("/")
    async def list_accounts(request):
        user_id = request.ctx.payload["user_id"]

        accounts = await account_service.get_my_accounts(user_id)

        return json({"data": accounts})

    return bp
