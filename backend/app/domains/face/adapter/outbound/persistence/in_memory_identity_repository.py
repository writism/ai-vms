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

    async def update(self, identity: Identity) -> Identity:
        if identity.id not in self._store:
            raise ValueError(f"Identity {identity.id} not found")
        self._store[identity.id] = identity
        return identity

    async def delete(self, identity_id: UUID) -> bool:
        return self._store.pop(identity_id, None) is not None

    async def find_by_name_and_employee_id(self, name: str, employee_id: str) -> Identity | None:
        for identity in self._store.values():
            if identity.name == name and identity.employee_id == employee_id:
                return identity
        return None

    async def find_by_name(self, name: str) -> Identity | None:
        for identity in self._store.values():
            if identity.name == name:
                return identity
        return None

    async def find_by_ids(self, ids: list[UUID]) -> list[Identity]:
        return [self._store[i] for i in ids if i in self._store]
