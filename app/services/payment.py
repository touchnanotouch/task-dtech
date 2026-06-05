from app.core import get_session
from app.repositories import PaymentRepo


class PaymentService:
    def __init__(self, payment_repo: PaymentRepo):
        self._payment_repo = payment_repo

    async def get_my_payments(
        self, user_id: int, page: int = 1, per_page: int = 10
    ) -> dict:
        async with get_session() as session:
            payments, total = await self._payment_repo.get_by_user(
                session, user_id, page=page, per_page=per_page
            )

            return {
                "data": [
                    {
                        "id": p.id,
                        "transaction_id": p.transaction_id,
                        "account_id": p.account_id,
                        "amount": str(p.amount),
                        "created_at": p.created_at.isoformat(),
                    }
                    for p in payments
                ],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                },
            }
