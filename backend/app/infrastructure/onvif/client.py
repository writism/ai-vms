import hashlib
import logging
import os
import re
from base64 import b64encode
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

logger = logging.getLogger(__name__)


def _ws_security_header(username: str, password: str) -> str:
    nonce_bytes = os.urandom(16)
    nonce_b64 = b64encode(nonce_bytes).decode()
    created = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    digest_input = nonce_bytes + created.encode("utf-8") + password.encode("utf-8")
    digest = b64encode(hashlib.sha1(digest_input).digest()).decode()
    return (
        '<s:Header>'
        '<Security xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"'
        ' s:mustUnderstand="true">'
        '<UsernameToken>'
        f'<Username>{username}</Username>'
        f'<Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">{digest}</Password>'
        f'<Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">{nonce_b64}</Nonce>'
        f'<Created xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">{created}</Created>'
        '</UsernameToken>'
        '</Security>'
        '</s:Header>'
    )


def _inject_ws_header(soap_body: str, username: str, password: str) -> str:
    header = _ws_security_header(username, password)
    return soap_body.replace("<s:Body>", f"{header}<s:Body>", 1)


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


async def _post_soap(
    client: httpx.AsyncClient,
    url: str,
    body: str,
    headers: dict[str, str],
    username: str | None,
    password: str | None,
    use_ws_security: bool,
) -> httpx.Response:
    content = body
    if use_ws_security and username and password:
        content = _inject_ws_header(body, username, password)
    return await client.post(url, content=content, headers=headers)


def _is_soap_fault(text: str) -> bool:
    return "Fault" in text and ("NotAuthorized" in text or "Sender" in text)


async def _try_get_detail(
    ip: str,
    port: int,
    username: str | None,
    password: str | None,
    timeout: float,
    use_ws_security: bool,
) -> OnvifDeviceDetail | None:
    base_url = f"http://{ip}:{port}/onvif/device_service"
    media_url = f"http://{ip}:{port}/onvif/media_service"
    headers = {"Content-Type": "application/soap+xml; charset=utf-8"}

    auth = None
    if not use_ws_security and username and password:
        auth = httpx.DigestAuth(username, password)

    info = None
    profiles: list[OnvifProfile] = []
    main_rtsp_url = None
    auth_failed = False

    async with httpx.AsyncClient(timeout=timeout, auth=auth) as client:
        try:
            resp = await _post_soap(client, base_url, DEVICE_INFO_BODY, headers, username, password, use_ws_security)
            if resp.status_code == 200 and not _is_soap_fault(resp.text):
                body = resp.text
                info = OnvifDeviceInfo(
                    manufacturer=_extract_tag(body, "Manufacturer") or "",
                    model=_extract_tag(body, "Model") or "",
                    firmware_version=_extract_tag(body, "FirmwareVersion") or "",
                    serial_number=_extract_tag(body, "SerialNumber") or "",
                    hardware_id=_extract_tag(body, "HardwareId") or "",
                )
            elif resp.status_code == 401 or _is_soap_fault(resp.text):
                auth_failed = True
        except Exception:
            logger.debug("Failed to get device info from %s:%d (ws_security=%s)", ip, port, use_ws_security)

        if auth_failed:
            return None

        try:
            resp = await _post_soap(client, media_url, PROFILES_BODY, headers, username, password, use_ws_security)
            if resp.status_code == 200 and not _is_soap_fault(resp.text):
                body = resp.text
                token_pattern = re.compile(r'token="([^"]+)"')
                name_pattern = re.compile(r"<[\w:]*Name[^>]*>(.*?)</[\w:]*Name>", re.DOTALL)
                tokens = token_pattern.findall(body)
                names = name_pattern.findall(body)

                for i, token in enumerate(tokens):
                    name = names[i].strip() if i < len(names) else token
                    profiles.append(OnvifProfile(token=token, name=name))
            elif resp.status_code == 401 or _is_soap_fault(resp.text):
                return None
        except Exception:
            logger.debug("Failed to get profiles from %s:%d (ws_security=%s)", ip, port, use_ws_security)

        for profile in profiles:
            try:
                stream_body = STREAM_URI_TEMPLATE.format(profile_token=profile.token)
                resp = await _post_soap(client, media_url, stream_body, headers, username, password, use_ws_security)
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


async def get_device_detail(
    ip: str,
    port: int = 80,
    username: str | None = None,
    password: str | None = None,
    timeout: float = 5.0,
) -> OnvifDeviceDetail:
    if username and password:
        # WS-Security first (Tapo, etc.), then Digest Auth (Hikvision, etc.)
        for use_ws in (True, False):
            result = await _try_get_detail(ip, port, username, password, timeout, use_ws)
            if result is not None and (result.main_rtsp_url or result.info):
                logger.info("ONVIF auth succeeded for %s:%d (ws_security=%s)", ip, port, use_ws)
                return result
        logger.warning("Both WS-Security and Digest Auth failed for %s:%d", ip, port)

    result = await _try_get_detail(ip, port, username, password, timeout, use_ws_security=False)
    if result is not None:
        return result

    return OnvifDeviceDetail(
        ip_address=ip,
        port=port,
        info=None,
        profiles=[],
        main_rtsp_url=None,
    )
