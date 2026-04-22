from abc import ABC, abstractmethod
from uuid import UUID

from app.domains.camera.domain.entity.camera import Camera


class CameraRepositoryPort(ABC):
    @abstractmethod
    async def save(self, camera: Camera) -> Camera: ...

    @abstractmethod
    async def find_by_id(self, camera_id: UUID) -> Camera | None: ...

    @abstractmethod
    async def find_all(self) -> list[Camera]: ...

    @abstractmethod
    async def find_by_network_id(self, network_id: UUID) -> list[Camera]: ...

    @abstractmethod
    async def delete(self, camera_id: UUID) -> bool: ...
