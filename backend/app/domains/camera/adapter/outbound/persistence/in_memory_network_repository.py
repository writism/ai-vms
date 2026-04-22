from uuid import UUID

from app.domains.camera.application.port.network_repository_port import NetworkRepositoryPort
from app.domains.camera.domain.entity.network import Network


class InMemoryNetworkRepository(NetworkRepositoryPort):
    def __init__(self) -> None:
        self._store: dict[UUID, Network] = {}

    async def save(self, network: Network) -> Network:
        self._store[network.id] = network
        return network

    async def find_by_id(self, network_id: UUID) -> Network | None:
        return self._store.get(network_id)

    async def find_all(self) -> list[Network]:
        return list(self._store.values())

    async def delete(self, network_id: UUID) -> bool:
        return self._store.pop(network_id, None) is not None
