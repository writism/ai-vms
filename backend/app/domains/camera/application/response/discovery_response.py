from pydantic import BaseModel


class DiscoveredCameraResponse(BaseModel):
    ip_address: str
    port: int
    manufacturer: str | None
    model: str | None
    rtsp_url: str | None
    onvif_address: str | None
