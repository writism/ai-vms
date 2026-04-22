from uuid import UUID

from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.domain.entity.camera import Camera


class InMemoryCameraRepository(CameraRepositoryPort):
    def __init__(self) -> None:
        self._store: dict[UUID, Camera] = {}

    async def save(self, camera: Camera) -> Camera:
        self._store[camera.id] = camera
        return camera

    async def find_by_id(self, camera_id: UUID) -> Camera | None:
        return self._store.get(camera_id)

    async def find_all(self) -> list[Camera]:
        return list(self._store.values())

    async def find_by_network_id(self, network_id: UUID) -> list[Camera]:
        return [c for c in self._store.values() if c.network_id == network_id]

    async def delete(self, camera_id: UUID) -> bool:
        return self._store.pop(camera_id, None) is not None
