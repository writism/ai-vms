from __future__ import annotations

import asyncio
import logging
import os
import uuid as uuid_mod
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.infrastructure.ai.frame_capture import frame_capture_service
from app.infrastructure.ai.insightface_service import DetectedFace, insightface_service
from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

SNAPSHOT_DIR = "uploads/snapshots"
_SUPERVISE_INTERVAL = 5.0
_CAPTURE_BACKOFF_ON_FAIL = 0.5
_MOTION_THRESHOLD = 25.0


def _save_face_snapshot(frame, face: DetectedFace) -> str | None:
    try:
        import cv2
        import numpy as np

        h, w = frame.shape[:2]
        x1, y1, x2, y2 = face.bbox
        bw = x2 - x1
        bh = y2 - y1

        # 얼굴이 프레임 대비 너무 크면 (카메라에 너무 가까운 경우) 저장하지 않음
        max_ratio = settings.face_snapshot_max_face_ratio
        if bw > w * max_ratio or bh > h * max_ratio:
            logger.debug(
                "snapshot skipped — face too large (%.0f%%×%.0f%% of frame)",
                bw / w * 100, bh / h * 100,
            )
            return None

        # 선명도 검사: Laplacian 분산이 기준 미만이면 블러로 간주하고 저장하지 않음
        face_crop_raw = frame[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
        if face_crop_raw.size > 0:
            gray = cv2.cvtColor(face_crop_raw, cv2.COLOR_BGR2GRAY)
            sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            if sharpness < settings.face_snapshot_min_sharpness:
                logger.debug(
                    "snapshot skipped — too blurry (sharpness=%.1f < %.1f)",
                    sharpness, settings.face_snapshot_min_sharpness,
                )
                return None

        pad = settings.face_snapshot_padding
        px = int(bw * pad)
        py = int(bh * pad)
        cx1 = max(0, x1 - px)
        cy1 = max(0, y1 - py)
        cx2 = min(w, x2 + px)
        cy2 = min(h, y2 + py)
        crop = frame[cy1:cy2, cx1:cx2]
        if crop.size == 0:
            return None

        # 얼굴이 작으면(원거리 카메라) Lanczos 업스케일로 최소 해상도 보장
        min_dim = settings.face_snapshot_min_output_size
        ch, cw = crop.shape[:2]
        if ch < min_dim or cw < min_dim:
            scale = min_dim / min(ch, cw)
            new_w = max(min_dim, int(cw * scale))
            new_h = max(min_dim, int(ch * scale))
            crop = cv2.resize(crop, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        date_dir = datetime.now(UTC).strftime("%Y%m%d")
        target_dir = os.path.join(SNAPSHOT_DIR, date_dir)
        os.makedirs(target_dir, exist_ok=True)
        filename = f"{uuid_mod.uuid4()}.jpg"
        relative_path = os.path.join(target_dir, filename)
        cv2.imwrite(relative_path, crop, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        return relative_path
    except Exception as exc:
        logger.warning("snapshot save failed: %s", exc)
        return None


class _FaceRecognitionEngine:
    """카메라당 capture task + 단일 process consumer 구조.

    Queue(maxsize=N) stale-drop으로 항상 최신 프레임만 처리. 카메라 추가/삭제는
    supervise loop가 5초 주기로 따라잡는다. multi-camera fan-out + go2rtc relay
    토글은 frame_capture_service가 처리하므로 그대로 유지된다.
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue = asyncio.Queue(
            maxsize=max(1, settings.pipeline_queue_maxsize)
        )
        self._capture_tasks: dict[UUID, asyncio.Task] = {}
        self._consumer_task: asyncio.Task | None = None
        self._supervisor_task: asyncio.Task | None = None
        self._prev_frames: dict[UUID, Any] = {}
        self._running = False
        self._merge_cycle = 0
        # best-frame-in-window state per camera
        self._window_best: dict[UUID, tuple[Any, datetime, float]] = {}  # cam → (frame, ts, sharpness)
        self._window_start: dict[UUID, float] = {}  # cam → monotonic time

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._consumer_task = asyncio.create_task(self._consume_loop())
        self._supervisor_task = asyncio.create_task(self._supervise_loop())
        logger.info(
            "Face recognition engine started (queue=%d, capture_interval=%.2fs)",
            self._queue.maxsize, settings.pipeline_capture_interval,
        )

    async def stop(self) -> None:
        self._running = False
        for task in list(self._capture_tasks.values()):
            task.cancel()
        if self._consumer_task and not self._consumer_task.done():
            self._consumer_task.cancel()
        if self._supervisor_task and not self._supervisor_task.done():
            self._supervisor_task.cancel()
        for task in list(self._capture_tasks.values()) + [
            t for t in (self._consumer_task, self._supervisor_task) if t is not None
        ]:
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass
        self._capture_tasks.clear()
        logger.info("Face recognition engine stopped")

    # ---- supervise -------------------------------------------------

    async def _supervise_loop(self) -> None:
        while self._running:
            try:
                online = await self._fetch_online_cameras()
                online_map: dict[UUID, str] = {c.id: c.rtsp_url for c in online}

                for cam_id, rtsp in online_map.items():
                    existing = self._capture_tasks.get(cam_id)
                    if existing is None or existing.done():
                        self._capture_tasks[cam_id] = asyncio.create_task(
                            self._capture_loop(cam_id, rtsp)
                        )
                        logger.info("capture task started camera=%s", cam_id)

                for cam_id in list(self._capture_tasks.keys()):
                    if cam_id not in online_map:
                        task = self._capture_tasks.pop(cam_id)
                        task.cancel()
                        # _release_camera 를 여기서 호출하지 않음.
                        # _read_persistent 스레드가 동일 VideoCapture 를 사용 중일 수 있어
                        # 동시 release → FFMPEG 데드락 발생. 실패 감지 시 _read_persistent 내부에서
                        # 자체 정리된다.
                        self._prev_frames.pop(cam_id, None)
                        logger.info("capture task cancelled camera=%s", cam_id)

                # 12 사이클(약 60초)마다 유사 클러스터 병합
                self._merge_cycle += 1
                if self._merge_cycle % 12 == 0:
                    await self._run_cluster_merge()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning("supervise loop error: %s", exc)
            try:
                await asyncio.sleep(_SUPERVISE_INTERVAL)
            except asyncio.CancelledError:
                break

    async def _run_cluster_merge(self) -> None:
        try:
            from app.domains.face.adapter.outbound.persistence.sqlalchemy_face_cluster_repository import (
                SqlAlchemyFaceClusterRepository,
            )
            from app.domains.face.application.service.face_cluster_service import FaceClusterService
            from app.infrastructure.database import orm_models  # noqa: F401
            from app.infrastructure.database.session import async_session_factory

            async with async_session_factory() as session:
                async with session.begin():
                    svc = FaceClusterService(SqlAlchemyFaceClusterRepository(session))
                    count = await svc.merge_similar_clusters()
                    if count > 0:
                        logger.info("cluster merge pass: merged %d cluster(s)", count)
        except Exception as exc:
            logger.warning("cluster merge error: %s", exc)

    async def _fetch_online_cameras(self) -> list[Any]:
        from app.domains.camera.adapter.outbound.persistence.sqlalchemy_camera_repository import (
            SqlAlchemyCameraRepository,
        )
        from app.domains.camera.application.service.camera_status_resolver import (
            resolve_status_for_many,
        )
        from app.domains.camera.domain.entity.camera import CameraStatus
        from app.domains.stream.adapter.outbound.external.go2rtc_stream_adapter import (
            Go2RtcStreamAdapter,
        )
        from app.infrastructure.database import orm_models  # noqa: F401
        from app.infrastructure.database.session import async_session_factory

        stream_port = Go2RtcStreamAdapter()
        # DB 세션은 카메라 목록 조회 후 즉시 반납 — go2rtc HTTP 요청 중 풀 점유 방지
        async with async_session_factory() as session:
            repo = SqlAlchemyCameraRepository(session)
            cameras = await repo.find_all()
        candidates = [c for c in cameras if c.rtsp_url]
        if not candidates:
            return []
        statuses = await resolve_status_for_many(candidates, stream_port)
        return [
            cam
            for cam, status in zip(candidates, statuses)
            if status == CameraStatus.ONLINE
        ]

    # ---- capture ---------------------------------------------------

    @staticmethod
    def _frame_sharpness(frame: Any) -> float:
        try:
            import cv2
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return float(cv2.Laplacian(gray, cv2.CV_64F).var())
        except Exception:
            return 0.0

    async def _capture_loop(self, camera_id: UUID, rtsp_url: str) -> None:
        import time

        window = max(0.1, settings.pipeline_best_frame_window)
        try:
            while self._running:
                captured = await frame_capture_service.capture_frame(
                    rtsp_url, str(camera_id)
                )
                if captured is None:
                    await asyncio.sleep(_CAPTURE_BACKOFF_ON_FAIL)
                    continue

                if settings.motion_gate_enabled and not self._has_motion(
                    camera_id, captured.frame
                ):
                    self._prev_frames[camera_id] = captured.frame
                    await asyncio.sleep(settings.pipeline_capture_interval)
                    continue
                self._prev_frames[camera_id] = captured.frame

                now_mono = time.monotonic()
                sharpness = self._frame_sharpness(captured.frame)

                # accumulate best frame in window
                prev_best = self._window_best.get(camera_id)
                if prev_best is None or sharpness > prev_best[2]:
                    self._window_best[camera_id] = (captured.frame, captured.timestamp, sharpness)
                if camera_id not in self._window_start:
                    self._window_start[camera_id] = now_mono

                # flush window when time expires
                if now_mono - self._window_start[camera_id] >= window:
                    best_frame, best_ts, best_sharp = self._window_best.pop(camera_id)
                    self._window_start.pop(camera_id, None)
                    self._stale_drop_put(camera_id, best_frame, best_ts)
                    logger.debug(
                        "best-frame flush camera=%s sharpness=%.1f", camera_id, best_sharp
                    )

                await asyncio.sleep(settings.pipeline_capture_interval)
        except asyncio.CancelledError:
            return
        except Exception as exc:
            logger.warning("capture loop error camera=%s: %s", camera_id, exc)

    def _has_motion(self, camera_id: UUID, frame: Any) -> bool:
        prev = self._prev_frames.get(camera_id)
        if prev is None:
            return True
        try:
            import cv2
            import numpy as np

            gp = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
            gc = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            diff = float(np.mean(cv2.absdiff(gc, gp)))
            return diff > _MOTION_THRESHOLD
        except Exception:
            return True

    def _stale_drop_put(self, camera_id: UUID, frame: Any, ts: datetime) -> None:
        if self._queue.full():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except asyncio.QueueEmpty:
                pass
        try:
            self._queue.put_nowait((camera_id, frame, ts))
        except asyncio.QueueFull:
            pass

    # ---- consume ---------------------------------------------------

    async def _consume_loop(self) -> None:
        while self._running:
            try:
                camera_id, frame, _ts = await self._queue.get()
                try:
                    await self._process_frame(camera_id, frame)
                finally:
                    self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning("consume loop error: %s", exc)

    async def _process_frame(self, camera_id: UUID, frame: Any) -> None:
        from app.domains.alert.adapter.outbound.persistence.sqlalchemy_alert_rule_repository import (
            SqlAlchemyAlertRuleRepository,
        )
        from app.domains.alert.adapter.outbound.persistence.sqlalchemy_danger_event_repository import (
            SqlAlchemyDangerEventRepository,
        )
        from app.domains.face.adapter.outbound.external.qdrant_embedding_adapter import (
            QdrantEmbeddingAdapter,
        )
        from app.domains.face.adapter.outbound.persistence.sqlalchemy_face_cluster_repository import (
            SqlAlchemyFaceClusterRepository,
        )
        from app.domains.face.adapter.outbound.persistence.sqlalchemy_identity_repository import (
            SqlAlchemyIdentityRepository,
        )
        from app.domains.face.adapter.outbound.persistence.sqlalchemy_recognition_log_repository import (
            SqlAlchemyRecognitionLogRepository,
        )
        from app.domains.face.application.service.face_cluster_service import (
            FaceClusterService,
        )
        from app.domains.face.application.usecase.recognition_log_usecase import (
            CreateRecognitionLogUseCase,
        )
        from app.domains.event.domain.entity.event import Event, EventType
        from app.domains.event.adapter.outbound.persistence.sqlalchemy_event_repository import (
            SqlAlchemyEventRepository,
        )
        from app.infrastructure.database import orm_models  # noqa: F401
        from app.infrastructure.database.session import async_session_factory
        from app.infrastructure.event_bus.notification_dispatcher import (
            notification_dispatcher,
        )

        detected_faces = await insightface_service.detect_and_embed(frame)
        if not detected_faces:
            return

        usable = [
            f for f in detected_faces if f.quality_score >= settings.face_quality_threshold
        ]
        if not usable:
            logger.debug(
                "all %d face(s) below quality threshold camera=%s",
                len(detected_faces), camera_id,
            )
            return

        logger.info(
            "Detected %d face(s) (usable=%d) from camera %s",
            len(detected_faces), len(usable), camera_id,
        )

        embedding_store = QdrantEmbeddingAdapter()
        async with async_session_factory() as session:
            async with session.begin():
                cluster_service = FaceClusterService(
                    SqlAlchemyFaceClusterRepository(session)
                )
                usecase = CreateRecognitionLogUseCase(
                    log_repo=SqlAlchemyRecognitionLogRepository(session),
                    identity_repo=SqlAlchemyIdentityRepository(session),
                    embedding_store=embedding_store,
                    alert_rule_repo=SqlAlchemyAlertRuleRepository(session),
                    danger_event_repo=SqlAlchemyDangerEventRepository(session),
                    dispatcher=notification_dispatcher,
                    cluster_service=cluster_service,
                )
                event_repo = SqlAlchemyEventRepository(session)

                loop = asyncio.get_event_loop()
                for face in usable:
                    snapshot_path = await loop.run_in_executor(
                        None, _save_face_snapshot, frame, face
                    )
                    if snapshot_path is None:
                        logger.debug("recognition log skipped — no snapshot camera=%s", camera_id)
                        continue
                    try:
                        response = await usecase.execute(
                            camera_id=camera_id,
                            embedding=face.embedding,
                            threshold=settings.recognition_threshold,
                            image_path=snapshot_path,
                            quality_score=face.quality_score,
                        )
                        event_type = (
                            EventType.FACE_RECOGNIZED
                            if response.is_registered
                            else EventType.FACE_UNIDENTIFIED
                        )
                        cam_short = str(camera_id)[:8]
                        if response.is_registered:
                            conf_pct = response.confidence * 100 if response.confidence <= 1.0 else response.confidence
                            desc = f"{response.identity_name} 인식 (cam: {cam_short}, {conf_pct:.1f}%)"
                        else:
                            desc = f"미등록 인물 감지 (cam: {cam_short})"
                        await event_repo.save(Event(
                            event_type=event_type,
                            camera_id=camera_id,
                            identity_id=response.identity_id,
                            description=desc,
                            snapshot_path=snapshot_path,
                        ))
                    except Exception as exc:
                        logger.warning(
                            "recognition log failed camera=%s: %s", camera_id, exc
                        )


_engine: _FaceRecognitionEngine | None = None


async def start_face_recognition_pipeline() -> None:
    global _engine

    if not settings.face_recognition_pipeline_enabled:
        logger.info("Face recognition pipeline disabled by config")
        return

    if not insightface_service.is_loaded:
        logger.info("InsightFace not loaded — skipping face recognition pipeline")
        return

    if not settings.use_database:
        logger.info("Face recognition pipeline requires database mode — skipping")
        return

    _engine = _FaceRecognitionEngine()
    await _engine.start()


async def stop_face_recognition_pipeline() -> None:
    global _engine
    if _engine:
        await _engine.stop()
        _engine = None
