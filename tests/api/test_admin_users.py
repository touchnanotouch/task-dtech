class TestAdminUsers:
    def test_list_users(self, test_client, admin_token):
        _, resp = test_client.get(
            "/api/v1/admin/users/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert resp.status == 200

        body = resp.json

        assert len(body["data"]) >= 2
        assert body["pagination"]["total"] >= 2

    def test_list_users_non_admin(self, test_client, user_token):
        _, resp = test_client.get(
            "/api/v1/admin/users/",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert resp.status == 403

    def test_list_users_unauthorized(self, test_client):
        _, resp = test_client.get("/api/v1/admin/users/")

        assert resp.status == 401

    def test_get_user(self, test_client, admin_token):
        _, resp = test_client.get(
            "/api/v1/admin/users/1",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert resp.status == 200
        assert resp.json["email"] == "user@test.com"
        assert resp.json["full_name"] == "Test User"

    def test_get_user_not_found(self, test_client, admin_token):
        _, resp = test_client.get(
            "/api/v1/admin/users/9999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert resp.status == 404

    def test_create_user(self, test_client, admin_token):
        _, resp = test_client.post(
            "/api/v1/admin/users/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "email": "newuser@test.com",
                "password": "secret123",
                "full_name": "New User",
            },
        )

        assert resp.status == 201

        body = resp.json

        assert body["email"] == "newuser@test.com"
        assert body["full_name"] == "New User"
        assert body["is_admin"] is False
        assert isinstance(body["id"], int)

    def test_create_user_duplicate_email(self, test_client, admin_token):
        _, resp1 = test_client.post(
            "/api/v1/admin/users/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "email": "dupe@test.com",
                "password": "secret123",
                "full_name": "Duplicate",
            },
        )

        assert resp1.status == 201

        _, resp2 = test_client.post(
            "/api/v1/admin/users/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "email": "dupe@test.com",
                "password": "secret456",
                "full_name": "Duplicate Again",
            },
        )

        assert resp2.status == 409

    def test_update_user(self, test_client, admin_token):
        _, resp = test_client.patch(
            "/api/v1/admin/users/1",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"full_name": "Updated Name"},
        )

        assert resp.status == 200
        assert resp.json["full_name"] == "Updated Name"

    def test_update_user_not_found(self, test_client, admin_token):
        _, resp = test_client.patch(
            "/api/v1/admin/users/9999",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"full_name": "Nobody"},
        )

        assert resp.status == 404

    def test_update_user_no_body(self, test_client, admin_token):
        _, resp = test_client.patch(
            "/api/v1/admin/users/1",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json",
            },
            content=b"",
        )

        assert resp.status == 400

    def test_delete_user(self, test_client, admin_token):
        _, resp = test_client.delete(
            "/api/v1/admin/users/1",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert resp.status == 204

    def test_delete_last_admin_blocked(self, test_client, admin_token):
        _, users_resp = test_client.get(
            "/api/v1/admin/users/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        admin_ids = [u["id"] for u in users_resp.json["data"] if u["is_admin"]]

        assert len(admin_ids) >= 1

        for uid in admin_ids[:-1]:
            test_client.delete(
                f"/api/v1/admin/users/{uid}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        _, resp = test_client.delete(
            f"/api/v1/admin/users/{admin_ids[-1]}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert resp.status == 409

    def test_get_user_accounts(self, test_client, admin_token):
        _, resp = test_client.get(
            "/api/v1/admin/users/1/accounts",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert resp.status == 200

        body = resp.json

        assert "data" in body
        assert len(body["data"]) >= 1
        assert str(body["data"][0]["balance"]) == "1000.00"

    def test_get_user_accounts_not_found(self, test_client, admin_token):
        _, resp = test_client.get(
            "/api/v1/admin/users/9999/accounts",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert resp.status == 404
