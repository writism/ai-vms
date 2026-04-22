from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.domains.camera.adapter.inbound.api.dependencies import (
    get_list_networks_usecase,
    get_network_usecase,
    get_register_network_usecase,
)
from app.domains.camera.application.request.camera_request import RegisterNetworkRequest
from app.domains.camera.application.response.camera_response import NetworkResponse
from app.domains.camera.application.usecase.network_usecase import (
    GetNetworkUseCase,
    ListNetworksUseCase,
    RegisterNetworkUseCase,
)

router = APIRouter(prefix="/networks", tags=["network"])


@router.post("", response_model=NetworkResponse, status_code=201)
async def register_network(
    request: RegisterNetworkRequest,
    usecase: RegisterNetworkUseCase = Depends(get_register_network_usecase),
) -> NetworkResponse:
    return await usecase.execute(request)


@router.get("", response_model=list[NetworkResponse])
async def list_networks(
    usecase: ListNetworksUseCase = Depends(get_list_networks_usecase),
) -> list[NetworkResponse]:
    return await usecase.execute()


@router.get("/{network_id}", response_model=NetworkResponse)
async def get_network(
    network_id: UUID,
    usecase: GetNetworkUseCase = Depends(get_network_usecase),
) -> NetworkResponse:
    result = await usecase.execute(network_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Network not found")
    return result
