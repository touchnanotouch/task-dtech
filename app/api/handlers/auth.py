from sanic import Blueprint
from sanic.exceptions import SanicException
from sanic.response import json

from app.api import LoginRequest, UserOut


def create_auth_bp(auth_service):
    bp = Blueprint("auth", url_prefix="/api/v1/auth")

    @bp.post("/login")
    async def login(request):
        if request.json is None:
            raise SanicException("Request body must be valid JSON", status_code=400)

        body = LoginRequest(**request.json)

        token = await auth_service.login(body.email, body.password)

        return json({"access_token": token, "token_type": "Bearer"})

    @bp.get("/me")
    async def me(request):
        token = request.headers.get("Authorization", "").removeprefix("Bearer ")

        user = await auth_service.get_current_user(token)

        return json(
            UserOut(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                is_admin=user.is_admin,
            ).model_dump()
        )

    return bp
