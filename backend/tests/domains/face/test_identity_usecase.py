import pytest
from uuid import uuid4

from app.domains.face.adapter.outbound.persistence.in_memory_identity_repository import InMemoryIdentityRepository
from app.domains.face.application.request.face_request import RegisterIdentityRequest
from app.domains.face.application.usecase.identity_usecase import (
    GetIdentityUseCase,
    ListIdentitiesUseCase,
    RegisterIdentityUseCase,
)


@pytest.fixture
def identity_repo():
    return InMemoryIdentityRepository()


@pytest.mark.anyio
async def test_register_identity(identity_repo):
    usecase = RegisterIdentityUseCase(identity_repo)
    result = await usecase.execute(
        RegisterIdentityRequest(
            name="홍길동",
            identity_type="INTERNAL",
            department="개발팀",
            employee_id="EMP001",
        )
    )

    assert result.name == "홍길동"
    assert result.identity_type == "INTERNAL"
    assert result.department == "개발팀"


@pytest.mark.anyio
async def test_list_identities(identity_repo):
    register = RegisterIdentityUseCase(identity_repo)
    await register.execute(RegisterIdentityRequest(name="User A", identity_type="INTERNAL"))
    await register.execute(RegisterIdentityRequest(name="User B", identity_type="VIP"))

    list_uc = ListIdentitiesUseCase(identity_repo)
    result = await list_uc.execute()

    assert len(result) == 2


@pytest.mark.anyio
async def test_get_identity(identity_repo):
    register = RegisterIdentityUseCase(identity_repo)
    created = await register.execute(RegisterIdentityRequest(name="Target", identity_type="EXTERNAL"))

    get_uc = GetIdentityUseCase(identity_repo)
    result = await get_uc.execute(created.id)

    assert result is not None
    assert result.name == "Target"


@pytest.mark.anyio
async def test_get_identity_not_found(identity_repo):
    get_uc = GetIdentityUseCase(identity_repo)
    result = await get_uc.execute(uuid4())

    assert result is None
