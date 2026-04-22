from pydantic import BaseModel


class StreamRegistrationResponse(BaseModel):
    stream_name: str
    success: bool


class WebRTCAnswerResponse(BaseModel):
    sdp_answer: str


class StreamListResponse(BaseModel):
    streams: dict
