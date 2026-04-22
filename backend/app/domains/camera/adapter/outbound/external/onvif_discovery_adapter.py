from app.domains.camera.application.port.discovery_port import CameraDiscoveryPort, DiscoveredCameraInfo
from app.infrastructure.onvif.client import get_device_detail
from app.infrastructure.onvif.discovery import discover_onvif_devices


class OnvifDiscoveryAdapter(CameraDiscoveryPort):
    async def discover(self, timeout: float = 3.0) -> list[DiscoveredCameraInfo]:
        devices = await discover_onvif_devices(timeout=timeout)
        return [
            DiscoveredCameraInfo(
                ip_address=d.ip_address,
                port=d.port,
                manufacturer=d.manufacturer,
                model=d.model,
                rtsp_url=None,
                onvif_address=d.address,
            )
            for d in devices
        ]

    async def get_device_detail(
        self, ip: str, port: int, username: str | None = None, password: str | None = None
    ) -> DiscoveredCameraInfo:
        detail = await get_device_detail(ip, port, username, password)
        return DiscoveredCameraInfo(
            ip_address=detail.ip_address,
            port=detail.port,
            manufacturer=detail.info.manufacturer if detail.info else None,
            model=detail.info.model if detail.info else None,
            rtsp_url=detail.main_rtsp_url,
            onvif_address=f"http://{ip}:{port}/onvif/device_service",
        )
