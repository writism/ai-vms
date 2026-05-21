import asyncio
import fcntl
import ipaddress
import logging
import re
import socket
import struct
import time
import uuid
from dataclasses import dataclass
from urllib.parse import unquote

logger = logging.getLogger(__name__)

WS_DISCOVERY_MULTICAST = "239.255.255.250"
WS_DISCOVERY_PORT = 3702
DEFAULT_TIMEOUT = 3.0
SIOCGIFADDR = 0x8915

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

# 타입 필터 없는 범용 probe — Hikvision 등 일부 펌웨어가 typed probe에 미응답
PROBE_TEMPLATE_ANY = """<?xml version="1.0" encoding="UTF-8"?>
<e:Envelope xmlns:e="http://www.w3.org/2003/05/soap-envelope"
            xmlns:w="http://schemas.xmlsoap.org/ws/2004/08/addressing"
            xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery">
  <e:Header>
    <w:MessageID>uuid:{message_id}</w:MessageID>
    <w:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</w:To>
    <w:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</w:Action>
  </e:Header>
  <e:Body>
    <d:Probe/>
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


_IPV4_HOST_RE = re.compile(r"^https?://(\d{1,3}(?:\.\d{1,3}){3})(?::(\d+))?(?:/|$)")


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
                model = unquote(scope.rsplit("/", 1)[-1])
            elif "/manufacturer/" in scope.lower():
                manufacturer = unquote(scope.rsplit("/", 1)[-1])
            elif "/hardware/" in scope.lower():
                hardware = unquote(scope.rsplit("/", 1)[-1])

        for xaddr in xaddrs:
            ip_match = _IPV4_HOST_RE.match(xaddr)
            if not ip_match:
                continue
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


def _list_ipv4_interfaces() -> list[tuple[str, str]]:
    interfaces: list[tuple[str, str]] = []
    try:
        names = socket.if_nameindex()
    except OSError as exc:
        logger.warning("if_nameindex unavailable: %s", exc)
        return interfaces

    for _, name in names:
        if name == "lo" or name.startswith(("docker", "br-", "veth")):
            continue
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
                packed = struct.pack("256s", name.encode("utf-8")[:15])
                ip_bytes = fcntl.ioctl(probe.fileno(), SIOCGIFADDR, packed)[20:24]
                ip = socket.inet_ntoa(ip_bytes)
            if ip.startswith("127.") or ip.startswith("169.254."):
                continue
            interfaces.append((name, ip))
        except OSError:
            continue
    return interfaces


class OnvifDiscoveryProtocol(asyncio.DatagramProtocol):
    def __init__(self, seen_ips: set[str], devices: list[DiscoveredDevice]) -> None:
        self._seen_ips = seen_ips
        self._devices = devices
        self._received = 0

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self._transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        self._received += 1
        try:
            xml_str = data.decode("utf-8", errors="ignore")
            for dev in _parse_probe_match(xml_str):
                if dev.ip_address in self._seen_ips:
                    continue
                self._seen_ips.add(dev.ip_address)
                self._devices.append(dev)
        except Exception:
            logger.debug("Failed to parse probe response from %s", addr)

    def error_received(self, exc: Exception) -> None:
        logger.debug("Discovery protocol error: %s", exc)

    @property
    def received_count(self) -> int:
        return self._received


async def _open_probe_socket(
    loop: asyncio.AbstractEventLoop,
    iface_name: str,
    iface_ip: str,
    seen_ips: set[str],
    devices: list[DiscoveredDevice],
) -> tuple[asyncio.DatagramTransport, OnvifDiscoveryProtocol] | None:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        if iface_ip != "0.0.0.0":
            sock.setsockopt(
                socket.IPPROTO_IP,
                socket.IP_MULTICAST_IF,
                socket.inet_aton(iface_ip),
            )
        sock.bind((iface_ip, 0))
        mreq = struct.pack(
            "4s4s",
            socket.inet_aton(WS_DISCOVERY_MULTICAST),
            socket.inet_aton(iface_ip),
        )
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.setblocking(False)

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: OnvifDiscoveryProtocol(seen_ips, devices),
            sock=sock,
        )
        dest = (WS_DISCOVERY_MULTICAST, WS_DISCOVERY_PORT)
        transport.sendto(PROBE_TEMPLATE.format(message_id=uuid.uuid4()).encode("utf-8"), dest)
        transport.sendto(PROBE_TEMPLATE_ANY.format(message_id=uuid.uuid4()).encode("utf-8"), dest)
        return transport, protocol
    except OSError as exc:
        logger.warning("WS-Discovery skip iface %s (%s): %s", iface_name, iface_ip, exc)
        return None


async def _open_unicast_scan(
    loop: asyncio.AbstractEventLoop,
    subnet: str,
    seen_ips: set[str],
    devices: list[DiscoveredDevice],
) -> tuple[asyncio.DatagramTransport, OnvifDiscoveryProtocol] | None:
    try:
        network = ipaddress.ip_network(subnet, strict=False)
    except ValueError as exc:
        logger.warning("Invalid discovery_scan_subnet %r: %s", subnet, exc)
        return None

    if network.num_addresses > 4096:
        logger.warning("discovery_scan_subnet %s too large (%d hosts), skipping unicast scan", subnet, network.num_addresses)
        return None

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", 0))
        sock.setblocking(False)

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: OnvifDiscoveryProtocol(seen_ips, devices),
            sock=sock,
        )
    except OSError as exc:
        logger.warning("Unicast scan socket error: %s", exc)
        return None

    hosts = list(network.hosts())
    logger.info("WS-Discovery unicast scan: subnet=%s hosts=%d", subnet, len(hosts))
    for ip in hosts:
        dest = (str(ip), WS_DISCOVERY_PORT)
        transport.sendto(PROBE_TEMPLATE.format(message_id=uuid.uuid4()).encode("utf-8"), dest)
        transport.sendto(PROBE_TEMPLATE_ANY.format(message_id=uuid.uuid4()).encode("utf-8"), dest)

    return transport, protocol


async def discover_onvif_devices(
    interface_ip: str = "0.0.0.0",
    timeout: float = DEFAULT_TIMEOUT,
    scan_subnet: str = "",
) -> list[DiscoveredDevice]:
    loop = asyncio.get_running_loop()

    if interface_ip != "0.0.0.0":
        targets: list[tuple[str, str]] = [("explicit", interface_ip)]
    else:
        targets = _list_ipv4_interfaces()
        if not targets:
            targets = [("default", "0.0.0.0")]

    seen_ips: set[str] = set()
    devices: list[DiscoveredDevice] = []
    all_pairs: list[tuple[asyncio.DatagramTransport, OnvifDiscoveryProtocol]] = []

    start = time.monotonic()
    for name, ip in targets:
        result = await _open_probe_socket(loop, name, ip, seen_ips, devices)
        if result is not None:
            all_pairs.append(result)

    if scan_subnet:
        result = await _open_unicast_scan(loop, scan_subnet, seen_ips, devices)
        if result is not None:
            all_pairs.append(result)

    if not all_pairs:
        logger.warning("WS-Discovery: no usable interface (targets=%s)", targets)
        return []

    await asyncio.sleep(timeout)

    received_total = 0
    for transport, protocol in all_pairs:
        received_total += protocol.received_count
        transport.close()

    elapsed = time.monotonic() - start
    logger.info(
        "WS-Discovery completed: interfaces=%s subnet=%s probes=%d responses=%d devices=%d elapsed=%.2fs",
        [f"{n}={ip}" for n, ip in targets],
        scan_subnet or "none",
        len(all_pairs),
        received_total,
        len(devices),
        elapsed,
    )
    return devices
