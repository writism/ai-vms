from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.face.application.port.recognition_log_port import RecognitionLogPort
from app.domains.face.domain.entity.recognition_log import RecognitionLog
from app.domains.face.infrastructure.orm.face_orm import RecognitionLogORM


def _to_entity(orm: RecognitionLogORM) -> RecognitionLog:
    return RecognitionLog(
        id=orm.id,
        camera_id=orm.camera_id,
        identity_id=orm.identity_id,
        identity_name=orm.identity_name,
        identity_type=orm.identity_type,
        confidence=orm.confidence,
        is_registered=orm.is_registered,
        embedding=list(orm.embedding) if orm.embedding is not None else None,
        image_path=orm.image_path,
        cluster_id=orm.cluster_id,
        created_at=orm.created_at,
    )


class SqlAlchemyRecognitionLogRepository(RecognitionLogPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, log: RecognitionLog) -> RecognitionLog:
        orm = RecognitionLogORM(
            id=log.id,
            camera_id=log.camera_id,
            identity_id=log.identity_id,
            identity_name=log.identity_name,
            identity_type=log.identity_type,
            confidence=log.confidence,
            is_registered=log.is_registered,
            embedding=log.embedding,
            image_path=log.image_path,
            cluster_id=log.cluster_id,
            created_at=log.created_at,
        )
        await self._session.merge(orm)
        await self._session.flush()
        return log

    async def find_recent(self, limit: int = 20) -> list[RecognitionLog]:
        result = await self._session.execute(
            select(RecognitionLogORM).order_by(RecognitionLogORM.created_at.desc()).limit(limit)
        )
        return [_to_entity(orm) for orm in result.scalars().all()]
