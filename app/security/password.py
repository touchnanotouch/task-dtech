import bcrypt as _bcrypt


class PasswordProvider:
    def hash(self, password: str) -> str:
        return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()

    def verify(self, password: str, hashed: str) -> bool:
        return _bcrypt.checkpw(password.encode(), hashed.encode())
