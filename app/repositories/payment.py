from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Payment


class PaymentRepo:
    async def get_by_transaction_id(
        self, session: AsyncSession, transaction_id: str
    ) -> Payment | None:
        result = await session.execute(
            select(Payment).where(Payment.transaction_id == transaction_id)
        )

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        session: AsyncSession,
        user_id: int,
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[list[Payment], int]:
        total = await session.execute(
            select(func.count()).select_from(Payment).where(Payment.user_id == user_id)
        )

        total_count = total.scalar() or 0

        result = await session.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .order_by(Payment.created_at.desc())
        )

        return list(result.scalars().all()), total_count

    async def create(
        self,
        session: AsyncSession,
        transaction_id: str,
        account_id: int,
        user_id: int,
        amount: Decimal,
    ) -> Payment:
        payment = Payment(
            transaction_id=transaction_id,
            account_id=account_id,
            user_id=user_id,
            amount=amount,
        )

        session.add(payment)

        await session.flush()
        await session.refresh(payment)

        return payment
