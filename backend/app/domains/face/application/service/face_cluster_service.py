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
        window_days = settings.cluster_active_window_days
        existing = await self._repo.find_active_pending(window_days)

        scored: list[tuple[float, FaceCluster]] = [
            (_cosine(embedding, c.representative_embedding), c) for c in existing
        ]
        scored.sort(key=lambda kv: kv[0], reverse=True)

        best_sim, best = (scored[0] if scored else (-1.0, None))

        # recent_avg: 최근 멤버 임베딩 평균으로 cluster drift(chain-link) 방지.
        # topk_avg 조건을 제거함 — 다수 클러스터 환경에서 타 클러스터가 average를 끌어내려
        # 정당한 흡수까지 막는 false-split 문제가 있었음.
        recent_avg = best_sim
        if best is not None:
            try:
                recent_embeddings = await self._repo.find_recent_member_embeddings(
                    best.id, settings.cluster_recent_member_anchor
                )
            except Exception:
                recent_embeddings = []
            if recent_embeddings:
                recent_sims = [_cosine(embedding, e) for e in recent_embeddings]
                recent_avg = sum(recent_sims) / len(recent_sims)

        now = datetime.now(UTC)
        # recent_avg에 약간의 여유(0.05)를 줌: 초기 멤버가 적거나 품질이 낮은 경우 보정
        absorb_ok = (
            best is not None
            and best_sim >= threshold
            and recent_avg >= threshold - 0.05
        )

        if absorb_ok:
            try:
                member_count = await self._repo.count_members(best.id)
            except Exception:
                member_count = 0
            if member_count >= settings.cluster_max_size:
                logger.info(
                    "cluster cap reached id=%s members=%d — starting new cluster",
                    best.id, member_count,
                )
            else:
                best.last_seen = now
                best.last_camera_id = camera_id
                if quality_score > best.representative_quality_score:
                    best.representative_embedding = embedding
                    best.representative_image_path = image_path
                    best.representative_quality_score = quality_score
                best.updated_at = now
                await self._repo.update(best)
                logger.info(
                    "cluster absorb id=%s sim=%.3f recent_avg=%.3f quality=%.2f members=%d",
                    best.id, best_sim, recent_avg, quality_score, member_count + 1,
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
            "cluster created (best_sim=%.3f recent_avg=%.3f >= thr=%.2f failed) id=%s",
            max(best_sim, 0.0), recent_avg, threshold, cluster.id,
        )
        return cluster

    async def merge_similar_clusters(self) -> int:
        """대표 embedding이 merge_threshold 이상 유사한 클러스터 쌍을 병합한다.
        품질이 낮은 쪽 클러스터를 높은 쪽으로 흡수시키고 IGNORED 처리한다."""
        merge_threshold = settings.cluster_merge_threshold
        window_days = settings.cluster_active_window_days
        clusters = await self._repo.find_active_pending(window_days)
        if len(clusters) < 2:
            return 0

        n = len(clusters)
        merged_ids: set[UUID] = set()
        merge_count = 0

        for i in range(n):
            if clusters[i].id in merged_ids:
                continue
            for j in range(i + 1, n):
                if clusters[j].id in merged_ids:
                    continue
                sim = _cosine(
                    clusters[i].representative_embedding,
                    clusters[j].representative_embedding,
                )
                if sim >= merge_threshold:
                    # 품질 높은 쪽이 survivor
                    if clusters[i].representative_quality_score >= clusters[j].representative_quality_score:
                        survivor, victim = clusters[i], clusters[j]
                    else:
                        survivor, victim = clusters[j], clusters[i]

                    try:
                        await self._repo.merge_into(victim.id, survivor.id)
                        merged_ids.add(victim.id)
                        merge_count += 1
                        logger.info(
                            "cluster merge: victim=%s → survivor=%s sim=%.3f",
                            victim.id, survivor.id, sim,
                        )
                    except Exception as exc:
                        logger.warning("cluster merge failed: %s", exc)

        return merge_count
