from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.alert.application.port.danger_event_repository_port import DangerEventRepositoryPort
from app.domains.alert.domain.entity.danger_event import DangerEvent
from app.domains.alert.infrastructure.mapper.alert_mapper import DangerEventMapper
from app.domains.alert.infrastructure.orm.alert_orm import DangerEventORM


class SqlAlchemyDangerEventRepository(DangerEventRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, event: DangerEvent) -> DangerEvent:
        orm = DangerEventMapper.to_orm(event)
        merged = await self._session.merge(orm)
        await self._session.flush()
        await self._session.refresh(merged)
        return DangerEventMapper.to_entity(merged)

    async def find_by_id(self, event_id: UUID) -> DangerEvent | None:
        orm = await self._session.get(DangerEventORM, event_id)
        return DangerEventMapper.to_entity(orm) if orm else None

    async def find_all(
        self,
        danger_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        camera_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[DangerEvent]:
        stmt = select(DangerEventORM)
        if danger_type:
            stmt = stmt.where(DangerEventORM.danger_type == danger_type)
        if severity:
            stmt = stmt.where(DangerEventORM.severity == severity)
        if status:
            stmt = stmt.where(DangerEventORM.status == status)
        if camera_id:
            stmt = stmt.where(DangerEventORM.camera_id == camera_id)
        stmt = stmt.order_by(DangerEventORM.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [DangerEventMapper.to_entity(orm) for orm in result.scalars().all()]

    async def count(
        self,
        danger_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(DangerEventORM)
        if danger_type:
            stmt = stmt.where(DangerEventORM.danger_type == danger_type)
        if severity:
            stmt = stmt.where(DangerEventORM.severity == severity)
        if status:
            stmt = stmt.where(DangerEventORM.status == status)
        result = await self._session.execute(stmt)
        return result.scalar_one()
