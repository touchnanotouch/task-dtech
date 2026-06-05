from decimal import Decimal

from app.security import verify_webhook_signature

from tests.helpers import webhook_signature


class TestVerifyWebhookSignature:
    def test_valid_signature(self):
        sig = webhook_signature("tx-123", 1, 42, Decimal("100.50"), "my-secret")

        assert verify_webhook_signature(
            transaction_id="tx-123",
            account_id=1,
            user_id=42,
            amount=Decimal("100.50"),
            signature=sig,
            secret="my-secret",
        )

    def test_wrong_secret(self):
        sig = webhook_signature("tx-123", 1, 42, Decimal("100.50"), "my-secret")

        assert not verify_webhook_signature(
            transaction_id="tx-123",
            account_id=1,
            user_id=42,
            amount=Decimal("100.50"),
            signature=sig,
            secret="wrong-secret",
        )

    def test_tampered_transaction_id(self):
        sig = webhook_signature("tx-123", 1, 42, Decimal("100.50"), "my-secret")

        assert not verify_webhook_signature(
            transaction_id="tx-999",
            account_id=1,
            user_id=42,
            amount=Decimal("100.50"),
            signature=sig,
            secret="my-secret",
        )

    def test_tampered_amount(self):
        sig = webhook_signature("tx-123", 1, 42, Decimal("100.50"), "my-secret")

        assert not verify_webhook_signature(
            transaction_id="tx-123",
            account_id=1,
            user_id=42,
            amount=Decimal("99.99"),
            signature=sig,
            secret="my-secret",
        )

    def test_tampered_account_id(self):
        sig = webhook_signature("tx-123", 1, 42, Decimal("100.50"), "my-secret")

        assert not verify_webhook_signature(
            transaction_id="tx-123",
            account_id=2,
            user_id=42,
            amount=Decimal("100.50"),
            signature=sig,
            secret="my-secret",
        )

    def test_tampered_user_id(self):
        sig = webhook_signature("tx-123", 1, 42, Decimal("100.50"), "my-secret")

        assert not verify_webhook_signature(
            transaction_id="tx-123",
            account_id=1,
            user_id=99,
            amount=Decimal("100.50"),
            signature=sig,
            secret="my-secret",
        )

    def test_empty_string_signature(self):
        assert not verify_webhook_signature(
            transaction_id="tx-123",
            account_id=1,
            user_id=42,
            amount=Decimal("100"),
            signature="",
            secret="my-secret",
        )

    def test_negative_amount(self):
        sig = webhook_signature("tx-1", 1, 1, Decimal("-50.00"), "secret")

        assert verify_webhook_signature(
            transaction_id="tx-1",
            account_id=1,
            user_id=1,
            amount=Decimal("-50.00"),
            signature=sig,
            secret="secret",
        )

    def test_large_amount(self):
        sig = webhook_signature("tx-1", 1, 1, Decimal("9999999999.99"), "secret")

        assert verify_webhook_signature(
            transaction_id="tx-1",
            account_id=1,
            user_id=1,
            amount=Decimal("9999999999.99"),
            signature=sig,
            secret="secret",
        )
