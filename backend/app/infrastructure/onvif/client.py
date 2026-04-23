import logging
import re
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

DEVICE_INFO_BODY = """<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:tds="http://www.onvif.org/ver10/device/wsdl">
  <s:Body>
    <tds:GetDeviceInformation/>
  </s:Body>
</s:Envelope>"""

PROFILES_BODY = """<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:trt="http://www.onvif.org/ver10/media/wsdl">
  <s:Body>
    <trt:GetProfiles/>
  </s:Body>
</s:Envelope>"""

STREAM_URI_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:trt="http://www.onvif.org/ver10/media/wsdl"
            xmlns:tt="http://www.onvif.org/ver10/schema">
  <s:Body>
    <trt:GetStreamUri>
      <trt:StreamSetup>
        <tt:Stream>RTP-Unicast</tt:Stream>
        <tt:Transport><tt:Protocol>RTSP</tt:Protocol></tt:Transport>
      </trt:StreamSetup>
      <trt:ProfileToken>{profile_token}</trt:ProfileToken>
    </trt:GetStreamUri>
  </s:Body>
</s:Envelope>"""


@dataclass
class OnvifDeviceInfo:
    manufacturer: str
    model: str
    firmware_version: str
    serial_number: str
    hardware_id: str


@dataclass
class OnvifProfile:
    token: str
    name: str
    rtsp_url: str | None = None


@dataclass
class OnvifDeviceDetail:
    ip_address: str
    port: int
    info: OnvifDeviceInfo | None
    profiles: list[OnvifProfile]
    main_rtsp_url: str | None


def _extract_tag(xml: str, tag: str) -> str | None:
    pattern = re.compile(rf"<(?:[\w]+:)?{tag}[^>]*>(.*?)</(?:[\w]+:)?{tag}>", re.DOTALL)
    m = pattern.search(xml)
    if not m:
        return None
    value = m.group(1).strip()
    return value.replace("&amp;", "&")


async def get_device_detail(
    ip: str,
    port: int = 80,
    username: str | None = None,
    password: str | None = None,
    timeout: float = 5.0,
) -> OnvifDeviceDetail:
    base_url = f"http://{ip}:{port}/onvif/device_service"
    media_url = f"http://{ip}:{port}/onvif/media_service"
    headers = {"Content-Type": "application/soap+xml; charset=utf-8"}

    auth = None
    if username and password:
        auth = httpx.DigestAuth(username, password)

    info = None
    profiles: list[OnvifProfile] = []
    main_rtsp_url = None

    async with httpx.AsyncClient(timeout=timeout, auth=auth) as client:
        try:
            resp = await client.post(base_url, content=DEVICE_INFO_BODY, headers=headers)
            if resp.status_code == 200:
                body = resp.text
                info = OnvifDeviceInfo(
                    manufacturer=_extract_tag(body, "Manufacturer") or "",
                    model=_extract_tag(body, "Model") or "",
                    firmware_version=_extract_tag(body, "FirmwareVersion") or "",
                    serial_number=_extract_tag(body, "SerialNumber") or "",
                    hardware_id=_extract_tag(body, "HardwareId") or "",
                )
        except Exception:
            logger.debug("Failed to get device info from %s:%d", ip, port)

        try:
            resp = await client.post(media_url, content=PROFILES_BODY, headers=headers)
            if resp.status_code == 200:
                body = resp.text
                token_pattern = re.compile(r'token="([^"]+)"')
                name_pattern = re.compile(r"<[\w:]*Name[^>]*>(.*?)</[\w:]*Name>", re.DOTALL)
                tokens = token_pattern.findall(body)
                names = name_pattern.findall(body)

                for i, token in enumerate(tokens):
                    name = names[i].strip() if i < len(names) else token
                    profiles.append(OnvifProfile(token=token, name=name))
        except Exception:
            logger.debug("Failed to get profiles from %s:%d", ip, port)

        for profile in profiles:
            try:
                stream_body = STREAM_URI_TEMPLATE.format(profile_token=profile.token)
                resp = await client.post(media_url, content=stream_body, headers=headers)
                if resp.status_code == 200:
                    uri = _extract_tag(resp.text, "Uri")
                    if uri:
                        profile.rtsp_url = uri
                        if main_rtsp_url is None:
                            main_rtsp_url = uri
            except Exception:
                logger.debug("Failed to get stream URI for profile %s", profile.token)

    return OnvifDeviceDetail(
        ip_address=ip,
        port=port,
        info=info,
        profiles=profiles,
        main_rtsp_url=main_rtsp_url,
    )
