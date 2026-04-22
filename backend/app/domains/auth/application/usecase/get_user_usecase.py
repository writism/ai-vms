from uuid import UUID

from app.domains.auth.application.port.user_repository_port import UserRepositoryPort
from app.domains.auth.application.response.auth_response import UserResponse


class GetCurrentUserUseCase:
    def __init__(self, user_repo: UserRepositoryPort):
        self._user_repo = user_repo

    async def execute(self, user_id: UUID) -> UserResponse | None:
        user = await self._user_repo.find_by_id(user_id)
        if user is None:
            return None
        return UserResponse.from_entity(user)
