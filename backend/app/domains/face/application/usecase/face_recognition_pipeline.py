from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.domain.entity.camera import CameraStatus
from app.domains.face.application.usecase.recognition_log_usecase import CreateRecognitionLogUseCase
from app.infrastructure.ai.frame_capture import FrameCaptureService
from app.infrastructure.ai.insightface_service import InsightFaceService
from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class FaceRecognitionWorker:
    def __init__(
        self,
        camera_repo: CameraRepositoryPort,
        frame_capture: FrameCaptureService,
        insightface: InsightFaceService,
        create_log_usecase: CreateRecognitionLogUseCase,
    ):
        self._camera_repo = camera_repo
        self._frame_capture = frame_capture
        self._insightface = insightface
        self._create_log = create_log_usecase
        self._prev_frames: dict[UUID, object] = {}

    async def process_camera(self, camera_id: UUID, rtsp_url: str) -> int:
        if settings.motion_gate_enabled:
            prev = self._prev_frames.get(camera_id)
            captured, has_motion = await self._frame_capture.capture_with_motion_gate(
                rtsp_url, str(camera_id), prev,
            )
            if captured is None:
                logger.debug("Frame capture failed: camera=%s", camera_id)
                return 0
            self._prev_frames[camera_id] = captured.frame
            if not has_motion:
                return 0
        else:
            captured = await self._frame_capture.capture_frame(rtsp_url, str(camera_id))
            if captured is None:
                logger.debug("Frame capture failed: camera=%s", camera_id)
                return 0

        detected_faces = await self._insightface.detect_and_embed(captured.frame)
        if detected_faces:
            logger.info("Detected %d face(s) from camera %s", len(detected_faces), camera_id)

        recognized = 0
        for face in detected_faces:
            if face.quality_score < settings.face_quality_threshold:
                logger.debug("Face skipped (low quality=%.2f): camera=%s", face.quality_score, camera_id)
                continue
            try:
                await self._create_log.execute(
                    camera_id=camera_id,
                    embedding=face.embedding,
                    threshold=settings.recognition_threshold,
                )
                recognized += 1
            except Exception as e:
                logger.warning("Recognition log failed for camera %s: %s", camera_id, e)

        return recognized

    async def run_cycle(self) -> int:
        cameras = await self._camera_repo.find_all()
        online_cameras = [
            c for c in cameras
            if c.status == CameraStatus.ONLINE and c.rtsp_url
        ]

        if not online_cameras:
            return -1

        total = 0
        for camera in online_cameras:
            try:
                count = await self.process_camera(camera.id, camera.rtsp_url)
                total += count
            except Exception as e:
                logger.warning("Face recognition failed for camera %s: %s", camera.name, e)

        return total


class FaceRecognitionScheduler:
    def __init__(self, worker: FaceRecognitionWorker, insightface: InsightFaceService):
        self._worker = worker
        self._insightface = insightface
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        if not self._insightface.is_loaded:
            logger.info("InsightFace not loaded — face recognition pipeline disabled")
            return

        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Face recognition pipeline started")

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
