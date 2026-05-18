from fastapi import APIRouter, Depends

from app.domains.setting.adapter.inbound.api.dependencies import (
    get_get_settings_usecase,
    get_update_settings_usecase,
)
from app.domains.setting.application.request.setting_request import UpdateSettingsRequest
from app.domains.setting.application.response.setting_response import SettingsGroupResponse
from app.domains.setting.application.usecase.setting_usecase import (
    GetSettingsUseCase,
    UpdateSettingsUseCase,
)

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsGroupResponse)
async def get_settings(
    usecase: GetSettingsUseCase = Depends(get_get_settings_usecase),
) -> SettingsGroupResponse:
    return await usecase.execute()


@router.patch("", response_model=SettingsGroupResponse)
async def update_settings(
    request: UpdateSettingsRequest,
    usecase: UpdateSettingsUseCase = Depends(get_update_settings_usecase),
) -> SettingsGroupResponse:
    return await usecase.execute(request)
