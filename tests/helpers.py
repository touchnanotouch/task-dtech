import hashlib

from decimal import Decimal


def webhook_signature(
    transaction_id: str,
    account_id: int,
    user_id: int,
    amount: Decimal | str,
    secret: str = "dev-webhook-secret",
) -> str:
    keys = sorted(["account_id", "amount", "transaction_id", "user_id"])

    values = {
        "account_id": str(account_id),
        "amount": str(amount),
        "transaction_id": transaction_id,
        "user_id": str(user_id),
    }

    raw = "".join(values[k] for k in keys) + secret

    return hashlib.sha256(raw.encode()).hexdigest()
