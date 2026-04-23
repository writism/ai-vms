import asyncio
import logging
from urllib.parse import urlparse
from uuid import UUID

from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.application.response.camera_response import CameraResponse
from app.domains.camera.domain.entity.camera import Camera

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


class GetCameraUseCase:
    def __init__(self, repo: CameraRepositoryPort):
        self._repo = repo

    async def execute(self, camera_id: UUID) -> CameraResponse | None:
        camera = await self._repo.find_by_id(camera_id)
        if camera is None:
            return None
        camera.status = "ONLINE" if await _check_rtsp_reachable(camera) else "OFFLINE"
        return CameraResponse.from_entity(camera)


class ListCamerasUseCase:
    def __init__(self, repo: CameraRepositoryPort):
        self._repo = repo

    async def execute(self) -> list[CameraResponse]:
        cameras = await self._repo.find_all()
        results = await asyncio.gather(
            *[_check_rtsp_reachable(c) for c in cameras],
            return_exceptions=True,
        )
        for camera, reachable in zip(cameras, results):
            camera.status = "ONLINE" if reachable is True else "OFFLINE"
        return [CameraResponse.from_entity(c) for c in cameras]
