from datetime import UTC, datetime
from uuid import UUID

from app.domains.face.application.port.face_embedding_port import FaceEmbeddingPort
from app.domains.face.application.port.face_repository_port import FaceRepositoryPort
from app.domains.face.application.port.identity_repository_port import IdentityRepositoryPort
from app.domains.face.application.request.face_request import RegisterIdentityRequest, UpdateIdentityRequest
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
            company=request.company,
            visit_purpose=request.visit_purpose,
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


class UpdateIdentityUseCase:
    def __init__(self, repo: IdentityRepositoryPort):
        self._repo = repo

    async def execute(self, identity_id: UUID, request: UpdateIdentityRequest) -> IdentityResponse | None:
        identity = await self._repo.find_by_id(identity_id)
        if identity is None:
            return None
        if request.name is not None:
            identity.name = request.name
        if request.identity_type is not None:
            identity.identity_type = IdentityType(request.identity_type)
        if request.department is not None:
            identity.department = request.department or None
        if request.employee_id is not None:
            identity.employee_id = request.employee_id or None
        if request.company is not None:
            identity.company = request.company or None
        if request.visit_purpose is not None:
            identity.visit_purpose = request.visit_purpose or None
        if request.notes is not None:
            identity.notes = request.notes or None
        identity.updated_at = datetime.now(UTC)
        updated = await self._repo.update(identity)
        return IdentityResponse.from_entity(updated)


class DeleteIdentityUseCase:
    def __init__(
        self,
        identity_repo: IdentityRepositoryPort,
        face_repo: FaceRepositoryPort,
        embedding_store: FaceEmbeddingPort,
    ):
        self._identity_repo = identity_repo
        self._face_repo = face_repo
        self._embedding_store = embedding_store

    async def execute(self, identity_id: UUID) -> bool:
        identity = await self._identity_repo.find_by_id(identity_id)
        if identity is None:
            return False
        faces = await self._face_repo.find_by_identity_id(identity_id)
        for face in faces:
            await self._embedding_store.delete(face.id)
            await self._face_repo.delete(face.id)
        await self._identity_repo.delete(identity_id)
        return True
