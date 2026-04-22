from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt

from app.domains.auth.application.port.token_port import TokenPort
from app.domains.auth.domain.value_object.token import TokenPair
from app.infrastructure.config.settings import settings


class JwtTokenService(TokenPort):
    def create_access_token(self, user_id: UUID, role: str) -> TokenPair:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {"sub": str(user_id), "role": role, "exp": expire}
        token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
        return TokenPair(access_token=token)

    def decode_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        except JWTError:
            return None
