from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.face.application.port.face_repository_port import FaceRepositoryPort
from app.domains.face.domain.entity.face import Face
from app.domains.face.infrastructure.mapper.face_mapper import FaceMapper
from app.domains.face.infrastructure.orm.face_orm import FaceORM
from app.infrastructure.persistence.base_repository import SqlAlchemyBaseRepository


class SqlAlchemyFaceRepository(
    SqlAlchemyBaseRepository[FaceORM, Face],
    FaceRepositoryPort,
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, FaceORM)

    def _to_entity(self, orm: FaceORM) -> Face:
        return FaceMapper.to_entity(orm)

    def _to_orm(self, entity: Face) -> FaceORM:
        return FaceMapper.to_orm(entity)

    async def find_by_identity_id(self, identity_id: UUID) -> list[Face]:
        result = await self._session.execute(
            select(FaceORM).where(FaceORM.identity_id == identity_id)
        )
        return [FaceMapper.to_entity(orm) for orm in result.scalars().all()]
