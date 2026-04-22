from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.camera.application.port.network_repository_port import NetworkRepositoryPort
from app.domains.camera.domain.entity.network import Network
from app.domains.camera.infrastructure.mapper.camera_mapper import NetworkMapper
from app.domains.camera.infrastructure.orm.camera_orm import NetworkORM


class SqlAlchemyNetworkRepository(NetworkRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, network: Network) -> Network:
        orm = NetworkMapper.to_orm(network)
        merged = await self._session.merge(orm)
        await self._session.flush()
        await self._session.refresh(merged)
        return NetworkMapper.to_entity(merged)

    async def find_by_id(self, network_id: UUID) -> Network | None:
        orm = await self._session.get(NetworkORM, network_id)
        return NetworkMapper.to_entity(orm) if orm else None

    async def find_all(self) -> list[Network]:
        result = await self._session.execute(select(NetworkORM))
        return [NetworkMapper.to_entity(orm) for orm in result.scalars().all()]

    async def delete(self, network_id: UUID) -> bool:
        orm = await self._session.get(NetworkORM, network_id)
        if orm is None:
            return False
        await self._session.delete(orm)
        await self._session.flush()
        return True
