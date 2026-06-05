from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.user import User
from app.repositories import AccountRepo, PaymentRepo, UserRepo
from app.security import JWTProvider, PasswordProvider


@pytest.fixture
def mock_session():
    session = AsyncMock()

    session.__aenter__.return_value = session
    session.__aexit__.return_value = None

    return session


@pytest.fixture
def mock_get_session(mock_session):
    with patch("app.services.auth.get_session", return_value=mock_session):
        with patch("app.services.admin.get_session", return_value=mock_session):
            with patch("app.services.webhook.get_session", return_value=mock_session):
                with patch(
                    "app.services.account.get_session", return_value=mock_session
                ):
                    with patch(
                        "app.services.payment.get_session", return_value=mock_session
                    ):
                        yield mock_session


@pytest.fixture
def user_repo():
    return MagicMock(spec=UserRepo)


@pytest.fixture
def account_repo():
    return MagicMock(spec=AccountRepo)


@pytest.fixture
def payment_repo():
    return MagicMock(spec=PaymentRepo)


@pytest.fixture
def jwt_provider():
    provider = MagicMock(spec=JWTProvider)

    provider.encode.return_value = "mock-token"
    provider.decode.return_value = {"user_id": 1, "is_admin": False}

    return provider


@pytest.fixture
def password_provider():
    provider = MagicMock(spec=PasswordProvider)

    provider.hash.return_value = "$2b$12$hashedpassword"
    provider.verify.return_value = True

    return provider


@pytest.fixture
def make_user():
    def _make(**overrides):
        return User(
            id=overrides.get("id", 1),
            email=overrides.get("email", "test@test.com"),
            password_hash=overrides.get("password_hash", "$2b$12$hash"),
            full_name=overrides.get("full_name", "Test User"),
            is_admin=overrides.get("is_admin", False),
        )

    return _make
