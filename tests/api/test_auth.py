class TestLogin:
    def test_success(self, test_client):
        _, resp = test_client.post(
            "/api/v1/auth/login",
            json={"email": "user@test.com", "password": "user123"},
        )

        assert resp.status == 200

        body = resp.json

        assert "access_token" in body
        assert body["token_type"] == "Bearer"

    def test_wrong_password(self, test_client):
        _, resp = test_client.post(
            "/api/v1/auth/login",
            json={"email": "user@test.com", "password": "wrong"},
        )

        assert resp.status == 401

    def test_user_not_found(self, test_client):
        _, resp = test_client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@test.com", "password": "user123"},
        )

        assert resp.status == 401

    def test_missing_json_body(self, test_client):
        _, resp = test_client.post(
            "/api/v1/auth/login",
            content=b"",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 400

    def test_invalid_json(self, test_client):
        _, resp = test_client.post(
            "/api/v1/auth/login",
            content=b"not json",
            headers={"Content-Type": "application/json"},
        )

        assert resp.status == 400


class TestMe:
    def test_authenticated(self, test_client, user_token):
        _, resp = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert resp.status == 200

        body = resp.json

        assert body["email"] == "user@test.com"
        assert body["full_name"] == "Test User"
        assert body["is_admin"] is False
        assert isinstance(body["id"], int)

    def test_no_token(self, test_client):
        _, resp = test_client.get("/api/v1/auth/me")

        assert resp.status == 401

    def test_bad_token(self, test_client):
        _, resp = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalidtoken123"},
        )

        assert resp.status == 401
