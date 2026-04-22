from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.application.request.camera_request import RegisterCameraRequest
from app.domains.camera.application.response.camera_response import CameraResponse
from app.domains.camera.domain.entity.camera import Camera


class RegisterCameraUseCase:
    def __init__(self, repo: CameraRepositoryPort):
        self._repo = repo

    async def execute(self, request: RegisterCameraRequest) -> CameraResponse:
        camera = Camera(
            name=request.name,
            ip_address=request.ip_address,
            network_id=request.network_id,
            rtsp_url=request.rtsp_url,
            onvif_port=request.onvif_port,
        )
        saved = await self._repo.save(camera)
        return CameraResponse.from_entity(saved)
