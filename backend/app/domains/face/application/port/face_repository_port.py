from abc import ABC, abstractmethod
from uuid import UUID

from app.domains.face.domain.entity.face import Face


class FaceRepositoryPort(ABC):
    @abstractmethod
    async def save(self, face: Face) -> Face: ...

    @abstractmethod
    async def find_by_identity_id(self, identity_id: UUID) -> list[Face]: ...

    @abstractmethod
    async def find_by_id(self, face_id: UUID) -> Face | None: ...

    @abstractmethod
    async def delete(self, face_id: UUID) -> bool: ...
