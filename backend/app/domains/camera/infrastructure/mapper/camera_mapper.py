import logging

from app.domains.camera.domain.entity.camera import Camera, CameraStatus
from app.domains.camera.domain.entity.network import Network
from app.domains.camera.infrastructure.orm.camera_orm import CameraORM, NetworkORM

logger = logging.getLogger(__name__)


def _encrypt_rtsp(url: str | None) -> str | None:
    if not url:
        return url
    try:
        from app.infrastructure.config.settings import settings
        from app.infrastructure.crypto.encryption import encrypt, is_encrypted
        if settings.encryption_key and not is_encrypted(url):
            return encrypt(url, settings.encryption_key)
    except Exception as e:
        logger.debug("rtsp encrypt skipped: %s", e)
    return url


def _decrypt_rtsp(url: str | None) -> str | None:
    if not url:
        return url
    try:
        from app.infrastructure.config.settings import settings
        from app.infrastructure.crypto.encryption import decrypt, is_encrypted
        if settings.encryption_key and is_encrypted(url):
            return decrypt(url, settings.encryption_key)
    except Exception as e:
        logger.debug("rtsp decrypt skipped: %s", e)
    return url


class CameraMapper:
    @staticmethod
    def to_entity(orm: CameraORM) -> Camera:
        return Camera(
            id=orm.id,
            name=orm.name,
            ip_address=orm.ip_address,
            network_id=orm.network_id,
            status=CameraStatus(orm.status),
            rtsp_url=_decrypt_rtsp(orm.rtsp_url),
            onvif_port=orm.onvif_port,
            manufacturer=orm.manufacturer,
            model=orm.model,
            firmware_version=orm.firmware_version,
            mac_address=orm.mac_address,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_orm(entity: Camera) -> CameraORM:
        return CameraORM(
            id=entity.id,
            name=entity.name,
            ip_address=entity.ip_address,
            network_id=entity.network_id,
            status=entity.status.value,
            rtsp_url=_encrypt_rtsp(entity.rtsp_url),
            onvif_port=entity.onvif_port,
            manufacturer=entity.manufacturer,
            model=entity.model,
            firmware_version=entity.firmware_version,
            mac_address=entity.mac_address,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class NetworkMapper:
    @staticmethod
    def to_entity(orm: NetworkORM) -> Network:
        return Network(
            id=orm.id,
            name=orm.name,
            subnet=orm.subnet,
            description=orm.description,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_orm(entity: Network) -> NetworkORM:
        return NetworkORM(
            id=entity.id,
            name=entity.name,
            subnet=entity.subnet,
            description=entity.description,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
