from uuid import UUID

from app.domains.face.application.port.identity_repository_port import IdentityRepositoryPort
from app.domains.face.domain.entity.identity import Identity


class InMemoryIdentityRepository(IdentityRepositoryPort):
    def __init__(self) -> None:
        self._store: dict[UUID, Identity] = {}

    async def save(self, identity: Identity) -> Identity:
        self._store[identity.id] = identity
        return identity

    async def find_by_id(self, identity_id: UUID) -> Identity | None:
        return self._store.get(identity_id)

    async def find_all(self) -> list[Identity]:
        return list(self._store.values())

    async def delete(self, identity_id: UUID) -> bool:
        return self._store.pop(identity_id, None) is not None
