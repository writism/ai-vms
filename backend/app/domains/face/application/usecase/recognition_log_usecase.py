import logging
from uuid import UUID

from app.domains.alert.application.port.alert_rule_repository_port import AlertRuleRepositoryPort
from app.domains.alert.application.port.danger_event_repository_port import DangerEventRepositoryPort
from app.domains.alert.application.response.alert_response import DangerEventResponse
from app.domains.alert.domain.entity.danger_event import DangerEvent, DangerType, Severity
from app.domains.face.application.port.face_embedding_port import FaceEmbeddingPort
from app.domains.face.application.port.identity_repository_port import IdentityRepositoryPort
from app.domains.face.application.port.recognition_log_port import RecognitionLogPort
from app.domains.face.application.response.face_response import RecognitionLogResponse
from app.domains.face.domain.entity.recognition_log import RecognitionLog
from app.infrastructure.event_bus.ws_manager import ws_manager

logger = logging.getLogger(__name__)


class CreateRecognitionLogUseCase:
    def __init__(
        self,
        log_repo: RecognitionLogPort,
        identity_repo: IdentityRepositoryPort,
        embedding_store: FaceEmbeddingPort,
        alert_rule_repo: AlertRuleRepositoryPort | None = None,
        danger_event_repo: DangerEventRepositoryPort | None = None,
    ):
        self._log_repo = log_repo
        self._identity_repo = identity_repo
        self._embedding_store = embedding_store
        self._alert_rule_repo = alert_rule_repo
        self._danger_event_repo = danger_event_repo

    async def execute(self, camera_id: UUID, embedding: list[float], threshold: float = 0.55) -> RecognitionLogResponse:
        results = await self._embedding_store.search(embedding=embedding, limit=1, threshold=threshold)

        if results and results[0].identity_id:
            match = results[0]
            identity = await self._identity_repo.find_by_id(match.identity_id)
            log = RecognitionLog(
                camera_id=camera_id,
                identity_id=match.identity_id,
                identity_name=identity.name if identity else "Unknown",
                identity_type=identity.identity_type.value if identity else "UNKNOWN",
                confidence=match.score,
                is_registered=True,
            )
        else:
            log = RecognitionLog(
                camera_id=camera_id,
                identity_id=None,
                identity_name="미등록 인물",
                identity_type="UNKNOWN",
                confidence=results[0].score if results else 0.0,
                is_registered=False,
            )

        saved = await self._log_repo.save(log)

        response = RecognitionLogResponse(
            id=saved.id,
            camera_id=saved.camera_id,
            identity_id=saved.identity_id,
            identity_name=saved.identity_name,
            identity_type=saved.identity_type,
            confidence=saved.confidence,
            is_registered=saved.is_registered,
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
                "created_at": saved.created_at.isoformat(),
            },
        })

        if saved.is_registered and self._alert_rule_repo and self._danger_event_repo:
            await self._create_face_alert(saved)

        return response

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

            event_response = DangerEventResponse.from_entity(saved_event)
            await ws_manager.broadcast({
                "type": "DANGER_EVENT",
                "data": event_response.model_dump(mode="json"),
            })
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
                created_at=log.created_at,
            )
            for log in logs
        ]
