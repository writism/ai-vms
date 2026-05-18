from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.setting.application.port.setting_repository_port import SettingRepositoryPort
from app.domains.setting.domain.entity.setting import SystemSetting
from app.domains.setting.infrastructure.mapper.setting_mapper import SettingMapper
from app.domains.setting.infrastructure.orm.setting_orm import SystemSettingORM


class SqlAlchemySettingRepository(SettingRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> list[SystemSetting]:
        result = await self._session.execute(select(SystemSettingORM))
        return [SettingMapper.to_entity(orm) for orm in result.scalars().all()]

    async def find_by_key(self, key: str) -> SystemSetting | None:
        result = await self._session.execute(
            select(SystemSettingORM).where(SystemSettingORM.key == key)
        )
        orm = result.scalar_one_or_none()
        return SettingMapper.to_entity(orm) if orm else None

    async def save(self, setting: SystemSetting) -> SystemSetting:
        existing = await self._session.execute(
            select(SystemSettingORM).where(SystemSettingORM.key == setting.key)
        )
        orm = existing.scalar_one_or_none()
        if orm:
            orm.value = setting.value
        else:
            orm = SettingMapper.to_orm(setting)
            self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return SettingMapper.to_entity(orm)
