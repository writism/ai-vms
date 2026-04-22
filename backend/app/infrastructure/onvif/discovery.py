import asyncio
import logging
import re
import socket
import struct
import uuid
from dataclasses import dataclass

logger = logging.getLogger(__name__)

WS_DISCOVERY_MULTICAST = "239.255.255.250"
WS_DISCOVERY_PORT = 3702
DEFAULT_TIMEOUT = 3.0

PROBE_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<e:Envelope xmlns:e="http://www.w3.org/2003/05/soap-envelope"
            xmlns:w="http://schemas.xmlsoap.org/ws/2004/08/addressing"
            xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery"
            xmlns:dn="http://www.onvif.org/ver10/network/wsdl">
  <e:Header>
    <w:MessageID>uuid:{message_id}</w:MessageID>
    <w:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</w:To>
    <w:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</w:Action>
  </e:Header>
  <e:Body>
    <d:Probe>
      <d:Types>dn:NetworkVideoTransmitter</d:Types>
    </d:Probe>
  </e:Body>
</e:Envelope>"""


@dataclass
class DiscoveredDevice:
    address: str
    ip_address: str
    port: int
    scopes: list[str]
    manufacturer: str | None = None
    model: str | None = None
    hardware: str | None = None


def _parse_probe_match(xml_data: str) -> list[DiscoveredDevice]:
    devices: list[DiscoveredDevice] = []

    addr_pattern = re.compile(r"<[\w:]*XAddrs[^>]*>(.*?)</[\w:]*XAddrs>", re.DOTALL)
    scope_pattern = re.compile(r"<[\w:]*Scopes[^>]*>(.*?)</[\w:]*Scopes>", re.DOTALL)

    for addr_match in addr_pattern.finditer(xml_data):
        xaddrs = addr_match.group(1).strip().split()
        scopes_match = scope_pattern.search(xml_data)
        scopes = scopes_match.group(1).strip().split() if scopes_match else []

        manufacturer = None
        model = None
        hardware = None
        for scope in scopes:
            if "/name/" in scope:
                model = scope.rsplit("/", 1)[-1]
            elif "/manufacturer/" in scope.lower():
                manufacturer = scope.rsplit("/", 1)[-1]
            elif "/hardware/" in scope.lower():
                hardware = scope.rsplit("/", 1)[-1]

        for xaddr in xaddrs:
            ip_match = re.search(r"https?://([^:/]+)(?::(\d+))?", xaddr)
            if ip_match:
                ip = ip_match.group(1)
                port = int(ip_match.group(2)) if ip_match.group(2) else 80
                devices.append(
                    DiscoveredDevice(
                        address=xaddr,
                        ip_address=ip,
                        port=port,
                        scopes=scopes,
                        manufacturer=manufacturer,
                        model=model,
                        hardware=hardware,
                    )
                )

    return devices


class OnvifDiscoveryProtocol(asyncio.DatagramProtocol):
    def __init__(self, future: asyncio.Future, timeout: float):
        self._future = future
        self._devices: list[DiscoveredDevice] = []
        self._seen_ips: set[str] = set()
        self._timeout = timeout

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self._transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        try:
            xml_str = data.decode("utf-8", errors="ignore")
            parsed = _parse_probe_match(xml_str)
            for dev in parsed:
                if dev.ip_address not in self._seen_ips:
                    self._seen_ips.add(dev.ip_address)
                    self._devices.append(dev)
        except Exception:
            logger.debug("Failed to parse probe response from %s", addr)

    def error_received(self, exc: Exception) -> None:
        logger.debug("Discovery protocol error: %s", exc)

    def get_devices(self) -> list[DiscoveredDevice]:
        return self._devices


async def discover_onvif_devices(
    interface_ip: str = "0.0.0.0",
    timeout: float = DEFAULT_TIMEOUT,
) -> list[DiscoveredDevice]:
    loop = asyncio.get_running_loop()
    future: asyncio.Future = loop.create_future()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    if interface_ip != "0.0.0.0":
        sock.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_MULTICAST_IF,
            socket.inet_aton(interface_ip),
        )

    mreq = struct.pack("4s4s", socket.inet_aton(WS_DISCOVERY_MULTICAST), socket.inet_aton(interface_ip))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.setblocking(False)

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: OnvifDiscoveryProtocol(future, timeout),
        sock=sock,
    )

    probe_message = PROBE_TEMPLATE.format(message_id=uuid.uuid4())
    transport.sendto(probe_message.encode("utf-8"), (WS_DISCOVERY_MULTICAST, WS_DISCOVERY_PORT))

    await asyncio.sleep(timeout)
    transport.close()

    return protocol.get_devices()
