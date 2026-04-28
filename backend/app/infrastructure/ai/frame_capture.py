from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CapturedFrame:
    camera_id: str
    frame: np.ndarray
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class FrameCaptureService:
    def __init__(self) -> None:
        self._captures: dict[str, object] = {}

    async def capture_frame(self, rtsp_url: str, camera_id: str) -> CapturedFrame | None:
        try:
            import cv2

            loop = asyncio.get_event_loop()
            frame = await loop.run_in_executor(None, self._read_frame, rtsp_url)
            if frame is None:
                return None
            return CapturedFrame(camera_id=camera_id, frame=frame)
        except Exception as e:
            logger.warning("Frame capture failed for camera %s: %s", camera_id, e)
            return None

    def _read_frame(self, rtsp_url: str) -> np.ndarray | None:
        import cv2

        clean_url = rtsp_url.split("#")[0]
        cap = cv2.VideoCapture(clean_url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)
        if not cap.isOpened():
            logger.debug("RTSP open failed: %s", rtsp_url.split("@")[-1])
            return None
        try:
            for _ in range(settings.frame_skip):
                cap.grab()
            ret, frame = cap.read()
            return frame if ret else None
        finally:
            cap.release()

    async def capture_with_motion_gate(
        self,
        rtsp_url: str,
        camera_id: str,
        prev_frame: np.ndarray | None = None,
        motion_threshold: float = 25.0,
    ) -> tuple[CapturedFrame | None, bool]:
        captured = await self.capture_frame(rtsp_url, camera_id)
        if captured is None:
            return None, False

        if not settings.motion_gate_enabled or prev_frame is None:
            return captured, True

        try:
            import cv2

            gray_curr = cv2.cvtColor(captured.frame, cv2.COLOR_BGR2GRAY)
            gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(gray_curr, gray_prev)
            mean_diff = float(np.mean(diff))
            has_motion = mean_diff > motion_threshold
            return captured, has_motion
        except Exception:
            return captured, True


frame_capture_service = FrameCaptureService()
