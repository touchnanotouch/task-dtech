class TestPayments:
    def test_list_my_payments_empty(self, test_client, user_token):
        _, resp = test_client.get(
            "/api/v1/payments/",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert resp.status == 200

        body = resp.json

        assert body["data"] == []
        assert body["pagination"]["total"] == 0
        assert body["pagination"]["page"] == 1
        assert body["pagination"]["per_page"] == 10

    def test_list_payments_unauthorized(self, test_client):
        _, resp = test_client.get("/api/v1/payments/")

        assert resp.status == 401

    def test_list_payments_pagination(self, test_client, user_token):
        _, resp = test_client.get(
            "/api/v1/payments/?page=2&per_page=5",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert resp.status == 200
        assert resp.json["pagination"] == {
            "page": 2,
            "per_page": 5,
            "total": 0,
        }
