from app.core import (
    get_session,
    CannotDeleteLastAdmin,
    EmailAlreadyExists,
    UserNotFound,
)
from app.repositories import AccountRepo, UserRepo
from app.security import PasswordProvider


class AdminService:
    def __init__(
        self,
        user_repo: UserRepo,
        account_repo: AccountRepo,
        password_service: PasswordProvider | None = None,
    ):
        self._user_repo = user_repo
        self._account_repo = account_repo
        self._password = password_service or PasswordProvider()

    async def create_user(self, email: str, password: str, full_name: str) -> dict:
        async with get_session() as session:
            existing = await self._user_repo.get_by_email(session, email)
            if existing:
                raise EmailAlreadyExists()

            user = await self._user_repo.create(
                session,
                email=email,
                password_hash=self._password.hash(password),
                full_name=full_name,
            )

            await session.commit()

            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_admin": user.is_admin,
            }

    async def update_user(
        self,
        user_id: int,
        email: str | None = None,
        password: str | None = None,
        full_name: str | None = None,
    ) -> dict:
        async with get_session() as session:
            if email:
                existing = await self._user_repo.get_by_email(session, email)
                if existing and existing.id != user_id:
                    raise EmailAlreadyExists()

            user = await self._user_repo.update(
                session,
                user_id=user_id,
                email=email,
                password_hash=self._password.hash(password) if password else None,
                full_name=full_name,
            )
            if not user:
                raise UserNotFound()

            await session.commit()

            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_admin": user.is_admin,
            }

    async def delete_user(self, user_id: int) -> None:
        async with get_session() as session:
            admins_count = await self._user_repo.count_admins(session)

            user = await self._user_repo.get_by_id(session, user_id)
            if not user:
                raise UserNotFound()

            if user.is_admin and admins_count <= 1:
                raise CannotDeleteLastAdmin()

            await self._user_repo.delete(session, user_id)

            await session.commit()

    async def get_user(self, user_id: int) -> dict:
        async with get_session() as session:
            user = await self._user_repo.get_by_id(session, user_id)
            if not user:
                raise UserNotFound()

            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_admin": user.is_admin,
            }

    async def list_users(self, page: int = 1, per_page: int = 10) -> dict:
        async with get_session() as session:
            users, total = await self._user_repo.list_all(
                session, page=page, per_page=per_page
            )

            return {
                "data": [
                    {
                        "id": u.id,
                        "email": u.email,
                        "full_name": u.full_name,
                        "is_admin": u.is_admin,
                    }
                    for u in users
                ],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                },
            }

    async def get_user_accounts(self, user_id: int) -> list[dict]:
        async with get_session() as session:
            user = await self._user_repo.get_by_id(session, user_id)
            if not user:
                raise UserNotFound()

            accounts = await self._account_repo.get_by_user(session, user_id)

            return [
                {
                    "id": a.id,
                    "balance": str(a.balance),
                    "created_at": a.created_at.isoformat(),
                }
                for a in accounts
            ]
