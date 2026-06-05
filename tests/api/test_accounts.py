class TestAccounts:
    def test_list_my_accounts(self, test_client, user_token):
        _, resp = test_client.get(
            "/api/v1/accounts/",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert resp.status == 200

        body = resp.json

        assert "data" in body
        assert len(body["data"]) >= 1

        account = body["data"][0]

        assert isinstance(account["id"], int)
        assert account["balance"] == "1000.00"
        assert "created_at" in account

    def test_list_accounts_unauthorized(self, test_client):
        _, resp = test_client.get("/api/v1/accounts/")

        assert resp.status == 401

    def test_list_accounts_admin(self, test_client, admin_token):
        _, resp = test_client.get(
            "/api/v1/accounts/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert resp.status == 200
        assert "data" in resp.json
