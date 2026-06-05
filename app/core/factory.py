import logging

from pydantic import ValidationError

from sanic import Sanic
from sanic.exceptions import SanicException
from sanic.response import json

from app.core import (
    EXCEPTION_MAP,
    AppError,
    Settings,
    close_db,
    init_db,
)


logger = logging.getLogger(__name__)


def create_app() -> Sanic:
    app = Sanic("PaymentAPI")

    settings = Settings()

    @app.before_server_start
    async def startup(app):
        await init_db(settings.database_url, echo=settings.debug)

    @app.after_server_stop
    async def shutdown(app):
        await close_db()

    @app.exception(AppError)
    async def handle_app_error(request, exception):
        status = EXCEPTION_MAP.get(type(exception), 400)

        return json({"error": str(exception)}, status=status)

    @app.exception(ValidationError)
    async def handle_validation_error(request, exception):
        return json({"error": str(exception)}, status=422)

    @app.exception(SanicException)
    async def handle_sanic_error(request, exception):
        return json({"error": str(exception)}, status=exception.status_code)

    @app.exception(Exception)
    async def handle_unexpected(request, exception):
        logger.exception("Unhandled exception")

        return json({"error": "Internal server error"}, status=500)

    _wire(app, settings)

    return app


def _wire(app: Sanic, settings: Settings) -> None:
    from app.repositories import AccountRepo, PaymentRepo, UserRepo
    from app.services import (
        AccountService,
        AdminService,
        AuthService,
        PaymentService,
        WebhookService,
    )
    from app.security import JWTProvider, PasswordProvider

    jwt_provider = JWTProvider(settings.jwt_secret, settings.jwt_expiration_hours)
    password_service = PasswordProvider()

    user_repo = UserRepo()
    account_repo = AccountRepo()
    payment_repo = PaymentRepo()

    auth_service = AuthService(user_repo, jwt_provider, password_service)
    admin_service = AdminService(user_repo, account_repo, password_service)
    account_service = AccountService(account_repo)
    payment_service = PaymentService(payment_repo)
    webhook_service = WebhookService(
        account_repo, payment_repo, settings.webhook_secret
    )

    from app.api import setup_auth_middleware

    setup_auth_middleware(app, jwt_provider)

    from app.api.handlers.auth import create_auth_bp
    from app.api.handlers.users import create_users_bp
    from app.api.handlers.accounts import create_accounts_bp
    from app.api.handlers.payments import create_payments_bp
    from app.api.handlers.webhook import create_webhook_bp

    app.blueprint(create_auth_bp(auth_service))
    app.blueprint(create_users_bp(admin_service))
    app.blueprint(create_accounts_bp(account_service))
    app.blueprint(create_payments_bp(payment_service))
    app.blueprint(create_webhook_bp(webhook_service))
