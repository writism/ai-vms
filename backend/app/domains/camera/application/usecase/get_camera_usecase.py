from uuid import UUID

from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.application.response.camera_response import CameraResponse
from app.domains.camera.application.service.camera_status_resolver import (
    resolve_status,
    resolve_status_for_many,
)
from app.domains.stream.application.port.stream_port import StreamPort


class GetCameraUseCase:
    def __init__(self, repo: CameraRepositoryPort, stream_port: StreamPort | None = None):
        self._repo = repo
        self._stream_port = stream_port

    async def execute(self, camera_id: UUID) -> CameraResponse | None:
        camera = await self._repo.find_by_id(camera_id)
        if camera is None:
            return None
        camera.status = await resolve_status(camera, self._stream_port)
        return CameraResponse.from_entity(camera)


class ListCamerasUseCase:
    def __init__(self, repo: CameraRepositoryPort, stream_port: StreamPort | None = None):
        self._repo = repo
        self._stream_port = stream_port

    async def execute(self) -> list[CameraResponse]:
        cameras = await self._repo.find_all()
        statuses = await resolve_status_for_many(cameras, self._stream_port)
        for camera, status in zip(cameras, statuses):
            camera.status = status
        return [CameraResponse.from_entity(c) for c in cameras]
