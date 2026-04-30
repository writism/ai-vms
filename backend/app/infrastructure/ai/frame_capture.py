from __future__ import annotations

import asyncio
import logging
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

_FLUSH_GRABS = 1
_READ_RETRIES = 2
_MAX_CONSECUTIVE_FAILURES = 90


@dataclass
class CapturedFrame:
    camera_id: str
    frame: np.ndarray
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


_OPEN_TIMEOUT_MS = 5_000
_READ_TIMEOUT_MS = 5_000


class FrameCaptureService:
    def __init__(self) -> None:
        self._captures: dict[str, Any] = {}
        self._fail_counts: dict[str, int] = {}
        self._lock = threading.Lock()
        # Per-camera locks: serialise ALL VideoCapture operations for a given camera.
        # asyncio.Task.cancel() only cancels at the next await; the thread running
        # _read_persistent continues until it finishes. If the supervisor immediately
        # spawns a new capture task, both threads would hit the same cap object and
        # trigger the libavcodec/pthread_frame.c async_lock assertion. Holding the
        # per-camera lock for the entire read sequence prevents concurrent cap access.
        self._cam_locks: dict[str, threading.Lock] = {}

    def _get_cam_lock(self, camera_id: str) -> threading.Lock:
        with self._lock:
            if camera_id not in self._cam_locks:
                self._cam_locks[camera_id] = threading.Lock()
            return self._cam_locks[camera_id]

    def _resolve_url(self, rtsp_url: str, camera_id: str) -> str:
        if settings.frame_capture_use_relay:
            return f"rtsp://{settings.go2rtc_rtsp_host}:{settings.go2rtc_rtsp_port}/{camera_id}"
        return rtsp_url.split("#")[0]

    async def capture_frame(self, rtsp_url: str, camera_id: str) -> CapturedFrame | None:
        target = self._resolve_url(rtsp_url, camera_id)
        try:
            frame = await asyncio.get_running_loop().run_in_executor(
                None, self._read_persistent, camera_id, target
            )
            if frame is not None:
                return CapturedFrame(camera_id=camera_id, frame=frame)

            # persistent path failed → fall back to one-shot ffmpeg subprocess
            frame = await self._read_frame_ffmpeg(target)
            if frame is None:
                return None
            return CapturedFrame(camera_id=camera_id, frame=frame)
        except Exception as e:
            logger.warning("Frame capture failed for camera %s: %s", camera_id, e)
            return None

    def _read_persistent(self, camera_id: str, url: str):
        import cv2
        import time

        cam_lock = self._get_cam_lock(camera_id)
        # Hold the per-camera lock for the entire read sequence so a stale thread
        # from a cancelled task cannot run concurrently with the new task's thread.
        with cam_lock:
            cap = self._captures.get(camera_id)

            if cap is None or not cap.isOpened():
                new_cap = cv2.VideoCapture()
                # Set connection / read timeouts BEFORE open() so FFMPEG respects them.
                # Without this, an unreachable camera blocks the thread for 30+ seconds,
                # saturating the thread pool and freezing the entire event loop.
                new_cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, _OPEN_TIMEOUT_MS)
                new_cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, _READ_TIMEOUT_MS)
                new_cap.open(url, cv2.CAP_FFMPEG)
                new_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                if not new_cap.isOpened():
                    logger.debug("VideoCapture open failed: camera=%s", camera_id)
                    return None
                self._captures[camera_id] = new_cap
                self._fail_counts[camera_id] = 0
                cap = new_cap
                logger.info("VideoCapture opened: camera=%s url=%s", camera_id, url.split("@")[-1])

            # flush small buffer so read() returns the freshest available frame
            for _ in range(_FLUSH_GRABS):
                cap.grab()

            ret, frame = cap.read()
            for _ in range(_READ_RETRIES):
                if ret and frame is not None:
                    break
                # 카메라 frame 간격(15~30fps = 33~67ms)을 살짝 기다린 뒤 재시도
                time.sleep(0.04)
                ret, frame = cap.read()

            if not ret or frame is None:
                self._fail_counts[camera_id] = self._fail_counts.get(camera_id, 0) + 1
                fail_count = self._fail_counts[camera_id]
                if fail_count >= _MAX_CONSECUTIVE_FAILURES:
                    logger.warning(
                        "VideoCapture failed %d times — releasing camera=%s",
                        fail_count, camera_id,
                    )
                    self._release_camera_locked(camera_id)
                return None

            self._fail_counts[camera_id] = 0
            return frame

    def _release_camera(self, camera_id: str) -> None:
        cam_lock = self._get_cam_lock(camera_id)
        with cam_lock:
            self._release_camera_locked(camera_id)

    def _release_camera_locked(self, camera_id: str) -> None:
        """Must be called while holding the per-camera lock."""
        cap = self._captures.pop(camera_id, None)
        self._fail_counts.pop(camera_id, None)
        if cap is not None:
            try:
                cap.release()
            except Exception:
                pass

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
            logger.error("ffmpeg binary not found — fallback path unavailable")
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
            import numpy as np

            gray_curr = cv2.cvtColor(captured.frame, cv2.COLOR_BGR2GRAY)
            gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(gray_curr, gray_prev)
            mean_diff = float(np.mean(diff))
            has_motion = mean_diff > motion_threshold
            return captured, has_motion
        except Exception:
            return captured, True

    def shutdown(self) -> None:
        for camera_id in list(self._captures.keys()):
            self._release_camera(camera_id)


frame_capture_service = FrameCaptureService()
