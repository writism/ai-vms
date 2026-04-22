from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.application.port.user_repository_port import UserRepositoryPort
from app.domains.auth.domain.entity.user import User
from app.domains.auth.infrastructure.mapper.user_mapper import UserMapper
from app.domains.auth.infrastructure.orm.user_orm import UserORM


class SqlAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> User:
        orm = UserMapper.to_orm(user)
        merged = await self._session.merge(orm)
        await self._session.flush()
        await self._session.refresh(merged)
        return UserMapper.to_entity(merged)

    async def find_by_id(self, user_id: UUID) -> User | None:
        orm = await self._session.get(UserORM, user_id)
        return UserMapper.to_entity(orm) if orm else None

    async def find_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserORM).where(UserORM.email == email))
        orm = result.scalar_one_or_none()
        return UserMapper.to_entity(orm) if orm else None

    async def find_all(self) -> list[User]:
        result = await self._session.execute(select(UserORM))
        return [UserMapper.to_entity(orm) for orm in result.scalars().all()]
