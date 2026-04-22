from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass
class EmbeddingSearchResult:
    face_id: UUID
    identity_id: UUID | None
    score: float


class FaceEmbeddingPort(ABC):
    @abstractmethod
    async def store(self, face_id: UUID, identity_id: UUID | None, embedding: list[float]) -> None: ...

    @abstractmethod
    async def search(self, embedding: list[float], limit: int = 5, threshold: float = 0.55) -> list[EmbeddingSearchResult]: ...

    @abstractmethod
    async def delete(self, face_id: UUID) -> bool: ...
