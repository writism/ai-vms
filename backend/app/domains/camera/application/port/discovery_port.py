from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DiscoveredCameraInfo:
    ip_address: str
    port: int
    manufacturer: str | None
    model: str | None
    rtsp_url: str | None
    onvif_address: str | None


class CameraDiscoveryPort(ABC):
    @abstractmethod
    async def discover(self, timeout: float = 3.0) -> list[DiscoveredCameraInfo]: ...

    @abstractmethod
    async def get_device_detail(
        self, ip: str, port: int, username: str | None = None, password: str | None = None
    ) -> DiscoveredCameraInfo: ...
