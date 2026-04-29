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

    def _resolve_url(self, rtsp_url: str, camera_id: str) -> str:
        if settings.frame_capture_use_relay:
            return f"rtsp://{settings.go2rtc_rtsp_host}:{settings.go2rtc_rtsp_port}/{camera_id}"
        return rtsp_url.split("#")[0]

    async def capture_frame(self, rtsp_url: str, camera_id: str) -> CapturedFrame | None:
        try:
            target = self._resolve_url(rtsp_url, camera_id)
            frame = await self._read_frame_ffmpeg(target)
            if frame is None and settings.frame_capture_use_relay:
                await asyncio.sleep(0.5)
                frame = await self._read_frame_ffmpeg(target)
            if frame is None:
                return None
            return CapturedFrame(camera_id=camera_id, frame=frame)
        except Exception as e:
            logger.warning("Frame capture failed for camera %s: %s", camera_id, e)
            return None

    async def _read_frame_ffmpeg(self, url: str) -> np.ndarray | None:
        import cv2
        import numpy as np

        cmd = [
            "ffmpeg",
            "-nostdin",
            "-loglevel", "error",
            "-rtsp_transport", "tcp",
            "-stimeout", "8000000",
            "-i", url,
            "-map", "0:v",
            "-frames:v", "1",
            "-f", "image2pipe",
            "-vcodec", "mjpeg",
            "-",
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=12)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                logger.debug("ffmpeg timeout: %s", url.split("@")[-1])
                return None
        except FileNotFoundError:
            logger.error("ffmpeg binary not found in container — install required")
            return None

        if proc.returncode != 0 or not stdout:
            logger.debug(
                "ffmpeg capture failed (rc=%s): %s — %s",
                proc.returncode,
                url.split("@")[-1],
                (stderr or b"").decode(errors="ignore").strip().splitlines()[-1:],
            )
            return None

        arr = np.frombuffer(stdout, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return frame

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
