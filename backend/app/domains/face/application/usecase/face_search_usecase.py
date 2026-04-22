from app.domains.face.application.port.face_embedding_port import FaceEmbeddingPort
from app.domains.face.application.port.face_repository_port import FaceRepositoryPort
from app.domains.face.application.port.identity_repository_port import IdentityRepositoryPort
from app.domains.face.application.request.face_request import RegisterFaceRequest, SearchFaceRequest
from app.domains.face.application.response.face_response import FaceMatchResponse
from app.domains.face.domain.entity.face import Face


class RegisterFaceUseCase:
    def __init__(
        self,
        face_repo: FaceRepositoryPort,
        embedding_store: FaceEmbeddingPort,
    ):
        self._face_repo = face_repo
        self._embedding_store = embedding_store

    async def execute(self, request: RegisterFaceRequest) -> None:
        face = Face(
            identity_id=request.identity_id,
            embedding=request.embedding,
            image_path=request.image_path,
            quality_score=request.quality_score,
        )
        saved = await self._face_repo.save(face)
        await self._embedding_store.store(saved.id, saved.identity_id, saved.embedding)


class SearchFaceUseCase:
    def __init__(
        self,
        embedding_store: FaceEmbeddingPort,
        identity_repo: IdentityRepositoryPort,
    ):
        self._embedding_store = embedding_store
        self._identity_repo = identity_repo

    async def execute(self, request: SearchFaceRequest) -> list[FaceMatchResponse]:
        results = await self._embedding_store.search(
            embedding=request.embedding,
            limit=request.limit,
            threshold=request.threshold,
        )
        matches: list[FaceMatchResponse] = []
        for r in results:
            identity_name = "Unknown"
            if r.identity_id:
                identity = await self._identity_repo.find_by_id(r.identity_id)
                if identity:
                    identity_name = identity.name

            matches.append(
                FaceMatchResponse(
                    identity_id=r.identity_id or r.face_id,
                    face_id=r.face_id,
                    score=r.score,
                    identity_name=identity_name,
                    is_confirmed=r.score >= 0.75,
                    needs_verification=0.55 <= r.score < 0.75,
                )
            )
        return matches
