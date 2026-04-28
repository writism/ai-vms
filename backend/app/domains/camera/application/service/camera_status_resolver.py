import asyncio
import logging
from urllib.parse import urlparse

from app.domains.camera.domain.entity.camera import Camera, CameraStatus
from app.domains.stream.application.port.stream_port import StreamPort

logger = logging.getLogger(__name__)


async def _check_rtsp_reachable(camera: Camera) -> bool:
    if not camera.rtsp_url:
        return False
    try:
        parsed = urlparse(camera.rtsp_url)
        host = parsed.hostname or camera.ip_address
        port = parsed.port or 554
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=2
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


async def fetch_registered_stream_names(stream_port: StreamPort | None) -> set[str] | None:
    if stream_port is None:
        return None
    try:
        streams = await stream_port.list_streams()
    except Exception as exc:
        logger.warning("go2rtc list_streams unavailable, status falls back to RTSP-only: %s", exc)
        return None
    return set(streams.keys())


async def resolve_status(
    camera: Camera,
    stream_port: StreamPort | None,
    registered_streams: set[str] | None = None,
) -> CameraStatus:
    if not camera.rtsp_url:
        return CameraStatus.OFFLINE

    if registered_streams is None and stream_port is not None:
        registered_streams = await fetch_registered_stream_names(stream_port)

    reachable = await _check_rtsp_reachable(camera)
    if not reachable:
        return CameraStatus.OFFLINE

    if registered_streams is None:
        return CameraStatus.ONLINE

    return CameraStatus.ONLINE if str(camera.id) in registered_streams else CameraStatus.OFFLINE


async def resolve_status_for_many(
    cameras: list[Camera],
    stream_port: StreamPort | None,
) -> list[CameraStatus]:
    registered = await fetch_registered_stream_names(stream_port)
    effective_port = stream_port if registered is not None else None
    results = await asyncio.gather(
        *[resolve_status(c, effective_port, registered) for c in cameras],
        return_exceptions=True,
    )
    statuses: list[CameraStatus] = []
    for camera, status in zip(cameras, results):
        if isinstance(status, BaseException):
            logger.warning("status resolve failed for %s: %s", camera.id, status)
            statuses.append(CameraStatus.OFFLINE)
        else:
            statuses.append(status)
    return statuses
