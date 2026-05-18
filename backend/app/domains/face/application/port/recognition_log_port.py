from abc import ABC, abstractmethod
from uuid import UUID

from app.domains.face.domain.entity.recognition_log import RecognitionLog


class RecognitionLogPort(ABC):
    @abstractmethod
    async def save(self, log: RecognitionLog) -> RecognitionLog: ...

    @abstractmethod
    async def find_recent(self, limit: int = 20) -> list[RecognitionLog]: ...

    @abstractmethod
    async def find_by_cluster(self, cluster_id: UUID, limit: int = 50) -> list[RecognitionLog]: ...

    @abstractmethod
    async def find_by_id(self, log_id: UUID) -> RecognitionLog | None: ...

    @abstractmethod
    async def assign_cluster_to_identity(
        self, cluster_id: UUID, identity_id: UUID, identity_name: str, identity_type: str
    ) -> int: ...

    @abstractmethod
    async def delete_by_id(self, log_id: UUID) -> bool: ...
