from uuid import UUID

from app.domains.face.application.port.face_repository_port import FaceRepositoryPort
from app.domains.face.domain.entity.face import Face


class InMemoryFaceRepository(FaceRepositoryPort):
    def __init__(self) -> None:
        self._store: dict[UUID, Face] = {}

    async def save(self, face: Face) -> Face:
        self._store[face.id] = face
        return face

    async def find_by_identity_id(self, identity_id: UUID) -> list[Face]:
        return [f for f in self._store.values() if f.identity_id == identity_id]

    async def find_by_id(self, face_id: UUID) -> Face | None:
        return self._store.get(face_id)

    async def delete(self, face_id: UUID) -> bool:
        return self._store.pop(face_id, None) is not None
