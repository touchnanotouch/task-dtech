from decimal import Decimal

from tests.helpers import webhook_signature


class TestWebhook:
    def test_success(self, test_client, seed):
        sig = webhook_signature("tx-1", 99, 1, Decimal("250.00"))

        _, resp = test_client.post(
            "/api/v1/webhook/",
            json={
                "transaction_id": "tx-1",
                "account_id": 99,
                "user_id": 1,
                "amount": "250.00",
                "signature": sig,
            },
        )

        assert resp.status == 200

        body = resp.json

        assert body["status"] == "success"
        assert isinstance(body["payment_id"], int)

    def test_creates_account_when_not_found(self, test_client, seed):
        sig = webhook_signature("tx-new-acc", 500, 1, Decimal("100.00"))

        _, resp = test_client.post(
            "/api/v1/webhook/",
            json={
                "transaction_id": "tx-new-acc",
                "account_id": 500,
                "user_id": 1,
                "amount": "100.00",
                "signature": sig,
            },
        )

        assert resp.status == 200
        assert resp.json["status"] == "success"

    def test_idempotent_duplicate_transaction(self, test_client, seed):
        sig = webhook_signature("tx-dup-2", 99, 1, Decimal("50.00"))

        payload = {
            "transaction_id": "tx-dup-2",
            "account_id": 99,
            "user_id": 1,
            "amount": "50.00",
            "signature": sig,
        }

        _, resp1 = test_client.post("/api/v1/webhook/", json=payload)

        assert resp1.json["status"] == "success"

        _, resp2 = test_client.post("/api/v1/webhook/", json=payload)

        assert resp2.status == 200
        assert resp2.json["status"] == "already_processed"
        assert resp2.json["payment_id"] == resp1.json["payment_id"]

    def test_invalid_signature(self, test_client):
        _, resp = test_client.post(
            "/api/v1/webhook/",
            json={
                "transaction_id": "tx-1",
                "account_id": 99,
                "user_id": 1,
                "amount": "250.00",
                "signature": "invalid",
            },
        )

        assert resp.status == 422

    def test_missing_body(self, test_client):
        _, resp = test_client.post(
            "/api/v1/webhook/",
            content=b"",
            headers={"Content-Type": "application/json"},
        )

        assert resp.status == 400

    def test_missing_fields(self, test_client):
        _, resp = test_client.post(
            "/api/v1/webhook/",
            json={"transaction_id": "tx-1"},
        )

        assert resp.status == 422
