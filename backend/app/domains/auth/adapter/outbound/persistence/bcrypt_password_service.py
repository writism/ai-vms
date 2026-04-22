from passlib.context import CryptContext

from app.domains.auth.application.port.password_port import PasswordPort

_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordService(PasswordPort):
    def hash(self, password: str) -> str:
        return _ctx.hash(password)

    def verify(self, plain: str, hashed: str) -> bool:
        return _ctx.verify(plain, hashed)
