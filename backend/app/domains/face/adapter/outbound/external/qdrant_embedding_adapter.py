import logging
from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.domains.face.application.port.face_embedding_port import EmbeddingSearchResult, FaceEmbeddingPort
from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "face_embeddings"


class QdrantEmbeddingAdapter(FaceEmbeddingPort):
    def __init__(self, url: str | None = None):
        self._url = url or settings.qdrant_url
        self._client: AsyncQdrantClient | None = None

    async def _get_client(self) -> AsyncQdrantClient:
        if self._client is None:
            self._client = AsyncQdrantClient(url=self._url)
            collections = await self._client.get_collections()
            names = [c.name for c in collections.collections]
            if COLLECTION_NAME not in names:
                await self._client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=settings.embedding_dimension,
                        distance=Distance.COSINE,
                    ),
                )
        return self._client

    async def store(self, face_id: UUID, identity_id: UUID | None, embedding: list[float]) -> None:
        client = await self._get_client()
        await client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=str(face_id),
                    vector=embedding,
                    payload={"identity_id": str(identity_id) if identity_id else None},
                )
            ],
        )

    async def search(self, embedding: list[float], limit: int = 5, threshold: float = 0.55) -> list[EmbeddingSearchResult]:
        client = await self._get_client()
        results = await client.search(
            collection_name=COLLECTION_NAME,
            query_vector=embedding,
            limit=limit,
            score_threshold=threshold,
        )
        return [
            EmbeddingSearchResult(
                face_id=UUID(str(r.id)),
                identity_id=UUID(r.payload["identity_id"]) if r.payload and r.payload.get("identity_id") else None,
                score=r.score,
            )
            for r in results
        ]

    async def delete(self, face_id: UUID) -> bool:
        client = await self._get_client()
        await client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=[str(face_id)],
        )
        return True
