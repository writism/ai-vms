from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.domain.entity.camera import Camera
from app.domains.camera.infrastructure.mapper.camera_mapper import CameraMapper
from app.domains.camera.infrastructure.orm.camera_orm import CameraORM


class SqlAlchemyCameraRepository(CameraRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, camera: Camera) -> Camera:
        orm = CameraMapper.to_orm(camera)
        merged = await self._session.merge(orm)
        await self._session.flush()
        await self._session.refresh(merged)
        return CameraMapper.to_entity(merged)

    async def find_by_id(self, camera_id: UUID) -> Camera | None:
        orm = await self._session.get(CameraORM, camera_id)
        return CameraMapper.to_entity(orm) if orm else None

    async def find_all(self) -> list[Camera]:
        result = await self._session.execute(select(CameraORM))
        return [CameraMapper.to_entity(orm) for orm in result.scalars().all()]

    async def find_by_network_id(self, network_id: UUID) -> list[Camera]:
        result = await self._session.execute(select(CameraORM).where(CameraORM.network_id == network_id))
        return [CameraMapper.to_entity(orm) for orm in result.scalars().all()]

    async def update(self, camera: Camera) -> Camera:
        orm = CameraMapper.to_orm(camera)
        merged = await self._session.merge(orm)
        await self._session.flush()
        await self._session.refresh(merged)
        return CameraMapper.to_entity(merged)

    async def delete(self, camera_id: UUID) -> bool:
        orm = await self._session.get(CameraORM, camera_id)
        if orm is None:
            return False
        await self._session.delete(orm)
        await self._session.flush()
        return True
