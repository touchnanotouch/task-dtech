from sanic import Blueprint
from sanic.exceptions import SanicException
from sanic.response import HTTPResponse, json

from app.api import CreateUserRequest, UpdateUserRequest, UserOut
from app.api.handlers import parse_pagination
from app.core import Forbidden


def create_users_bp(admin_service):
    bp = Blueprint("users", url_prefix="/api/v1/admin/users")

    def _require_admin(request):
        payload = getattr(request.ctx, "payload", {})
        if not payload.get("is_admin"):
            raise Forbidden()

    def _require_body(request):
        if request.json is None:
            raise SanicException("Request body must be valid JSON", status_code=400)

    @bp.get("/")
    async def list_users(request):
        _require_admin(request)

        page, per_page = parse_pagination(request)

        result = await admin_service.list_users(page=page, per_page=per_page)

        return json(result)

    @bp.get("/<user_id:int>")
    async def get_user(request, user_id):
        _require_admin(request)

        result = await admin_service.get_user(user_id)

        return json(result)

    @bp.post("/")
    async def create_user(request):
        _require_admin(request)
        _require_body(request)

        body = CreateUserRequest(**request.json)

        user = await admin_service.create_user(
            email=body.email,
            password=body.password,
            full_name=body.full_name,
        )

        return json(UserOut(**user).model_dump(), status=201)

    @bp.patch("/<user_id:int>")
    async def update_user(request, user_id):
        _require_admin(request)
        _require_body(request)

        body = UpdateUserRequest(**request.json)

        kwargs = {k: v for k, v in body.model_dump().items() if v is not None}

        user = await admin_service.update_user(user_id, **kwargs)

        return json(UserOut(**user).model_dump())

    @bp.delete("/<user_id:int>")
    async def delete_user(request, user_id):
        _require_admin(request)

        await admin_service.delete_user(user_id)

        return HTTPResponse(status=204)

    @bp.get("/<user_id:int>/accounts")
    async def get_accounts(request, user_id):
        _require_admin(request)

        accounts = await admin_service.get_user_accounts(user_id)

        return json({"data": accounts})

    return bp
