import pytest

from app.domains.camera.adapter.outbound.persistence.in_memory_camera_repository import InMemoryCameraRepository
from app.domains.camera.application.request.camera_request import RegisterCameraRequest
from app.domains.camera.application.usecase.register_camera_usecase import RegisterCameraUseCase
from app.domains.camera.application.usecase.get_camera_usecase import GetCameraUseCase, ListCamerasUseCase
from app.domains.camera.domain.entity.camera import CameraStatus


@pytest.fixture
def camera_repo():
    return InMemoryCameraRepository()


@pytest.mark.anyio
async def test_register_camera(camera_repo):
    usecase = RegisterCameraUseCase(camera_repo)
    request = RegisterCameraRequest(
        name="Camera 1",
        ip_address="192.168.1.100",
        rtsp_url="rtsp://192.168.1.100:554/stream",
        onvif_port=80,
    )

    result = await usecase.execute(request)

    assert result.name == "Camera 1"
    assert result.ip_address == "192.168.1.100"
    assert result.status == CameraStatus.OFFLINE
    assert result.rtsp_url == "rtsp://192.168.1.100:554/stream"


@pytest.mark.anyio
async def test_list_cameras(camera_repo):
    register = RegisterCameraUseCase(camera_repo)
    await register.execute(RegisterCameraRequest(name="Cam A", ip_address="10.0.0.1"))
    await register.execute(RegisterCameraRequest(name="Cam B", ip_address="10.0.0.2"))

    list_uc = ListCamerasUseCase(camera_repo)
    result = await list_uc.execute()

    assert len(result) == 2


@pytest.mark.anyio
async def test_get_camera_by_id(camera_repo):
    register = RegisterCameraUseCase(camera_repo)
    created = await register.execute(RegisterCameraRequest(name="Cam", ip_address="10.0.0.1"))

    get_uc = GetCameraUseCase(camera_repo)
    result = await get_uc.execute(created.id)

    assert result is not None
    assert result.name == "Cam"


@pytest.mark.anyio
async def test_get_camera_not_found(camera_repo):
    from uuid import uuid4
    get_uc = GetCameraUseCase(camera_repo)
    result = await get_uc.execute(uuid4())

    assert result is None
