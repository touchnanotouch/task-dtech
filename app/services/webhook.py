from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from app.core import get_session, InvalidSignature
from app.repositories import AccountRepo, PaymentRepo
from app.security import verify_webhook_signature


class WebhookService:
    def __init__(
        self, account_repo: AccountRepo, payment_repo: PaymentRepo, webhook_secret: str
    ):
        self._account_repo = account_repo
        self._payment_repo = payment_repo
        self._secret = webhook_secret

    async def process_payment(
        self,
        transaction_id: str,
        account_id: int,
        user_id: int,
        amount: Decimal,
        signature: str,
    ) -> dict:
        if not verify_webhook_signature(
            transaction_id=transaction_id,
            account_id=account_id,
            user_id=user_id,
            amount=amount,
            signature=signature,
            secret=self._secret,
        ):
            raise InvalidSignature()

        async with get_session() as session:
            existing = await self._payment_repo.get_by_transaction_id(
                session, transaction_id
            )
            if existing:
                return {
                    "status": "already_processed",
                    "payment_id": existing.id,
                }

            account = await self._account_repo.get_by_user_and_id(
                session, user_id, account_id
            )
            if not account:
                try:
                    account = await self._account_repo.create(
                        session, account_id=account_id, user_id=user_id
                    )
                except IntegrityError:
                    await session.rollback()
                    account = await self._account_repo.get_by_user_and_id(
                        session, user_id, account_id
                    )
                    if not account:
                        raise

            try:
                payment = await self._payment_repo.create(
                    session,
                    transaction_id=transaction_id,
                    account_id=account.id,
                    user_id=user_id,
                    amount=amount,
                )

                await self._account_repo.increase_balance(session, account.id, amount)

                await session.commit()
            except IntegrityError:
                await session.rollback()
                existing = await self._payment_repo.get_by_transaction_id(
                    session, transaction_id
                )
                if existing:
                    return {
                        "status": "already_processed",
                        "payment_id": existing.id,
                    }
                raise

            return {
                "status": "success",
                "payment_id": payment.id,
            }
