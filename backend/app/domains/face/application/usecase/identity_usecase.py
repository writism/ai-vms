from uuid import UUID

from app.domains.face.application.port.identity_repository_port import IdentityRepositoryPort
from app.domains.face.application.request.face_request import RegisterIdentityRequest
from app.domains.face.application.response.face_response import IdentityResponse
from app.domains.face.domain.entity.identity import Identity, IdentityType


class RegisterIdentityUseCase:
    def __init__(self, repo: IdentityRepositoryPort):
        self._repo = repo

    async def execute(self, request: RegisterIdentityRequest) -> IdentityResponse:
        identity = Identity(
            name=request.name,
            identity_type=IdentityType(request.identity_type),
            department=request.department,
            employee_id=request.employee_id,
            notes=request.notes,
        )
        saved = await self._repo.save(identity)
        return IdentityResponse.from_entity(saved)


class ListIdentitiesUseCase:
    def __init__(self, repo: IdentityRepositoryPort):
        self._repo = repo

    async def execute(self) -> list[IdentityResponse]:
        identities = await self._repo.find_all()
        return [IdentityResponse.from_entity(i) for i in identities]


class GetIdentityUseCase:
    def __init__(self, repo: IdentityRepositoryPort):
        self._repo = repo

    async def execute(self, identity_id: UUID) -> IdentityResponse | None:
        identity = await self._repo.find_by_id(identity_id)
        if identity is None:
            return None
        return IdentityResponse.from_entity(identity)
