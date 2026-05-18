from abc import abstractmethod
from typing import Generic, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

TORM = TypeVar("TORM")
TEntity = TypeVar("TEntity")


class SqlAlchemyBaseRepository(Generic[TORM, TEntity]):
    def __init__(self, session: AsyncSession, orm_class: Type[TORM]):
        self._session = session
        self._orm_class = orm_class

    @abstractmethod
    def _to_entity(self, orm: TORM) -> TEntity: ...

    @abstractmethod
    def _to_orm(self, entity: TEntity) -> TORM: ...

    async def save(self, entity: TEntity) -> TEntity:
        orm = self._to_orm(entity)
        merged = await self._session.merge(orm)
        await self._session.flush()
        await self._session.refresh(merged)
        return self._to_entity(merged)

    async def find_by_id(self, entity_id: UUID) -> TEntity | None:
        orm = await self._session.get(self._orm_class, entity_id)
        return self._to_entity(orm) if orm else None

    async def find_all(self) -> list[TEntity]:
        result = await self._session.execute(select(self._orm_class))
        return [self._to_entity(orm) for orm in result.scalars().all()]

    async def delete(self, entity_id: UUID) -> bool:
        orm = await self._session.get(self._orm_class, entity_id)
        if orm is None:
            return False
        await self._session.delete(orm)
        await self._session.flush()
        return True
