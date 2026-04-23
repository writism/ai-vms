from datetime import datetime
from urllib.parse import quote, urlparse, urlunparse
from uuid import UUID

from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.application.port.discovery_port import CameraDiscoveryPort
from app.domains.camera.application.request.camera_request import FetchRtspUrlRequest, UpdateCameraRequest
from app.domains.camera.application.response.camera_response import CameraResponse


def _inject_credentials(rtsp_url: str, username: str, password: str) -> str:
    parsed = urlparse(rtsp_url)
    netloc = f"{quote(username, safe='')}:{quote(password, safe='')}@{parsed.hostname}"
    if parsed.port:
        netloc += f":{parsed.port}"
    return urlunparse(parsed._replace(netloc=netloc))


class UpdateCameraUseCase:
    def __init__(self, repo: CameraRepositoryPort):
        self._repo = repo

    async def execute(self, camera_id: UUID, request: UpdateCameraRequest) -> CameraResponse | None:
        camera = await self._repo.find_by_id(camera_id)
        if camera is None:
            return None
        if request.name is not None:
            camera.name = request.name
        if request.rtsp_url is not None:
            camera.rtsp_url = request.rtsp_url
        if request.onvif_port is not None:
            camera.onvif_port = request.onvif_port
        if request.manufacturer is not None:
            camera.manufacturer = request.manufacturer
        if request.model is not None:
            camera.model = request.model
        camera.updated_at = datetime.now()
        updated = await self._repo.update(camera)
        return CameraResponse.from_entity(updated)


class FetchRtspUrlUseCase:
    def __init__(self, repo: CameraRepositoryPort, discovery: CameraDiscoveryPort):
        self._repo = repo
        self._discovery = discovery

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
        camera.rtsp_url = rtsp_url
        if detail.manufacturer:
            camera.manufacturer = detail.manufacturer
        if detail.model:
            camera.model = detail.model
        camera.updated_at = datetime.now()
        updated = await self._repo.update(camera)
        return CameraResponse.from_entity(updated)
