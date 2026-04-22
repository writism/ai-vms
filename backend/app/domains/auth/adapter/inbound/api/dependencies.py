from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.domains.auth.adapter.outbound.persistence.bcrypt_password_service import BcryptPasswordService
from app.domains.auth.adapter.outbound.persistence.in_memory_user_repository import InMemoryUserRepository
from app.domains.auth.adapter.outbound.persistence.jwt_token_service import JwtTokenService
from app.domains.auth.application.port.token_port import TokenPort
from app.domains.auth.application.port.user_repository_port import UserRepositoryPort
from app.domains.auth.application.usecase.get_user_usecase import GetCurrentUserUseCase
from app.domains.auth.application.usecase.login_usecase import LoginUseCase
from app.domains.auth.domain.entity.user import User, UserRole

_password_service = BcryptPasswordService()
_user_repo = InMemoryUserRepository()
_token_service = JwtTokenService()

_security = HTTPBearer()

_seeded = False


async def _seed_admin() -> None:
    global _seeded
    if _seeded:
        return
    existing = await _user_repo.find_by_email("admin@ai-vms.local")
    if existing is None:
        admin = User(
            email="admin@ai-vms.local",
            hashed_password=_password_service.hash("admin1234"),
            name="관리자",
            role=UserRole.ADMIN,
        )
        await _user_repo.save(admin)
    _seeded = True


def get_login_usecase() -> LoginUseCase:
    return LoginUseCase(_user_repo, _password_service, _token_service)


def get_user_repo() -> UserRepositoryPort:
    return _user_repo


def get_token_service() -> TokenPort:
    return _token_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> User:
    await _seed_admin()
    payload = _token_service.decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    from uuid import UUID

    usecase = GetCurrentUserUseCase(_user_repo)
    user_response = await usecase.execute(UUID(user_id))
    if user_response is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    user = await _user_repo.find_by_id(UUID(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
