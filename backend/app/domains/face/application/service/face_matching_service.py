import logging
from dataclasses import dataclass
from uuid import UUID

from app.domains.face.application.port.face_embedding_port import FaceEmbeddingPort

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    top_identity_id: UUID | None
    top_score: float
    is_registered: bool
    candidate_count: int


class FaceMatchingService:
    def __init__(self, embedding_store: FaceEmbeddingPort):
        self._store = embedding_store

    async def match(
        self,
        embedding: list[float],
        threshold: float = 0.55,
        search_limit: int = 10,
    ) -> MatchResult:
        results = await self._store.search(embedding=embedding, limit=search_limit, threshold=0.0)

        identity_results = [r for r in results if r.identity_id is not None]
        if identity_results:
            best_per_identity: dict[UUID, float] = {}
            for r in identity_results:
                cur = best_per_identity.get(r.identity_id, -1.0)
                if r.score > cur:
                    best_per_identity[r.identity_id] = r.score
            top_identity_id, top_score = max(best_per_identity.items(), key=lambda kv: kv[1])
        else:
            top_score = results[0].score if results else 0.0
            top_identity_id = None

        is_registered = bool(top_identity_id and top_score >= threshold)
        logger.info(
            "Face match: top_score=%.3f threshold=%.3f identity=%s candidates=%d",
            top_score, threshold, top_identity_id, len(results),
        )
        return MatchResult(
            top_identity_id=top_identity_id,
            top_score=top_score,
            is_registered=is_registered,
            candidate_count=len(results),
        )
