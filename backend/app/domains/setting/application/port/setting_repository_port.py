from abc import ABC, abstractmethod

from app.domains.setting.domain.entity.setting import SystemSetting


class SettingRepositoryPort(ABC):
    @abstractmethod
    async def find_all(self) -> list[SystemSetting]: ...

    @abstractmethod
    async def find_by_key(self, key: str) -> SystemSetting | None: ...

    @abstractmethod
    async def save(self, setting: SystemSetting) -> SystemSetting: ...
