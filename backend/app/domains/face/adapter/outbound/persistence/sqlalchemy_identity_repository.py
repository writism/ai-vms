from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.face.application.port.identity_repository_port import IdentityRepositoryPort
from app.domains.face.domain.entity.identity import Identity
from app.domains.face.infrastructure.mapper.face_mapper import IdentityMapper
from app.domains.face.infrastructure.orm.face_orm import IdentityORM


class SqlAlchemyIdentityRepository(IdentityRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, identity: Identity) -> Identity:
        orm = IdentityMapper.to_orm(identity)
        merged = await self._session.merge(orm)
        await self._session.flush()
        await self._session.refresh(merged)
        return IdentityMapper.to_entity(merged)

    async def find_by_id(self, identity_id: UUID) -> Identity | None:
        orm = await self._session.get(IdentityORM, identity_id)
        return IdentityMapper.to_entity(orm) if orm else None

    async def find_all(self) -> list[Identity]:
        result = await self._session.execute(select(IdentityORM))
        return [IdentityMapper.to_entity(orm) for orm in result.scalars().all()]

    async def update(self, identity: Identity) -> Identity:
        orm = await self._session.get(IdentityORM, identity.id)
        if orm is None:
            raise ValueError(f"Identity {identity.id} not found")
        orm.name = identity.name
        orm.identity_type = identity.identity_type.value
        orm.department = identity.department
        orm.employee_id = identity.employee_id
        orm.company = identity.company
        orm.visit_purpose = identity.visit_purpose
        orm.notes = identity.notes
        orm.is_active = identity.is_active
        await self._session.flush()
        await self._session.refresh(orm)
        return IdentityMapper.to_entity(orm)

    async def delete(self, identity_id: UUID) -> bool:
        orm = await self._session.get(IdentityORM, identity_id)
        if orm is None:
            return False
        await self._session.delete(orm)
        await self._session.flush()
        return True
