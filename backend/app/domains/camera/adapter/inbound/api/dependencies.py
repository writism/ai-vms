from app.domains.camera.adapter.outbound.external.onvif_discovery_adapter import OnvifDiscoveryAdapter
from app.domains.camera.adapter.outbound.persistence.in_memory_camera_repository import InMemoryCameraRepository
from app.domains.camera.adapter.outbound.persistence.in_memory_network_repository import InMemoryNetworkRepository
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

_camera_repo = InMemoryCameraRepository()
_network_repo = InMemoryNetworkRepository()
_discovery_adapter = OnvifDiscoveryAdapter()


def get_register_camera_usecase() -> RegisterCameraUseCase:
    return RegisterCameraUseCase(_camera_repo)


def get_camera_usecase() -> GetCameraUseCase:
    return GetCameraUseCase(_camera_repo)


def get_list_cameras_usecase() -> ListCamerasUseCase:
    return ListCamerasUseCase(_camera_repo)


def get_register_network_usecase() -> RegisterNetworkUseCase:
    return RegisterNetworkUseCase(_network_repo)


def get_network_usecase() -> GetNetworkUseCase:
    return GetNetworkUseCase(_network_repo)


def get_list_networks_usecase() -> ListNetworksUseCase:
    return ListNetworksUseCase(_network_repo)


def get_discover_cameras_usecase() -> DiscoverCamerasUseCase:
    return DiscoverCamerasUseCase(_discovery_adapter)


def get_batch_register_cameras_usecase() -> BatchRegisterCamerasUseCase:
    return BatchRegisterCamerasUseCase(_camera_repo)
