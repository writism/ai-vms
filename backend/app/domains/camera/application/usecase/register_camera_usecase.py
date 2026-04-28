import logging

from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.application.request.camera_request import RegisterCameraRequest
from app.domains.camera.application.response.camera_response import CameraResponse
from app.domains.camera.domain.entity.camera import Camera
from app.domains.stream.application.port.stream_port import StreamPort

logger = logging.getLogger(__name__)


class RegisterCameraUseCase:
    def __init__(self, repo: CameraRepositoryPort, stream_port: StreamPort | None = None):
        self._repo = repo
        self._stream_port = stream_port

    async def execute(self, request: RegisterCameraRequest) -> CameraResponse:
        camera = Camera(
            name=request.name,
            ip_address=request.ip_address,
            network_id=request.network_id,
            rtsp_url=request.rtsp_url,
            onvif_port=request.onvif_port,
        )
        saved = await self._repo.save(camera)
        if self._stream_port is not None and saved.rtsp_url:
            try:
                await self._stream_port.register_stream(str(saved.id), saved.rtsp_url)
            except Exception as exc:
                logger.warning("go2rtc register_stream failed for %s: %s", saved.id, exc)
        return CameraResponse.from_entity(saved)
