from abc import ABC, abstractmethod
from uuid import UUID

from app.domains.face.domain.entity.identity import Identity


class IdentityRepositoryPort(ABC):
    @abstractmethod
    async def save(self, identity: Identity) -> Identity: ...

    @abstractmethod
    async def find_by_id(self, identity_id: UUID) -> Identity | None: ...

    @abstractmethod
    async def find_all(self) -> list[Identity]: ...

    @abstractmethod
    async def delete(self, identity_id: UUID) -> bool: ...
