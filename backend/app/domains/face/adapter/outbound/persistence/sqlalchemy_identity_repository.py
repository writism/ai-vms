from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.face.application.port.identity_repository_port import IdentityRepositoryPort
from app.domains.face.domain.entity.identity import Identity
from app.domains.face.infrastructure.mapper.face_mapper import IdentityMapper
from app.domains.face.infrastructure.orm.face_orm import IdentityORM
from app.infrastructure.persistence.base_repository import SqlAlchemyBaseRepository
import logging

logger = logging.getLogger(__name__)


class SqlAlchemyIdentityRepository(
    SqlAlchemyBaseRepository[IdentityORM, Identity],
    IdentityRepositoryPort,
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, IdentityORM)

    def _to_entity(self, orm: IdentityORM) -> Identity:
        return IdentityMapper.to_entity(orm)

    def _to_orm(self, entity: Identity) -> IdentityORM:
        return IdentityMapper.to_orm(entity)

    async def update(self, identity: Identity) -> Identity:
        orm = await self._session.get(IdentityORM, identity.id)
        if orm is None:
            raise ValueError(f"Identity {identity.id} not found")
        orm.name = identity.name
        orm.identity_type = identity.identity_type.value
        orm.department = identity.department
        orm.employee_id = identity.employee_id
        orm.position = identity.position
        orm.company = identity.company
        orm.visit_purpose = identity.visit_purpose
        orm.notes = identity.notes
        orm.is_active = identity.is_active
        await self._session.flush()
        await self._session.refresh(orm)
        return IdentityMapper.to_entity(orm)

    async def find_by_name_and_employee_id(self, name: str, employee_id: str) -> Identity | None:
        result = await self._session.execute(
            select(IdentityORM).where(
                IdentityORM.name == name,
                IdentityORM.employee_id == employee_id,
            )
        )
        orm = result.scalar_one_or_none()
        return IdentityMapper.to_entity(orm) if orm else None

    async def find_by_name(self, name: str) -> Identity | None:
        result = await self._session.execute(
            select(IdentityORM).where(IdentityORM.name == name).limit(1)
        )
        orm = result.scalar_one_or_none()
        return IdentityMapper.to_entity(orm) if orm else None

    async def find_by_ids(self, ids: list[UUID]) -> list[Identity]:
        if not ids:
            return []
        result = await self._session.execute(
            select(IdentityORM).where(IdentityORM.id.in_(ids))
        )
        return [IdentityMapper.to_entity(orm) for orm in result.scalars().all()]
