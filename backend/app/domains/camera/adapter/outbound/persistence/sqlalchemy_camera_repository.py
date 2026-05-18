from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.domain.entity.camera import Camera
from app.domains.camera.infrastructure.mapper.camera_mapper import CameraMapper
from app.domains.camera.infrastructure.orm.camera_orm import CameraORM
from app.infrastructure.persistence.base_repository import SqlAlchemyBaseRepository


class SqlAlchemyCameraRepository(
    SqlAlchemyBaseRepository[CameraORM, Camera],
    CameraRepositoryPort,
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CameraORM)

    def _to_entity(self, orm: CameraORM) -> Camera:
        return CameraMapper.to_entity(orm)

    def _to_orm(self, entity: Camera) -> CameraORM:
        return CameraMapper.to_orm(entity)

    async def find_by_network_id(self, network_id: UUID) -> list[Camera]:
        result = await self._session.execute(
            select(CameraORM).where(CameraORM.network_id == network_id)
        )
        return [CameraMapper.to_entity(orm) for orm in result.scalars().all()]

    async def update(self, camera: Camera) -> Camera:
        return await self.save(camera)
