import logging
from datetime import UTC, datetime
from urllib.parse import quote, urlparse, urlunparse
from uuid import UUID

from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.application.port.discovery_port import CameraDiscoveryPort
from app.domains.camera.application.request.camera_request import FetchRtspUrlRequest, UpdateCameraRequest
from app.domains.camera.application.response.camera_response import CameraResponse
from app.domains.camera.application.service.camera_status_resolver import resolve_status
from app.domains.camera.domain.entity.camera import Camera
from app.domains.stream.application.port.stream_port import StreamPort

logger = logging.getLogger(__name__)


_TCP_TRANSPORT_KEYWORDS = ("tp-link", "tplink", "tapo")


def _needs_tcp_transport(manufacturer: str | None, onvif_port: int | None = None) -> bool:
    # Tapo cameras use ONVIF port 2020; also catch by manufacturer name
    if onvif_port == 2020:
        return True
    if not manufacturer:
        return False
    mfr = manufacturer.lower()
    return any(kw in mfr for kw in _TCP_TRANSPORT_KEYWORDS)


def _inject_credentials(rtsp_url: str, username: str, password: str) -> str:
    parsed = urlparse(rtsp_url)
    netloc = f"{quote(username, safe='')}:{quote(password, safe='')}@{parsed.hostname}"
    if parsed.port:
        netloc += f":{parsed.port}"
    return urlunparse(parsed._replace(netloc=netloc))


async def _sync_stream(stream_port: StreamPort | None, camera: Camera) -> None:
    if stream_port is None or not camera.rtsp_url:
        return
    try:
        await stream_port.register_stream(str(camera.id), camera.rtsp_url)
    except Exception as exc:
        logger.warning("go2rtc register_stream failed for %s: %s", camera.id, exc)


class UpdateCameraUseCase:
    def __init__(self, repo: CameraRepositoryPort, stream_port: StreamPort | None = None):
        self._repo = repo
        self._stream_port = stream_port

    async def execute(self, camera_id: UUID, request: UpdateCameraRequest) -> CameraResponse | None:
        camera = await self._repo.find_by_id(camera_id)
        if camera is None:
            return None
        rtsp_changed = False
        if request.name is not None:
            camera.name = request.name
        if request.rtsp_url is not None:
            camera.rtsp_url = request.rtsp_url
            rtsp_changed = True
        if request.onvif_port is not None:
            camera.onvif_port = request.onvif_port
        if request.manufacturer is not None:
            camera.manufacturer = request.manufacturer
        if request.model is not None:
            camera.model = request.model
        camera.updated_at = datetime.now(UTC)
        updated = await self._repo.update(camera)
        if rtsp_changed:
            await _sync_stream(self._stream_port, updated)
        updated.status = await resolve_status(updated, self._stream_port)
        return CameraResponse.from_entity(updated)


class FetchRtspUrlUseCase:
    def __init__(
        self,
        repo: CameraRepositoryPort,
        discovery: CameraDiscoveryPort,
        stream_port: StreamPort | None = None,
    ):
        self._repo = repo
        self._discovery = discovery
        self._stream_port = stream_port

    async def execute(self, camera_id: UUID, request: FetchRtspUrlRequest) -> CameraResponse | None:
        camera = await self._repo.find_by_id(camera_id)
        if camera is None:
            return None
        detail = await self._discovery.get_device_detail(
            ip=camera.ip_address,
            port=camera.onvif_port,
            username=request.username,
            password=request.password,
        )
        rtsp_url = detail.rtsp_url
        if rtsp_url and request.username and request.password:
            rtsp_url = _inject_credentials(rtsp_url, request.username, request.password)
        # Tapo (ONVIF port 2020): ONVIF auth often fails but RTSP stream is accessible.
        # Fall back to standard Tapo RTSP URL format when ONVIF returns nothing.
        if not rtsp_url and camera.onvif_port == 2020:
            base = f"rtsp://{camera.ip_address}:554/stream1"
            rtsp_url = _inject_credentials(base, request.username, request.password) if request.username and request.password else base
        if rtsp_url and _needs_tcp_transport(detail.manufacturer, camera.onvif_port):
            rtsp_url += "#tcp"
        camera.rtsp_url = rtsp_url
        if detail.manufacturer:
            camera.manufacturer = detail.manufacturer
        if detail.model:
            camera.model = detail.model
        camera.updated_at = datetime.now(UTC)
        updated = await self._repo.update(camera)
        await _sync_stream(self._stream_port, updated)
        updated.status = await resolve_status(updated, self._stream_port)
        return CameraResponse.from_entity(updated)
