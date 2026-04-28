from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from app.domains.face.application.usecase.face_recognition_pipeline import (
    FaceRecognitionScheduler,
    FaceRecognitionWorker,
)
from app.infrastructure.ai.frame_capture import frame_capture_service
from app.infrastructure.ai.insightface_service import insightface_service
from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

_scheduler: FaceRecognitionScheduler | None = None


class _DbSessionWorker:
    """Runs face recognition with a fresh DB session per cycle."""

    def __init__(self) -> None:
        self._prev_frames: dict[UUID, object] = {}
        self._running = True

    async def run_cycle(self) -> int:
        from app.infrastructure.database.session import async_session_factory
        from app.domains.camera.adapter.outbound.persistence.sqlalchemy_camera_repository import SqlAlchemyCameraRepository
        from app.domains.face.adapter.outbound.persistence.sqlalchemy_identity_repository import SqlAlchemyIdentityRepository
        from app.domains.face.adapter.outbound.persistence.sqlalchemy_recognition_log_repository import SqlAlchemyRecognitionLogRepository
        from app.domains.alert.adapter.outbound.persistence.sqlalchemy_alert_rule_repository import SqlAlchemyAlertRuleRepository
        from app.domains.alert.adapter.outbound.persistence.sqlalchemy_danger_event_repository import SqlAlchemyDangerEventRepository
        from app.domains.face.adapter.outbound.external.qdrant_embedding_adapter import QdrantEmbeddingAdapter
        from app.domains.face.application.usecase.recognition_log_usecase import CreateRecognitionLogUseCase

        embedding_store = QdrantEmbeddingAdapter()

        async with async_session_factory() as session:
            async with session.begin():
                camera_repo = SqlAlchemyCameraRepository(session)
                worker = FaceRecognitionWorker(
                    camera_repo=camera_repo,
                    frame_capture=frame_capture_service,
                    insightface=insightface_service,
                    create_log_usecase=CreateRecognitionLogUseCase(
                        log_repo=SqlAlchemyRecognitionLogRepository(session),
                        identity_repo=SqlAlchemyIdentityRepository(session),
                        embedding_store=embedding_store,
                        alert_rule_repo=SqlAlchemyAlertRuleRepository(session),
                        danger_event_repo=SqlAlchemyDangerEventRepository(session),
                    ),
                )
                worker._prev_frames = self._prev_frames
                count = await worker.run_cycle()
                self._prev_frames = worker._prev_frames
                return count


class _DbScheduler:
    def __init__(self) -> None:
        self._worker = _DbSessionWorker()
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Face recognition pipeline started (DB mode)")

    async def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Face recognition pipeline stopped")

    async def _loop(self) -> None:
        NO_CAMERA_INTERVAL = 10.0
        while self._running:
            try:
                count = await self._worker.run_cycle()
                if count < 0:
                    interval = NO_CAMERA_INTERVAL
                elif count > 0:
                    interval = settings.process_interval_active
                else:
                    interval = settings.process_interval_idle
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Face recognition cycle error: %s", e)
                await asyncio.sleep(settings.process_interval_idle)


async def start_face_recognition_pipeline() -> None:
    global _scheduler

    if not settings.face_recognition_pipeline_enabled:
        logger.info("Face recognition pipeline disabled by config")
        return

    if not insightface_service.is_loaded:
        logger.info("InsightFace not loaded — skipping face recognition pipeline")
        return

    if not settings.use_database:
        logger.info("Face recognition pipeline requires database mode — skipping")
        return

    _scheduler = _DbScheduler()
    await _scheduler.start()


async def stop_face_recognition_pipeline() -> None:
    global _scheduler
    if _scheduler:
        await _scheduler.stop()
        _scheduler = None
