from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.face.application.port.face_repository_port import FaceRepositoryPort
from app.domains.face.domain.entity.face import Face
from app.domains.face.infrastructure.mapper.face_mapper import FaceMapper
from app.domains.face.infrastructure.orm.face_orm import FaceORM


class SqlAlchemyFaceRepository(FaceRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, face: Face) -> Face:
        orm = FaceMapper.to_orm(face)
        merged = await self._session.merge(orm)
        await self._session.flush()
        await self._session.refresh(merged)
        return FaceMapper.to_entity(merged)

    async def find_by_identity_id(self, identity_id: UUID) -> list[Face]:
        result = await self._session.execute(
            select(FaceORM).where(FaceORM.identity_id == identity_id)
        )
        return [FaceMapper.to_entity(orm) for orm in result.scalars().all()]

    async def find_by_id(self, face_id: UUID) -> Face | None:
        orm = await self._session.get(FaceORM, face_id)
        return FaceMapper.to_entity(orm) if orm else None

    async def delete(self, face_id: UUID) -> bool:
        orm = await self._session.get(FaceORM, face_id)
        if orm is None:
            return False
        await self._session.delete(orm)
        await self._session.flush()
        return True
