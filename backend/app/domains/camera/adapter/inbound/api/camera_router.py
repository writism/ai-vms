from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.domains.camera.adapter.inbound.api.dependencies import (
    get_batch_register_cameras_usecase,
    get_camera_usecase,
    get_discover_cameras_usecase,
    get_list_cameras_usecase,
    get_register_camera_usecase,
)
from app.domains.camera.application.request.camera_request import RegisterCameraRequest
from app.domains.camera.application.request.discovery_request import BatchRegisterCamerasRequest, DiscoverCamerasRequest
from app.domains.camera.application.response.camera_response import CameraResponse
from app.domains.camera.application.response.discovery_response import DiscoveredCameraResponse
from app.domains.camera.application.usecase.discover_cameras_usecase import (
    BatchRegisterCamerasUseCase,
    DiscoverCamerasUseCase,
)
from app.domains.camera.application.usecase.get_camera_usecase import GetCameraUseCase, ListCamerasUseCase
from app.domains.camera.application.usecase.register_camera_usecase import RegisterCameraUseCase

router = APIRouter(prefix="/cameras", tags=["camera"])


@router.post("", response_model=CameraResponse, status_code=201)
async def register_camera(
    request: RegisterCameraRequest,
    usecase: RegisterCameraUseCase = Depends(get_register_camera_usecase),
) -> CameraResponse:
    return await usecase.execute(request)


@router.get("", response_model=list[CameraResponse])
async def list_cameras(
    usecase: ListCamerasUseCase = Depends(get_list_cameras_usecase),
) -> list[CameraResponse]:
    return await usecase.execute()


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: UUID,
    usecase: GetCameraUseCase = Depends(get_camera_usecase),
) -> CameraResponse:
    result = await usecase.execute(camera_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return result


@router.post("/discover", response_model=list[DiscoveredCameraResponse])
async def discover_cameras(
    request: DiscoverCamerasRequest,
    usecase: DiscoverCamerasUseCase = Depends(get_discover_cameras_usecase),
) -> list[DiscoveredCameraResponse]:
    return await usecase.execute(request)


@router.post("/batch", response_model=list[CameraResponse], status_code=201)
async def batch_register_cameras(
    request: BatchRegisterCamerasRequest,
    usecase: BatchRegisterCamerasUseCase = Depends(get_batch_register_cameras_usecase),
) -> list[CameraResponse]:
    return await usecase.execute(request)
