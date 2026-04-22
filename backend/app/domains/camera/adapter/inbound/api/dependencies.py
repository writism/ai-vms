from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.camera.adapter.outbound.external.onvif_discovery_adapter import OnvifDiscoveryAdapter
from app.domains.camera.adapter.outbound.persistence.in_memory_camera_repository import InMemoryCameraRepository
from app.domains.camera.adapter.outbound.persistence.in_memory_network_repository import InMemoryNetworkRepository
from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.camera.application.port.network_repository_port import NetworkRepositoryPort
from app.domains.camera.application.usecase.discover_cameras_usecase import (
    BatchRegisterCamerasUseCase,
    DiscoverCamerasUseCase,
)
from app.domains.camera.application.usecase.get_camera_usecase import GetCameraUseCase, ListCamerasUseCase
from app.domains.camera.application.usecase.network_usecase import (
    GetNetworkUseCase,
    ListNetworksUseCase,
    RegisterNetworkUseCase,
)
from app.domains.camera.application.usecase.register_camera_usecase import RegisterCameraUseCase
from app.infrastructure.config.settings import settings

_in_memory_camera_repo = InMemoryCameraRepository()
_in_memory_network_repo = InMemoryNetworkRepository()
_discovery_adapter = OnvifDiscoveryAdapter()


def _get_camera_repo(session: AsyncSession | None = None) -> CameraRepositoryPort:
    if settings.use_database and session:
        from app.domains.camera.adapter.outbound.persistence.sqlalchemy_camera_repository import SqlAlchemyCameraRepository
        return SqlAlchemyCameraRepository(session)
    return _in_memory_camera_repo


def _get_network_repo(session: AsyncSession | None = None) -> NetworkRepositoryPort:
    if settings.use_database and session:
        from app.domains.camera.adapter.outbound.persistence.sqlalchemy_network_repository import SqlAlchemyNetworkRepository
        return SqlAlchemyNetworkRepository(session)
    return _in_memory_network_repo


async def _get_session():
    if settings.use_database:
        from app.infrastructure.database.session import get_async_session
        async for session in get_async_session():
            yield session
    else:
        yield None


def get_register_camera_usecase(session: AsyncSession | None = Depends(_get_session)) -> RegisterCameraUseCase:
    return RegisterCameraUseCase(_get_camera_repo(session))


def get_camera_usecase(session: AsyncSession | None = Depends(_get_session)) -> GetCameraUseCase:
    return GetCameraUseCase(_get_camera_repo(session))


def get_list_cameras_usecase(session: AsyncSession | None = Depends(_get_session)) -> ListCamerasUseCase:
    return ListCamerasUseCase(_get_camera_repo(session))


def get_register_network_usecase(session: AsyncSession | None = Depends(_get_session)) -> RegisterNetworkUseCase:
    return RegisterNetworkUseCase(_get_network_repo(session))


def get_network_usecase(session: AsyncSession | None = Depends(_get_session)) -> GetNetworkUseCase:
    return GetNetworkUseCase(_get_network_repo(session))


def get_list_networks_usecase(session: AsyncSession | None = Depends(_get_session)) -> ListNetworksUseCase:
    return ListNetworksUseCase(_get_network_repo(session))


def get_discover_cameras_usecase() -> DiscoverCamerasUseCase:
    return DiscoverCamerasUseCase(_discovery_adapter)


def get_batch_register_cameras_usecase(session: AsyncSession | None = Depends(_get_session)) -> BatchRegisterCamerasUseCase:
    return BatchRegisterCamerasUseCase(_get_camera_repo(session))
