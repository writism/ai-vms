from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.domains.face.application.port.face_cluster_repository_port import FaceClusterRepositoryPort
from app.domains.face.application.response.face_response import FaceSuggestionResponse
from app.domains.face.domain.entity.face_cluster import ClusterStatus
from app.infrastructure.config.settings import settings


class ListFaceSuggestionsUseCase:
    def __init__(self, repo: FaceClusterRepositoryPort):
        self._repo = repo

    async def execute(self) -> list[FaceSuggestionResponse]:
        since = datetime.now(UTC) - timedelta(hours=settings.cluster_window_hours)
        suggestions = await self._repo.find_suggestions(
            min_count=settings.cluster_recommend_threshold,
            since=since,
        )
        return [
            FaceSuggestionResponse(
                cluster_id=s.cluster.id,
                image_url=f"/{s.cluster.representative_image_path}" if s.cluster.representative_image_path else None,
                count_window=s.count_window,
                avg_confidence=round(s.avg_confidence, 3),
                last_seen=s.cluster.last_seen,
                last_camera_id=s.cluster.last_camera_id,
                quality_score=s.cluster.representative_quality_score,
                status=s.cluster.status.value,
            )
            for s in suggestions
        ]


class ResolveFaceSuggestionUseCase:
    def __init__(self, repo: FaceClusterRepositoryPort):
        self._repo = repo

    async def register(self, cluster_id: UUID, identity_id: UUID) -> bool:
        return await self._repo.update_status(cluster_id, ClusterStatus.REGISTERED, identity_id)

    async def ignore(self, cluster_id: UUID) -> bool:
        return await self._repo.update_status(cluster_id, ClusterStatus.IGNORED)
