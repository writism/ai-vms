from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.face.application.port.face_cluster_repository_port import (
    ClusterSuggestion,
    FaceClusterRepositoryPort,
)
from app.domains.face.domain.entity.face_cluster import ClusterStatus, FaceCluster
from app.domains.face.infrastructure.mapper.face_mapper import FaceClusterMapper
from app.domains.face.infrastructure.orm.face_orm import FaceClusterORM, RecognitionLogORM


class SqlAlchemyFaceClusterRepository(FaceClusterRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, cluster: FaceCluster) -> FaceCluster:
        orm = FaceClusterMapper.to_orm(cluster)
        await self._session.merge(orm)
        await self._session.flush()
        return cluster

    async def find_by_id(self, cluster_id: UUID) -> FaceCluster | None:
        orm = await self._session.get(FaceClusterORM, cluster_id)
        return FaceClusterMapper.to_entity(orm) if orm else None

    async def find_active_pending(self) -> list[FaceCluster]:
        result = await self._session.execute(
            select(FaceClusterORM)
            .where(FaceClusterORM.status == ClusterStatus.PENDING.value)
            .order_by(FaceClusterORM.last_seen.desc())
        )
        return [FaceClusterMapper.to_entity(orm) for orm in result.scalars().all()]

    async def update(self, cluster: FaceCluster) -> FaceCluster:
        orm = await self._session.get(FaceClusterORM, cluster.id)
        if orm is None:
            return await self.save(cluster)
        orm.representative_embedding = cluster.representative_embedding
        orm.representative_image_path = cluster.representative_image_path
        orm.representative_quality_score = cluster.representative_quality_score
        orm.last_seen = cluster.last_seen
        orm.last_camera_id = cluster.last_camera_id
        orm.status = cluster.status.value
        orm.linked_identity_id = cluster.linked_identity_id
        orm.updated_at = cluster.updated_at
        await self._session.flush()
        return cluster

    async def update_status(
        self, cluster_id: UUID, status: ClusterStatus, linked_identity_id: UUID | None = None
    ) -> bool:
        orm = await self._session.get(FaceClusterORM, cluster_id)
        if orm is None:
            return False
        orm.status = status.value
        if linked_identity_id is not None:
            orm.linked_identity_id = linked_identity_id
        await self._session.flush()
        return True

    async def find_suggestions(self, min_count: int, since: datetime) -> list[ClusterSuggestion]:
        count_col = func.count(RecognitionLogORM.id).label("count_window")
        avg_col = func.coalesce(func.avg(RecognitionLogORM.confidence), 0.0).label("avg_confidence")
        result = await self._session.execute(
            select(FaceClusterORM, count_col, avg_col)
            .outerjoin(
                RecognitionLogORM,
                (RecognitionLogORM.cluster_id == FaceClusterORM.id)
                & (RecognitionLogORM.created_at >= since),
            )
            .where(FaceClusterORM.status == ClusterStatus.PENDING.value)
            .group_by(FaceClusterORM.id)
            .having(count_col >= min_count)
            .order_by(FaceClusterORM.last_seen.desc())
        )
        return [
            ClusterSuggestion(
                cluster=FaceClusterMapper.to_entity(row[0]),
                count_window=int(row[1] or 0),
                avg_confidence=float(row[2] or 0.0),
            )
            for row in result.all()
        ]
