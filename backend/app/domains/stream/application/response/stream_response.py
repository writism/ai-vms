from pydantic import BaseModel


class StreamRegistrationResponse(BaseModel):
    stream_name: str
    success: bool


class WebRTCAnswerResponse(BaseModel):
    sdp_answer: str


class StreamListResponse(BaseModel):
    streams: dict


class MediaServerStreamResponse(BaseModel):
    name: str
    url: str
    camera_ip: str | None = None


class MediaServerResponse(BaseModel):
    ip: str
    port: int
    reachable: bool
    streams: list[MediaServerStreamResponse]
    is_own: bool


class CameraConflictResponse(BaseModel):
    camera_ip: str
    servers: list[str]


class MediaServerScanResponse(BaseModel):
    servers: list[MediaServerResponse]
    conflicts: list[CameraConflictResponse]
    own_server_ip: str | None = None
