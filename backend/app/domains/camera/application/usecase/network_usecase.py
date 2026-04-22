from uuid import UUID

from app.domains.camera.application.port.network_repository_port import NetworkRepositoryPort
from app.domains.camera.application.request.camera_request import RegisterNetworkRequest
from app.domains.camera.application.response.camera_response import NetworkResponse
from app.domains.camera.domain.entity.network import Network


class RegisterNetworkUseCase:
    def __init__(self, repo: NetworkRepositoryPort):
        self._repo = repo

    async def execute(self, request: RegisterNetworkRequest) -> NetworkResponse:
        network = Network(
            name=request.name,
            subnet=request.subnet,
            description=request.description,
        )
        saved = await self._repo.save(network)
        return NetworkResponse.from_entity(saved)


class ListNetworksUseCase:
    def __init__(self, repo: NetworkRepositoryPort):
        self._repo = repo

    async def execute(self) -> list[NetworkResponse]:
        networks = await self._repo.find_all()
        return [NetworkResponse.from_entity(n) for n in networks]


class GetNetworkUseCase:
    def __init__(self, repo: NetworkRepositoryPort):
        self._repo = repo

    async def execute(self, network_id: UUID) -> NetworkResponse | None:
        network = await self._repo.find_by_id(network_id)
        if network is None:
            return None
        return NetworkResponse.from_entity(network)
