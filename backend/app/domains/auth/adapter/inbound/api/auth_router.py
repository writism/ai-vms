from fastapi import APIRouter, Depends, HTTPException, status

from app.domains.auth.adapter.inbound.api.dependencies import get_current_user, get_login_usecase
from app.domains.auth.application.request.auth_request import LoginRequest
from app.domains.auth.application.response.auth_response import TokenResponse, UserResponse
from app.domains.auth.application.usecase.login_usecase import LoginUseCase
from app.domains.auth.domain.entity.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    usecase: LoginUseCase = Depends(get_login_usecase),
) -> TokenResponse:
    result = await usecase.execute(request)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return result


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.from_entity(current_user)
