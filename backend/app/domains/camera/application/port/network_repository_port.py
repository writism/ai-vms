from abc import ABC, abstractmethod
from uuid import UUID

from app.domains.camera.domain.entity.network import Network


class NetworkRepositoryPort(ABC):
    @abstractmethod
    async def save(self, network: Network) -> Network: ...

    @abstractmethod
    async def find_by_id(self, network_id: UUID) -> Network | None: ...

    @abstractmethod
    async def find_all(self) -> list[Network]: ...

    @abstractmethod
    async def delete(self, network_id: UUID) -> bool: ...
