from pydantic import BaseModel


class RegisterStreamRequest(BaseModel):
    camera_id: str
    rtsp_url: str


class WebRTCOfferRequest(BaseModel):
    stream_name: str
    sdp_offer: str


class ScanMediaServersRequest(BaseModel):
    subnet: str
