from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.adapter.outbound.persistence.bcrypt_password_service import BcryptPasswordService
from app.domains.auth.adapter.outbound.persistence.in_memory_user_repository import InMemoryUserRepository
from app.domains.auth.adapter.outbound.persistence.jwt_token_service import JwtTokenService
from app.domains.auth.application.port.token_port import TokenPort
from app.domains.auth.application.port.user_repository_port import UserRepositoryPort
from app.domains.auth.application.usecase.get_user_usecase import GetCurrentUserUseCase
from app.domains.auth.application.usecase.login_usecase import LoginUseCase
from app.domains.auth.domain.entity.user import User
from app.infrastructure.config.settings import settings

_password_service = BcryptPasswordService()
_in_memory_user_repo = InMemoryUserRepository()
_token_service = JwtTokenService()

_security = HTTPBearer()


def _get_user_repo(session: AsyncSession | None = None) -> UserRepositoryPort:
    if settings.use_database and session:
        from app.domains.auth.adapter.outbound.persistence.sqlalchemy_user_repository import SqlAlchemyUserRepository
        return SqlAlchemyUserRepository(session)
    return _in_memory_user_repo


async def _get_session():
    if settings.use_database:
        from app.infrastructure.database.session import get_async_session
        async for session in get_async_session():
            yield session
    else:
        yield None


def get_login_usecase(session: AsyncSession | None = Depends(_get_session)) -> LoginUseCase:
    return LoginUseCase(_get_user_repo(session), _password_service, _token_service)


def get_user_repo(session: AsyncSession | None = Depends(_get_session)) -> UserRepositoryPort:
    return _get_user_repo(session)


def get_token_service() -> TokenPort:
    return _token_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
    session: AsyncSession | None = Depends(_get_session),
) -> User:
    payload = _token_service.decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    repo = _get_user_repo(session)
    user = await repo.find_by_id(UUID(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
