import jwt as pyjwt

from datetime import datetime, timedelta, timezone


class JWTProvider:
    def __init__(self, secret: str, expiration_hours: int = 24):
        self._secret = secret
        self._expiration = timedelta(hours=expiration_hours)

    def encode(self, user_id: int, is_admin: bool) -> str:
        payload = {
            "user_id": user_id,
            "is_admin": is_admin,
            "exp": datetime.now(timezone.utc) + self._expiration,
        }

        return pyjwt.encode(payload, self._secret, algorithm="HS256")

    def decode(self, token: str) -> dict:
        return pyjwt.decode(token, self._secret, algorithms=["HS256"])
