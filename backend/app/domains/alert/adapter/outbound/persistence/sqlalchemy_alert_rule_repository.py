from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.alert.application.port.alert_rule_repository_port import AlertRuleRepositoryPort
from app.domains.alert.domain.entity.alert_rule import AlertRule
from app.domains.alert.infrastructure.mapper.alert_mapper import AlertRuleMapper
from app.domains.alert.infrastructure.orm.alert_orm import AlertRuleORM


class SqlAlchemyAlertRuleRepository(AlertRuleRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, rule: AlertRule) -> AlertRule:
        orm = AlertRuleMapper.to_orm(rule)
        merged = await self._session.merge(orm)
        await self._session.flush()
        await self._session.refresh(merged)
        return AlertRuleMapper.to_entity(merged)

    async def find_by_id(self, rule_id: UUID) -> AlertRule | None:
        orm = await self._session.get(AlertRuleORM, rule_id)
        return AlertRuleMapper.to_entity(orm) if orm else None

    async def find_all(self) -> list[AlertRule]:
        result = await self._session.execute(select(AlertRuleORM))
        return [AlertRuleMapper.to_entity(orm) for orm in result.scalars().all()]

    async def find_active_rules(self) -> list[AlertRule]:
        result = await self._session.execute(
            select(AlertRuleORM).where(AlertRuleORM.is_active.is_(True))
        )
        return [AlertRuleMapper.to_entity(orm) for orm in result.scalars().all()]

    async def find_matching_rules(self, camera_id: UUID, danger_type: str | None = None) -> list[AlertRule]:
        stmt = select(AlertRuleORM).where(
            AlertRuleORM.is_active.is_(True),
            or_(AlertRuleORM.camera_id.is_(None), AlertRuleORM.camera_id == camera_id),
        )
        result = await self._session.execute(stmt)
        rules = [AlertRuleMapper.to_entity(orm) for orm in result.scalars().all()]
        if danger_type is not None:
            rules = [r for r in rules if danger_type in r.danger_types or r.enable_face_recognition]
        return rules

    async def delete(self, rule_id: UUID) -> bool:
        orm = await self._session.get(AlertRuleORM, rule_id)
        if orm is None:
            return False
        await self._session.delete(orm)
        await self._session.flush()
        return True
