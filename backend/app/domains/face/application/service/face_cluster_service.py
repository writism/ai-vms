import logging
import math
from datetime import UTC, datetime
from uuid import UUID

from app.domains.face.application.port.face_cluster_repository_port import FaceClusterRepositoryPort
from app.domains.face.domain.entity.face_cluster import FaceCluster
from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0 or nb == 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


class FaceClusterService:
    def __init__(self, repo: FaceClusterRepositoryPort):
        self._repo = repo

    async def cluster_face(
        self,
        embedding: list[float],
        image_path: str | None,
        quality_score: float,
        camera_id: UUID,
    ) -> FaceCluster:
        threshold = settings.cluster_similarity_threshold
        existing = await self._repo.find_active_pending()

        best: FaceCluster | None = None
        best_sim = -1.0
        for cluster in existing:
            sim = _cosine(embedding, cluster.representative_embedding)
            if sim > best_sim:
                best_sim = sim
                best = cluster

        now = datetime.now(UTC)
        if best is not None and best_sim >= threshold:
            best.last_seen = now
            best.last_camera_id = camera_id
            if quality_score > best.representative_quality_score:
                best.representative_embedding = embedding
                best.representative_image_path = image_path
                best.representative_quality_score = quality_score
            best.updated_at = now
            await self._repo.update(best)
            logger.info(
                "cluster absorb id=%s sim=%.3f quality=%.2f",
                best.id, best_sim, quality_score,
            )
            return best

        cluster = FaceCluster(
            representative_embedding=embedding,
            representative_image_path=image_path,
            representative_quality_score=quality_score,
            last_seen=now,
            last_camera_id=camera_id,
        )
        await self._repo.save(cluster)
        logger.info(
            "cluster created id=%s (no match >=%.2f, best_sim=%.3f)",
            cluster.id, threshold, max(best_sim, 0.0),
        )
        return cluster
