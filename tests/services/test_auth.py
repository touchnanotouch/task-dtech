import jwt as pyjwt
import pytest

from app.core import InvalidCredentials, InvalidToken
from app.services import AuthService


@pytest.mark.asyncio
class TestLogin:
    async def test_success(
        self, mock_get_session, user_repo, jwt_provider, password_provider, make_user
    ):
        user = make_user()

        user_repo.get_by_email.return_value = user
        password_provider.verify.return_value = True
        jwt_provider.encode.return_value = "access-token"

        svc = AuthService(user_repo, jwt_provider, password_provider)

        token = await svc.login("test@test.com", "password")

        assert token == "access-token"

        user_repo.get_by_email.assert_called_once()
        password_provider.verify.assert_called_once_with("password", user.password_hash)
        jwt_provider.encode.assert_called_once_with(user_id=1, is_admin=False)

    async def test_user_not_found(
        self, mock_get_session, user_repo, jwt_provider, password_provider
    ):
        user_repo.get_by_email.return_value = None

        svc = AuthService(user_repo, jwt_provider, password_provider)

        with pytest.raises(InvalidCredentials):
            await svc.login("unknown@test.com", "password")

    async def test_wrong_password(
        self, mock_get_session, user_repo, jwt_provider, password_provider, make_user
    ):
        user = make_user()

        user_repo.get_by_email.return_value = user
        password_provider.verify.return_value = False

        svc = AuthService(user_repo, jwt_provider, password_provider)

        with pytest.raises(InvalidCredentials):
            await svc.login("test@test.com", "wrong-password")


@pytest.mark.asyncio
class TestGetCurrentUser:
    async def test_valid_token(
        self, mock_get_session, user_repo, jwt_provider, password_provider, make_user
    ):
        user = make_user()

        user_repo.get_by_id.return_value = user

        svc = AuthService(user_repo, jwt_provider, password_provider)

        result = await svc.get_current_user("valid-token")

        assert result is user

        jwt_provider.decode.assert_called_once_with("valid-token")

    async def test_expired_token(
        self, mock_get_session, user_repo, jwt_provider, password_provider
    ):
        jwt_provider.decode.side_effect = pyjwt.ExpiredSignatureError()

        svc = AuthService(user_repo, jwt_provider, password_provider)

        with pytest.raises(InvalidToken):
            await svc.get_current_user("expired-token")

    async def test_malformed_token(
        self, mock_get_session, user_repo, jwt_provider, password_provider
    ):
        jwt_provider.decode.side_effect = pyjwt.InvalidTokenError()

        svc = AuthService(user_repo, jwt_provider, password_provider)

        with pytest.raises(InvalidToken):
            await svc.get_current_user("bad-token")

    async def test_user_deleted(
        self, mock_get_session, user_repo, jwt_provider, password_provider
    ):
        user_repo.get_by_id.return_value = None

        svc = AuthService(user_repo, jwt_provider, password_provider)

        with pytest.raises(InvalidToken):
            await svc.get_current_user("valid-token")
