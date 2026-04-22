from abc import ABC, abstractmethod
from uuid import UUID

from app.domains.auth.domain.value_object.token import TokenPair


class TokenPort(ABC):
    @abstractmethod
    def create_access_token(self, user_id: UUID, role: str) -> TokenPair: ...

    @abstractmethod
    def decode_token(self, token: str) -> dict | None: ...
