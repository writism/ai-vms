from uuid import UUID

from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.infrastructure.ai.frame_capture import CapturedFrame, frame_capture_service


class CaptureFrameUseCase:
    def __init__(self, camera_repo: CameraRepositoryPort):
        self._camera_repo = camera_repo

    async def execute(self, camera_id: UUID) -> CapturedFrame | None:
        camera = await self._camera_repo.find_by_id(camera_id)
        if camera is None or camera.rtsp_url is None:
            return None
        return await frame_capture_service.capture_frame(camera.rtsp_url, str(camera_id))
