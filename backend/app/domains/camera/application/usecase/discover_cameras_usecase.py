from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.application.port.discovery_port import CameraDiscoveryPort
from app.domains.camera.application.request.discovery_request import BatchRegisterCamerasRequest, DiscoverCamerasRequest
from app.domains.camera.application.response.camera_response import CameraResponse
from app.domains.camera.application.response.discovery_response import DiscoveredCameraResponse
from app.domains.camera.domain.entity.camera import Camera


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
    def __init__(self, repo: CameraRepositoryPort):
        self._repo = repo

    async def execute(self, request: BatchRegisterCamerasRequest) -> list[CameraResponse]:
        results: list[CameraResponse] = []
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
            results.append(CameraResponse.from_entity(saved))
        return results
