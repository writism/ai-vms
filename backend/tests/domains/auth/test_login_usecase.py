import pytest

from app.domains.auth.adapter.outbound.persistence.bcrypt_password_service import BcryptPasswordService
from app.domains.auth.adapter.outbound.persistence.in_memory_user_repository import InMemoryUserRepository
from app.domains.auth.adapter.outbound.persistence.jwt_token_service import JwtTokenService
from app.domains.auth.application.request.auth_request import LoginRequest
from app.domains.auth.application.usecase.login_usecase import LoginUseCase
from app.domains.auth.domain.entity.user import User, UserRole


@pytest.fixture
def user_repo():
    return InMemoryUserRepository()


@pytest.fixture
def password_service():
    return BcryptPasswordService()


@pytest.fixture
def token_service():
    return JwtTokenService()


@pytest.fixture
def login_usecase(user_repo, password_service, token_service):
    return LoginUseCase(user_repo, password_service, token_service)


@pytest.mark.anyio
async def test_login_success(user_repo, password_service, login_usecase):
    user = User(
        email="test@example.com",
        hashed_password=password_service.hash("password123"),
        name="Test User",
        role=UserRole.ADMIN,
    )
    await user_repo.save(user)

    result = await login_usecase.execute(LoginRequest(email="test@example.com", password="password123"))

    assert result is not None
    assert result.access_token
    assert result.token_type == "bearer"


@pytest.mark.anyio
async def test_login_wrong_password(user_repo, password_service, login_usecase):
    user = User(
        email="test@example.com",
        hashed_password=password_service.hash("password123"),
        name="Test User",
        role=UserRole.VIEWER,
    )
    await user_repo.save(user)

    result = await login_usecase.execute(LoginRequest(email="test@example.com", password="wrong"))

    assert result is None


@pytest.mark.anyio
async def test_login_user_not_found(login_usecase):
    result = await login_usecase.execute(LoginRequest(email="nobody@example.com", password="password"))

    assert result is None


@pytest.mark.anyio
async def test_login_inactive_user(user_repo, password_service, login_usecase):
    user = User(
        email="inactive@example.com",
        hashed_password=password_service.hash("password123"),
        name="Inactive",
        role=UserRole.VIEWER,
        is_active=False,
    )
    await user_repo.save(user)

    result = await login_usecase.execute(LoginRequest(email="inactive@example.com", password="password123"))

    assert result is None
