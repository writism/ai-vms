from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.setting.application.usecase.setting_usecase import (
    GetSettingsUseCase,
    LoadRuntimeSettingsUseCase,
    UpdateSettingsUseCase,
)
from app.infrastructure.config.settings import settings


async def _get_session():
    if settings.use_database:
        from app.infrastructure.database.session import get_async_session
        async for session in get_async_session():
            yield session
    else:
        yield None


def _get_repo(session: AsyncSession | None = None):
    if settings.use_database and session:
        from app.domains.setting.adapter.outbound.persistence.sqlalchemy_setting_repository import (
            SqlAlchemySettingRepository,
        )
        return SqlAlchemySettingRepository(session)
    from app.domains.setting.adapter.outbound.persistence.sqlalchemy_setting_repository import (
        SqlAlchemySettingRepository,
    )
    raise RuntimeError("Settings require database")


def get_get_settings_usecase(session: AsyncSession | None = Depends(_get_session)) -> GetSettingsUseCase:
    return GetSettingsUseCase(_get_repo(session))


def get_update_settings_usecase(session: AsyncSession | None = Depends(_get_session)) -> UpdateSettingsUseCase:
    return UpdateSettingsUseCase(_get_repo(session))


def get_load_runtime_settings_usecase(session: AsyncSession | None = Depends(_get_session)) -> LoadRuntimeSettingsUseCase:
    return LoadRuntimeSettingsUseCase(_get_repo(session))
