from app.domains.setting.domain.entity.setting import SystemSetting
from app.domains.setting.infrastructure.orm.setting_orm import SystemSettingORM


class SettingMapper:
    @staticmethod
    def to_entity(orm: SystemSettingORM) -> SystemSetting:
        return SystemSetting(
            id=orm.id,
            key=orm.key,
            value=orm.value,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_orm(entity: SystemSetting) -> SystemSettingORM:
        return SystemSettingORM(
            id=entity.id,
            key=entity.key,
            value=entity.value,
        )
