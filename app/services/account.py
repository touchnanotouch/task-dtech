from app.core import get_session
from app.repositories import AccountRepo


class AccountService:
    def __init__(self, account_repo: AccountRepo):
        self._account_repo = account_repo

    async def get_my_accounts(self, user_id: int) -> list[dict]:
        async with get_session() as session:
            accounts = await self._account_repo.get_by_user(session, user_id)

            return [
                {
                    "id": a.id,
                    "balance": str(a.balance),
                    "created_at": a.created_at.isoformat(),
                }
                for a in accounts
            ]
