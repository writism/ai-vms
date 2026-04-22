from app.domains.auth.application.port.password_port import PasswordPort
from app.domains.auth.application.port.token_port import TokenPort
from app.domains.auth.application.port.user_repository_port import UserRepositoryPort
from app.domains.auth.application.request.auth_request import LoginRequest
from app.domains.auth.application.response.auth_response import TokenResponse


class LoginUseCase:
    def __init__(self, user_repo: UserRepositoryPort, password_service: PasswordPort, token_service: TokenPort):
        self._user_repo = user_repo
        self._password_service = password_service
        self._token_service = token_service

    async def execute(self, request: LoginRequest) -> TokenResponse | None:
        user = await self._user_repo.find_by_email(request.email)
        if user is None:
            return None
        if not user.is_active:
            return None
        if not self._password_service.verify(request.password, user.hashed_password):
            return None
        token_pair = self._token_service.create_access_token(user.id, user.role.value)
        return TokenResponse(access_token=token_pair.access_token, token_type=token_pair.token_type)
