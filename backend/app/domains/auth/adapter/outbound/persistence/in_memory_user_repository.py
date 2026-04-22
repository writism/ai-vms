from uuid import UUID

from app.domains.auth.application.port.user_repository_port import UserRepositoryPort
from app.domains.auth.domain.entity.user import User


class InMemoryUserRepository(UserRepositoryPort):
    def __init__(self) -> None:
        self._store: dict[UUID, User] = {}

    async def save(self, user: User) -> User:
        self._store[user.id] = user
        return user

    async def find_by_id(self, user_id: UUID) -> User | None:
        return self._store.get(user_id)

    async def find_by_email(self, email: str) -> User | None:
        for user in self._store.values():
            if user.email == email:
                return user
        return None

    async def find_all(self) -> list[User]:
        return list(self._store.values())
