from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.event.application.port.event_repository_port import EventRepositoryPort
from app.domains.event.domain.entity.event import Event
from app.domains.event.infrastructure.mapper.event_mapper import EventMapper
from app.domains.event.infrastructure.orm.event_orm import EventORM


class SqlAlchemyEventRepository(EventRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, event: Event) -> Event:
        orm = EventMapper.to_orm(event)
        merged = await self._session.merge(orm)
        await self._session.flush()
        await self._session.refresh(merged)
        return EventMapper.to_entity(merged)

    async def find_by_id(self, event_id: UUID) -> Event | None:
        orm = await self._session.get(EventORM, event_id)
        return EventMapper.to_entity(orm) if orm else None

    async def find_all(
        self,
        event_type: str | None = None,
        camera_id: UUID | None = None,
        identity_id: UUID | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Event]:
        stmt = select(EventORM)
        if event_type:
            stmt = stmt.where(EventORM.event_type == event_type)
        if camera_id:
            stmt = stmt.where(EventORM.camera_id == camera_id)
        if identity_id:
            stmt = stmt.where(EventORM.identity_id == identity_id)
        if from_date:
            stmt = stmt.where(EventORM.created_at >= from_date)
        if to_date:
            stmt = stmt.where(EventORM.created_at <= to_date)
        stmt = stmt.order_by(EventORM.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [EventMapper.to_entity(orm) for orm in result.scalars().all()]

    async def count(
        self,
        event_type: str | None = None,
        camera_id: UUID | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(EventORM)
        if event_type:
            stmt = stmt.where(EventORM.event_type == event_type)
        if camera_id:
            stmt = stmt.where(EventORM.camera_id == camera_id)
        if from_date:
            stmt = stmt.where(EventORM.created_at >= from_date)
        if to_date:
            stmt = stmt.where(EventORM.created_at <= to_date)
        result = await self._session.execute(stmt)
        return result.scalar_one()
