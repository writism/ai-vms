from uuid import UUID

from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.application.response.camera_response import CameraResponse


class GetCameraUseCase:
    def __init__(self, repo: CameraRepositoryPort):
        self._repo = repo

    async def execute(self, camera_id: UUID) -> CameraResponse | None:
        camera = await self._repo.find_by_id(camera_id)
        if camera is None:
            return None
        return CameraResponse.from_entity(camera)


class ListCamerasUseCase:
    def __init__(self, repo: CameraRepositoryPort):
        self._repo = repo

    async def execute(self) -> list[CameraResponse]:
        cameras = await self._repo.find_all()
        return [CameraResponse.from_entity(c) for c in cameras]
