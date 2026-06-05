import pytest

from decimal import Decimal
from unittest.mock import MagicMock

from sqlalchemy.exc import IntegrityError

from app.core import InvalidSignature
from app.repositories import AccountRepo, PaymentRepo
from app.services import WebhookService

from tests.helpers import webhook_signature


SECRET = "test-webhook-secret"
TX_ID = "tx-unique-1"
AMOUNT = Decimal("250.00")


@pytest.fixture
def account_repo():
    return MagicMock(spec=AccountRepo)


@pytest.fixture
def payment_repo():
    return MagicMock(spec=PaymentRepo)


@pytest.fixture
def svc(account_repo, payment_repo):
    return WebhookService(account_repo, payment_repo, SECRET)


class TestProcessPayment:
    async def test_success(self, mock_get_session, svc, account_repo, payment_repo):
        sig = webhook_signature(TX_ID, 1, 1, AMOUNT, SECRET)

        account_repo.get_by_user_and_id.return_value = MagicMock(id=1)
        payment_repo.get_by_transaction_id.return_value = None

        payment = MagicMock(id=42)

        payment_repo.create.return_value = payment

        result = await svc.process_payment(
            transaction_id=TX_ID,
            account_id=1,
            user_id=1,
            amount=AMOUNT,
            signature=sig,
        )

        assert result == {"status": "success", "payment_id": 42}

        account_repo.increase_balance.assert_called_once_with(
            mock_get_session, 1, AMOUNT
        )
        mock_get_session.commit.assert_called_once()

    async def test_invalid_signature(self, mock_get_session, svc):
        with pytest.raises(InvalidSignature):
            await svc.process_payment(
                transaction_id=TX_ID,
                account_id=1,
                user_id=1,
                amount=AMOUNT,
                signature="invalid",
            )

    async def test_idempotent_duplicate_before_insert(
        self, svc, mock_get_session, account_repo, payment_repo
    ):
        sig = webhook_signature("tx-dup", 1, 1, AMOUNT, SECRET)

        account_repo.get_by_user_and_id.return_value = MagicMock(id=1)
        payment_repo.get_by_transaction_id.return_value = MagicMock(id=5)

        result = await svc.process_payment(
            transaction_id="tx-dup",
            account_id=1,
            user_id=1,
            amount=AMOUNT,
            signature=sig,
        )

        assert result == {"status": "already_processed", "payment_id": 5}

    async def test_idempotent_duplicate_transaction_race(
        self, svc, mock_get_session, account_repo, payment_repo
    ):
        sig = webhook_signature("tx-race", 1, 1, AMOUNT, SECRET)

        account_repo.get_by_user_and_id.return_value = MagicMock(id=1)
        payment_repo.get_by_transaction_id.side_effect = [None, MagicMock(id=7)]
        payment_repo.create.side_effect = IntegrityError("stmt", {}, Exception())

        result = await svc.process_payment(
            transaction_id="tx-race",
            account_id=1,
            user_id=1,
            amount=AMOUNT,
            signature=sig,
        )

        assert result == {"status": "already_processed", "payment_id": 7}

        mock_get_session.rollback.assert_called_once()

    async def test_creates_account_when_not_found(
        self, mock_get_session, svc, account_repo, payment_repo
    ):
        sig = webhook_signature(TX_ID, 99, 1, AMOUNT, SECRET)

        account_repo.get_by_user_and_id.side_effect = [None, MagicMock(id=99)]
        account_repo.create.return_value = MagicMock(id=99)
        payment_repo.get_by_transaction_id.return_value = None
        payment_repo.create.return_value = MagicMock(id=42)

        result = await svc.process_payment(
            transaction_id=TX_ID,
            account_id=99,
            user_id=1,
            amount=AMOUNT,
            signature=sig,
        )

        assert result["status"] == "success"

        account_repo.create.assert_called_once_with(
            mock_get_session, account_id=99, user_id=1
        )

    async def test_race_condition_on_account_create(
        self, mock_get_session, svc, account_repo, payment_repo
    ):
        sig = webhook_signature("tx-acc-race", 99, 1, AMOUNT, SECRET)

        account_repo.get_by_user_and_id.side_effect = [None, MagicMock(id=99)]
        account_repo.create.side_effect = IntegrityError("stmt", {}, Exception())
        payment_repo.get_by_transaction_id.return_value = None
        payment_repo.create.return_value = MagicMock(id=42)

        result = await svc.process_payment(
            transaction_id="tx-acc-race",
            account_id=99,
            user_id=1,
            amount=AMOUNT,
            signature=sig,
        )

        assert result["status"] == "success"

        mock_get_session.rollback.assert_called_once()

    async def test_account_create_race_and_still_missing(
        self, mock_get_session, svc, account_repo, payment_repo
    ):
        sig = webhook_signature("tx-miss", 99, 1, AMOUNT, SECRET)

        payment_repo.get_by_transaction_id.return_value = None
        account_repo.get_by_user_and_id.side_effect = [None, None]
        account_repo.create.side_effect = IntegrityError("stmt", {}, Exception())

        with pytest.raises(IntegrityError):
            await svc.process_payment(
                transaction_id="tx-miss",
                account_id=99,
                user_id=1,
                amount=AMOUNT,
                signature=sig,
            )
