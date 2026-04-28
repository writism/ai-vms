import logging

from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.application.port.discovery_port import CameraDiscoveryPort
from app.domains.camera.application.request.discovery_request import BatchRegisterCamerasRequest, DiscoverCamerasRequest
from app.domains.camera.application.response.camera_response import CameraResponse
from app.domains.camera.application.response.discovery_response import DiscoveredCameraResponse
from app.domains.camera.application.service.camera_status_resolver import (
    fetch_registered_stream_names,
    resolve_status,
)
from app.domains.camera.domain.entity.camera import Camera
from app.domains.stream.application.port.stream_port import StreamPort

logger = logging.getLogger(__name__)


class DiscoverCamerasUseCase:
    def __init__(self, discovery: CameraDiscoveryPort):
        self._discovery = discovery

    async def execute(self, request: DiscoverCamerasRequest) -> list[DiscoveredCameraResponse]:
        devices = await self._discovery.discover(timeout=request.timeout)
        return [
            DiscoveredCameraResponse(
                ip_address=d.ip_address,
                port=d.port,
                manufacturer=d.manufacturer,
                model=d.model,
                rtsp_url=d.rtsp_url,
                onvif_address=d.onvif_address,
            )
            for d in devices
        ]


class BatchRegisterCamerasUseCase:
    def __init__(self, repo: CameraRepositoryPort, stream_port: StreamPort | None = None):
        self._repo = repo
        self._stream_port = stream_port

    async def execute(self, request: BatchRegisterCamerasRequest) -> list[CameraResponse]:
        saved_cameras: list[Camera] = []
        for item in request.cameras:
            camera = Camera(
                name=item.name,
                ip_address=item.ip_address,
                network_id=request.network_id,
                rtsp_url=item.rtsp_url,
                onvif_port=item.onvif_port,
                manufacturer=item.manufacturer,
                model=item.model,
            )
            saved = await self._repo.save(camera)
            if self._stream_port is not None and saved.rtsp_url:
                try:
                    await self._stream_port.register_stream(str(saved.id), saved.rtsp_url)
                except Exception as exc:
                    logger.warning("go2rtc register_stream failed for %s: %s", saved.id, exc)
            saved_cameras.append(saved)

        registered = await fetch_registered_stream_names(self._stream_port)
        for cam in saved_cameras:
            cam.status = await resolve_status(cam, self._stream_port, registered)
        return [CameraResponse.from_entity(c) for c in saved_cameras]
