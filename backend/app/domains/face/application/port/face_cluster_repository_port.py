from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domains.face.domain.entity.face_cluster import ClusterStatus, FaceCluster


class ClusterSuggestion:
    def __init__(self, cluster: FaceCluster, count_window: int, avg_confidence: float):
        self.cluster = cluster
        self.count_window = count_window
        self.avg_confidence = avg_confidence


class FaceClusterRepositoryPort(ABC):
    @abstractmethod
    async def save(self, cluster: FaceCluster) -> FaceCluster: ...

    @abstractmethod
    async def find_by_id(self, cluster_id: UUID) -> FaceCluster | None: ...

    @abstractmethod
    async def find_active_pending(self, window_days: int = 7) -> list[FaceCluster]: ...

    @abstractmethod
    async def merge_into(self, source_id: UUID, target_id: UUID) -> None: ...

    @abstractmethod
    async def update(self, cluster: FaceCluster) -> FaceCluster: ...

    @abstractmethod
    async def update_status(self, cluster_id: UUID, status: ClusterStatus, linked_identity_id: UUID | None = None) -> bool: ...

    @abstractmethod
    async def find_suggestions(self, min_count: int, since: datetime) -> list[ClusterSuggestion]: ...

    @abstractmethod
    async def count_members(self, cluster_id: UUID) -> int: ...

    @abstractmethod
    async def find_recent_member_embeddings(
        self, cluster_id: UUID, limit: int
    ) -> list[list[float]]: ...
