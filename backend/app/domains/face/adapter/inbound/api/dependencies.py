from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.face.adapter.outbound.external.qdrant_embedding_adapter import QdrantEmbeddingAdapter
from app.domains.face.adapter.outbound.persistence.in_memory_face_repository import InMemoryFaceRepository
from app.domains.face.adapter.outbound.persistence.in_memory_identity_repository import InMemoryIdentityRepository
from app.domains.face.application.port.face_repository_port import FaceRepositoryPort
from app.domains.face.application.port.identity_repository_port import IdentityRepositoryPort
from app.domains.face.application.usecase.face_search_usecase import RegisterFaceUseCase, SearchFaceUseCase
from app.domains.face.application.usecase.identity_usecase import (
    GetIdentityUseCase,
    ListIdentitiesUseCase,
    RegisterIdentityUseCase,
)
from app.infrastructure.config.settings import settings

_in_memory_identity_repo = InMemoryIdentityRepository()
_in_memory_face_repo = InMemoryFaceRepository()
_embedding_store = QdrantEmbeddingAdapter()


def _get_identity_repo(session: AsyncSession | None = None) -> IdentityRepositoryPort:
    if settings.use_database and session:
        from app.domains.face.adapter.outbound.persistence.sqlalchemy_identity_repository import SqlAlchemyIdentityRepository
        return SqlAlchemyIdentityRepository(session)
    return _in_memory_identity_repo


def _get_face_repo(session: AsyncSession | None = None) -> FaceRepositoryPort:
    if settings.use_database and session:
        from app.domains.face.adapter.outbound.persistence.sqlalchemy_face_repository import SqlAlchemyFaceRepository
        return SqlAlchemyFaceRepository(session)
    return _in_memory_face_repo


def get_register_identity_usecase() -> RegisterIdentityUseCase:
    return RegisterIdentityUseCase(_get_identity_repo())


def get_list_identities_usecase() -> ListIdentitiesUseCase:
    return ListIdentitiesUseCase(_get_identity_repo())


def get_identity_usecase() -> GetIdentityUseCase:
    return GetIdentityUseCase(_get_identity_repo())


def get_register_face_usecase() -> RegisterFaceUseCase:
    return RegisterFaceUseCase(_get_face_repo(), _embedding_store)


def get_search_face_usecase() -> SearchFaceUseCase:
    return SearchFaceUseCase(_embedding_store, _get_identity_repo())
