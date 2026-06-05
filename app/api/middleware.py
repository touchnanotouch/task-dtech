import logging

import jwt as pyjwt

from sanic.response import json

PUBLIC_PATHS = {"/api/v1/auth/login", "/api/v1/webhook", "/api/v1/webhook/"}

logger = logging.getLogger(__name__)


def setup_auth_middleware(app, jwt_provider):
    @app.middleware("request")
    async def auth_middleware(request):
        if request.path in PUBLIC_PATHS:
            return

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return json({"error": "Missing or malformed token"}, status=401)

        token = auth.removeprefix("Bearer ")

        try:
            payload = jwt_provider.decode(token)
        except pyjwt.ExpiredSignatureError:
            return json({"error": "Token expired"}, status=401)
        except pyjwt.InvalidTokenError:
            return json({"error": "Invalid token"}, status=401)

        request.ctx.payload = payload
