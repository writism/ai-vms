from app.domains.face.adapter.outbound.external.qdrant_embedding_adapter import QdrantEmbeddingAdapter
from app.domains.face.adapter.outbound.persistence.in_memory_face_repository import InMemoryFaceRepository
from app.domains.face.adapter.outbound.persistence.in_memory_identity_repository import InMemoryIdentityRepository
from app.domains.face.application.usecase.face_search_usecase import RegisterFaceUseCase, SearchFaceUseCase
from app.domains.face.application.usecase.identity_usecase import (
    GetIdentityUseCase,
    ListIdentitiesUseCase,
    RegisterIdentityUseCase,
)

_identity_repo = InMemoryIdentityRepository()
_face_repo = InMemoryFaceRepository()
_embedding_store = QdrantEmbeddingAdapter()


def get_register_identity_usecase() -> RegisterIdentityUseCase:
    return RegisterIdentityUseCase(_identity_repo)


def get_list_identities_usecase() -> ListIdentitiesUseCase:
    return ListIdentitiesUseCase(_identity_repo)


def get_identity_usecase() -> GetIdentityUseCase:
    return GetIdentityUseCase(_identity_repo)


def get_register_face_usecase() -> RegisterFaceUseCase:
    return RegisterFaceUseCase(_face_repo, _embedding_store)


def get_search_face_usecase() -> SearchFaceUseCase:
    return SearchFaceUseCase(_embedding_store, _identity_repo)
