from decimal import Decimal

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


class AccountRepo:
    async def get_by_user(self, session: AsyncSession, user_id: int) -> list[Account]:
        result = await session.execute(
            select(Account).where(Account.user_id == user_id).order_by(Account.id)
        )

        return list(result.scalars().all())

    async def get_by_user_and_id(
        self, session: AsyncSession, user_id: int, account_id: int
    ) -> Account | None:
        result = await session.execute(
            select(Account).where(Account.id == account_id, Account.user_id == user_id)
        )

        return result.scalar_one_or_none()

    async def create(
        self, session: AsyncSession, account_id: int, user_id: int
    ) -> Account:
        account = Account(id=account_id, user_id=user_id, balance=Decimal("0.00"))

        session.add(account)

        await session.flush()
        await session.refresh(account)

        return account

    async def increase_balance(
        self, session: AsyncSession, account_id: int, amount: Decimal
    ) -> None:
        await session.execute(
            update(Account)
            .where(Account.id == account_id)
            .values(balance=Account.balance + amount, updated_at=func.now())
        )

        await session.flush()

        account = await session.get(Account, account_id)
        if account:
            session.expire(account)
