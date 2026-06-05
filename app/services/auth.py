import jwt as pyjwt

from app.core import get_session, InvalidCredentials, InvalidToken
from app.models.user import User
from app.repositories import UserRepo
from app.security import JWTProvider, PasswordProvider


class AuthService:
    def __init__(
        self,
        user_repo: UserRepo,
        jwt_provider: JWTProvider,
        password_service: PasswordProvider | None = None,
    ):
        self._user_repo = user_repo
        self._jwt = jwt_provider
        self._password = password_service or PasswordProvider()

    async def login(self, email: str, password: str) -> str:
        async with get_session() as session:
            user = await self._user_repo.get_by_email(session, email)

            if not user or not self._password.verify(password, user.password_hash):
                raise InvalidCredentials()

            return self._jwt.encode(user_id=user.id, is_admin=user.is_admin)

    async def get_current_user(self, token: str) -> User | None:
        try:
            payload = self._jwt.decode(token)
        except (
            pyjwt.ExpiredSignatureError,
            pyjwt.InvalidTokenError,
        ):
            raise InvalidToken()

        async with get_session() as session:
            user = await self._user_repo.get_by_id(session, payload["user_id"])
            if not user:
                raise InvalidToken()

            return user
