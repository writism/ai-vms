import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domains.alert.application.port.alert_rule_repository_port import AlertRuleRepositoryPort
from app.domains.alert.application.port.danger_event_repository_port import DangerEventRepositoryPort
from app.domains.alert.domain.entity.danger_event import DangerEvent, DangerType, Severity
from app.domains.face.application.port.face_embedding_port import FaceEmbeddingPort
from app.domains.face.application.port.identity_repository_port import IdentityRepositoryPort
from app.domains.face.application.port.recognition_log_port import RecognitionLogPort
from app.domains.face.application.response.face_response import RecognitionLogResponse
from app.domains.face.application.service.face_cluster_service import FaceClusterService
from app.domains.face.application.service.face_matching_service import FaceMatchingService
from app.domains.face.domain.entity.recognition_log import RecognitionLog
from app.infrastructure.config.settings import settings
from app.infrastructure.event_bus.notification_dispatcher import NotificationDispatcher
from app.infrastructure.event_bus.ws_manager import ws_manager

logger = logging.getLogger(__name__)

from app.infrastructure.pipeline.recognition_cooldown_guard import (
    cluster_cooldown_guard,
    identity_cooldown_guard,
)

# 프로세스 단위 in-memory state (단일 백엔드 프로세스 가정)
_identity_last_grown: dict[UUID, datetime] = {}


class CreateRecognitionLogUseCase:
    def __init__(
        self,
        log_repo: RecognitionLogPort,
        identity_repo: IdentityRepositoryPort,
        embedding_store: FaceEmbeddingPort,
        alert_rule_repo: AlertRuleRepositoryPort | None = None,
        danger_event_repo: DangerEventRepositoryPort | None = None,
        dispatcher: NotificationDispatcher | None = None,
        cluster_service: FaceClusterService | None = None,
    ):
        self._log_repo = log_repo
        self._identity_repo = identity_repo
        self._embedding_store = embedding_store
        self._alert_rule_repo = alert_rule_repo
        self._danger_event_repo = danger_event_repo
        self._dispatcher = dispatcher
        self._cluster_service = cluster_service
        self._matching_service = FaceMatchingService(embedding_store)

    async def execute(
        self,
        camera_id: UUID,
        embedding: list[float],
        threshold: float = 0.55,
        image_path: str | None = None,
        quality_score: float = 0.0,
    ) -> RecognitionLogResponse:
        match = await self._matching_service.match(embedding, threshold)

        logger.info(
            "Face search: camera=%s top_score=%.3f threshold=%.3f identity=%s candidates=%d",
            camera_id, match.top_score, threshold, match.top_identity_id, match.candidate_count,
        )

        now = datetime.now(UTC)

        # 등록 인물 쿨다운: 동일 인물 × 동일 카메라 조합으로 짧은 시간 내 반복 기록 억제
        if match.is_registered and match.top_identity_id is not None:
            cooldown = settings.identity_recognition_cooldown_sec
            if identity_cooldown_guard.is_suppressed(
                match.top_identity_id, camera_id, cooldown, now
            ):
                logger.debug(
                    "identity cooldown skip: identity=%s elapsed=%.1fs",
                    match.top_identity_id,
                    identity_cooldown_guard.elapsed_sec(match.top_identity_id, camera_id, now),
                )
                await self._maybe_multishot_grow(
                    match.top_identity_id, match.top_score, embedding, now
                )
                return RecognitionLogResponse(
                    id=uuid4(),
                    camera_id=camera_id,
                    identity_id=match.top_identity_id,
                    identity_name="",
                    identity_type="",
                    confidence=match.top_score,
                    is_registered=True,
                    image_url=None,
                    created_at=now,
                )

        cluster_id: UUID | None = None
        if not match.is_registered and self._cluster_service is not None:
            try:
                cluster = await self._cluster_service.cluster_face(
                    embedding=embedding,
                    image_path=image_path,
                    quality_score=quality_score,
                    camera_id=camera_id,
                )
                cluster_id = cluster.id
            except Exception as exc:
                logger.warning("face cluster failed: %s", exc)

        # 미등록 인물 쿨다운: 동일 클러스터 × 동일 카메라 조합으로 반복 기록 억제
        if not match.is_registered and cluster_id is not None:
            cooldown = settings.unregistered_recognition_cooldown_sec
            if cluster_cooldown_guard.is_suppressed(cluster_id, camera_id, cooldown, now):
                logger.debug("cluster cooldown skip: cluster=%s", cluster_id)
                return RecognitionLogResponse(
                    id=uuid4(),
                    camera_id=camera_id,
                    identity_id=None,
                    identity_name="",
                    identity_type="",
                    confidence=match.top_score,
                    is_registered=False,
                    image_url=None,
                    created_at=now,
                )

        if match.is_registered:
            identity = await self._identity_repo.find_by_id(match.top_identity_id)
            log = RecognitionLog(
                camera_id=camera_id,
                identity_id=match.top_identity_id,
                identity_name=identity.name if identity else "Unknown",
                identity_type=identity.identity_type.value if identity else "UNKNOWN",
                confidence=match.top_score,
                is_registered=True,
                embedding=embedding,
                image_path=image_path,
                cluster_id=cluster_id,
            )
        else:
            log = RecognitionLog(
                camera_id=camera_id,
                identity_id=None,
                identity_name="미등록 인물",
                identity_type="UNKNOWN",
                confidence=match.top_score,
                is_registered=False,
                embedding=embedding,
                image_path=image_path,
                cluster_id=cluster_id,
            )

        saved = await self._log_repo.save(log)
        image_url = f"/{saved.image_path}" if saved.image_path else None

        response = RecognitionLogResponse(
            id=saved.id,
            camera_id=saved.camera_id,
            identity_id=saved.identity_id,
            identity_name=saved.identity_name,
            identity_type=saved.identity_type,
            confidence=saved.confidence,
            is_registered=saved.is_registered,
            image_url=image_url,
            created_at=saved.created_at,
        )

        await ws_manager.broadcast({
            "type": "recognition",
            "data": {
                "id": str(saved.id),
                "camera_id": str(saved.camera_id),
                "identity_name": saved.identity_name,
                "identity_type": saved.identity_type,
                "confidence": round(saved.confidence * 100, 1),
                "is_registered": saved.is_registered,
                "image_url": image_url,
                "created_at": saved.created_at.isoformat(),
            },
        })

        if saved.is_registered and saved.identity_id is not None:
            identity_cooldown_guard.mark(saved.identity_id, camera_id, saved.created_at)
            await self._maybe_multishot_grow(
                saved.identity_id, saved.confidence, embedding, saved.created_at
            )
        elif not saved.is_registered and cluster_id is not None:
            cluster_cooldown_guard.mark(cluster_id, camera_id, saved.created_at)

        if saved.is_registered and self._alert_rule_repo and self._danger_event_repo:
            await self._create_face_alert(saved)

        return response

    async def _maybe_multishot_grow(
        self,
        identity_id: UUID,
        top_score: float,
        embedding: list[float],
        now: datetime,
    ) -> None:
        if not settings.multishot_enabled:
            return
        if top_score < settings.multishot_min_score:
            return
        if top_score < settings.multishot_sim_low or top_score > settings.multishot_sim_high:
            return

        last = _identity_last_grown.get(identity_id)
        cooldown = settings.multishot_identity_cooldown_sec
        if last is not None and (now - last).total_seconds() < cooldown:
            return

        try:
            current = await self._embedding_store.count_by_identity(identity_id)
        except Exception as exc:
            logger.warning("multishot count failed identity=%s: %s", identity_id, exc)
            return
        if current >= settings.multishot_per_identity_max:
            return

        try:
            await self._embedding_store.store(uuid4(), identity_id, embedding)
            _identity_last_grown[identity_id] = now
            logger.info(
                "multishot grown identity=%s sim=%.3f bank=%d→%d",
                identity_id, top_score, current, current + 1,
            )
        except Exception as exc:
            logger.warning("multishot store failed identity=%s: %s", identity_id, exc)

    async def _create_face_alert(self, log: RecognitionLog) -> None:
        try:
            rules = await self._alert_rule_repo.find_active_rules()
            matching = [r for r in rules if r.enable_face_recognition]
            if not matching:
                return

            rule = matching[0]
            confidence_pct = round(log.confidence * 100, 1)
            type_label = {"EMPLOYEE": "임직원", "VISITOR": "방문객"}.get(log.identity_type, log.identity_type)
            description = (
                f"[{rule.name}] 얼굴 인식: {log.identity_name} ({type_label}), "
                f"신뢰도: {confidence_pct}%"
            )

            event = DangerEvent(
                camera_id=log.camera_id,
                danger_type=DangerType.FACE_RECOGNIZED,
                severity=Severity.MEDIUM,
                confidence=log.confidence,
                description=description,
            )
            saved_event = await self._danger_event_repo.save(event)

            if self._dispatcher is not None:
                await self._dispatcher.dispatch(saved_event, matching)
            else:
                logger.debug("dispatcher not configured; face alert event saved without broadcast")
        except Exception as e:
            logger.warning("Face alert creation failed: %s", e)


class ListRecognitionLogsUseCase:
    def __init__(self, log_repo: RecognitionLogPort):
        self._log_repo = log_repo

    async def execute(self, limit: int = 20) -> list[RecognitionLogResponse]:
        logs = await self._log_repo.find_recent(limit)
        return [
            RecognitionLogResponse(
                id=log.id,
                camera_id=log.camera_id,
                identity_id=log.identity_id,
                identity_name=log.identity_name,
                identity_type=log.identity_type,
                confidence=log.confidence,
                is_registered=log.is_registered,
                image_url=f"/{log.image_path}" if log.image_path else None,
                created_at=log.created_at,
            )
            for log in logs
        ]
