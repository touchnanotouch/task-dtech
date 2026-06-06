from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class UserRepo:
    async def get_by_id(self, session: AsyncSession, user_id: int) -> User | None:
        return await session.get(User, user_id)

    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        result = await session.execute(select(User).where(User.email == email))

        return result.scalar_one_or_none()

    async def create(
        self,
        session: AsyncSession,
        email: str,
        password_hash: str,
        full_name: str,
        is_admin: bool = False,
    ) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            is_admin=is_admin,
        )

        session.add(user)

        await session.flush()
        await session.refresh(user)

        return user

    async def update(
        self,
        session: AsyncSession,
        user_id: int,
        email: str | None = None,
        password_hash: str | None = None,
        full_name: str | None = None,
    ) -> User | None:
        user = await session.get(User, user_id)
        if not user:
            return None

        if email is not None:
            user.email = email

        if password_hash is not None:
            user.password_hash = password_hash

        if full_name is not None:
            user.full_name = full_name

        await session.flush()
        await session.refresh(user)

        return user

    async def delete(self, session: AsyncSession, user_id: int) -> bool:
        user = await session.get(User, user_id)
        if not user:
            return False

        await session.delete(user)
        await session.flush()

        return True

    async def count_admins(self, session: AsyncSession) -> int:
        result = await session.execute(
            select(func.count()).select_from(User).where(User.is_admin.is_(True))
        )

        return result.scalar() or 0

    async def list_all(
        self, session: AsyncSession, page: int = 1, per_page: int = 10
    ) -> tuple[list[User], int]:
        total = await session.execute(select(func.count()).select_from(User))
        total_count = total.scalar() or 0

        result = await session.execute(
            select(User).offset((page - 1) * per_page).limit(per_page).order_by(User.id)
        )

        return list(result.scalars().all()), total_count
