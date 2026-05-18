import logging
import os
import uuid as uuid_mod
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.domains.face.adapter.inbound.api.dependencies import (
    get_cluster_snapshot_repo,
    get_delete_identity_usecase,
    get_embedding_store,
    get_face_repo,
    get_identity_repo,
    get_identity_usecase,
    get_list_face_suggestions_usecase,
    get_list_identities_usecase,
    get_list_recognition_logs_usecase,
    get_register_face_usecase,
    get_register_identity_usecase,
    get_resolve_face_suggestion_usecase,
    get_search_face_usecase,
    get_update_identity_usecase,
)
from app.domains.face.application.port.face_embedding_port import FaceEmbeddingPort
from app.domains.face.application.port.face_repository_port import FaceRepositoryPort
from app.domains.face.application.port.identity_repository_port import IdentityRepositoryPort
from app.domains.face.application.port.recognition_log_port import RecognitionLogPort
from app.domains.face.application.request.face_request import (
    RegisterFaceRequest,
    RegisterIdentityRequest,
    SearchFaceRequest,
    UpdateIdentityRequest,
)
from app.domains.face.application.response.face_response import (
    ClusterSnapshotResponse,
    FaceDetailResponse,
    FaceMatchResponse,
    FaceSuggestionResponse,
    IdentityResponse,
    OutlierSnapshotResponse,
    RecognitionLogResponse,
    SimilarIdentityResponse,
)
from app.domains.face.application.service.embedding_utils import compute_outlier_similarities
from app.domains.face.application.usecase.face_search_usecase import RegisterFaceUseCase, SearchFaceUseCase
from app.domains.face.application.usecase.face_suggestion_usecase import (
    ListFaceSuggestionsUseCase,
    ResolveFaceSuggestionUseCase,
)
from app.domains.face.application.usecase.identity_usecase import (
    DeleteIdentityUseCase,
    GetIdentityUseCase,
    ListIdentitiesUseCase,
    RegisterIdentityUseCase,
    UpdateIdentityUseCase,
)
from app.domains.face.application.usecase.recognition_log_usecase import ListRecognitionLogsUseCase

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads/faces"

router = APIRouter(prefix="/faces", tags=["face"])


@router.post("/identities", response_model=IdentityResponse, status_code=201)
async def register_identity(
    request: RegisterIdentityRequest,
    usecase: RegisterIdentityUseCase = Depends(get_register_identity_usecase),
) -> IdentityResponse:
    return await usecase.execute(request)


@router.get("/identities", response_model=list[IdentityResponse])
async def list_identities(
    usecase: ListIdentitiesUseCase = Depends(get_list_identities_usecase),
) -> list[IdentityResponse]:
    return await usecase.execute()


@router.get("/identities/{identity_id}", response_model=IdentityResponse)
async def get_identity(
    identity_id: UUID,
    usecase: GetIdentityUseCase = Depends(get_identity_usecase),
) -> IdentityResponse:
    result = await usecase.execute(identity_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Identity not found")
    return result


@router.put("/identities/{identity_id}", response_model=IdentityResponse)
async def update_identity(
    identity_id: UUID,
    request: UpdateIdentityRequest,
    usecase: UpdateIdentityUseCase = Depends(get_update_identity_usecase),
) -> IdentityResponse:
    result = await usecase.execute(identity_id, request)
    if result is None:
        raise HTTPException(status_code=404, detail="Identity not found")
    return result


@router.delete("/identities/{identity_id}", status_code=204)
async def delete_identity(
    identity_id: UUID,
    usecase: DeleteIdentityUseCase = Depends(get_delete_identity_usecase),
) -> None:
    deleted = await usecase.execute(identity_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Identity not found")


@router.post("/identities/{identity_id}/photo", status_code=201)
async def upload_face_photo(
    identity_id: UUID,
    file: UploadFile,
    identity_usecase: GetIdentityUseCase = Depends(get_identity_usecase),
    face_usecase: RegisterFaceUseCase = Depends(get_register_face_usecase),
    face_repo: FaceRepositoryPort = Depends(get_face_repo),
) -> dict:
    identity = await identity_usecase.execute(identity_id)
    if identity is None:
        raise HTTPException(status_code=404, detail="Identity not found")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "photo.jpg")[1] or ".jpg"
    filename = f"{uuid_mod.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    embedding: list[float] = []
    quality_score = 0.0
    try:
        from app.infrastructure.ai.insightface_service import insightface_service
        if insightface_service.is_loaded:
            import numpy as np
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(content)).convert("RGB")
            frame = np.array(img)
            faces = await insightface_service.detect_and_embed_for_registration(frame)
            if faces:
                embedding = faces[0].embedding
                quality_score = faces[0].quality_score
    except Exception as e:
        logger.warning("Face embedding extraction skipped: %s", e)

    if embedding:
        req = RegisterFaceRequest(
            identity_id=identity_id,
            embedding=embedding,
            image_path=filepath,
            quality_score=quality_score,
        )
        await face_usecase.execute(req)
    else:
        from app.domains.face.domain.entity.face import Face
        face = Face(identity_id=identity_id, embedding=[], image_path=filepath)
        await face_repo.save(face)

    return {"status": "ok", "image_path": filepath, "has_embedding": bool(embedding)}


@router.post("/register", status_code=201)
async def register_face(
    request: RegisterFaceRequest,
    usecase: RegisterFaceUseCase = Depends(get_register_face_usecase),
) -> dict:
    await usecase.execute(request)
    return {"status": "ok"}


@router.post("/search", response_model=list[FaceMatchResponse])
async def search_face(
    request: SearchFaceRequest,
    usecase: SearchFaceUseCase = Depends(get_search_face_usecase),
) -> list[FaceMatchResponse]:
    return await usecase.execute(request)


@router.get("/recognition-logs", response_model=list[RecognitionLogResponse])
async def list_recognition_logs(
    limit: int = 20,
    usecase: ListRecognitionLogsUseCase = Depends(get_list_recognition_logs_usecase),
) -> list[RecognitionLogResponse]:
    return await usecase.execute(limit)


@router.get("/suggestions", response_model=list[FaceSuggestionResponse])
async def list_face_suggestions(
    usecase: ListFaceSuggestionsUseCase = Depends(get_list_face_suggestions_usecase),
) -> list[FaceSuggestionResponse]:
    return await usecase.execute()


@router.post("/suggestions/{cluster_id}/register", status_code=204)
async def register_face_suggestion(
    cluster_id: UUID,
    identity_id: UUID,
    usecase: ResolveFaceSuggestionUseCase = Depends(get_resolve_face_suggestion_usecase),
) -> None:
    ok = await usecase.register(cluster_id, identity_id)
    if not ok:
        raise HTTPException(status_code=404, detail="cluster not found")


@router.post("/suggestions/{cluster_id}/ignore", status_code=204)
async def ignore_face_suggestion(
    cluster_id: UUID,
    usecase: ResolveFaceSuggestionUseCase = Depends(get_resolve_face_suggestion_usecase),
) -> None:
    ok = await usecase.ignore(cluster_id)
    if not ok:
        raise HTTPException(status_code=404, detail="cluster not found")


@router.get("/recognition-logs/{log_id}/match", response_model=list[SimilarIdentityResponse])
async def match_recognition_log(
    log_id: UUID,
    limit: int = 5,
    log_repo: RecognitionLogPort = Depends(get_cluster_snapshot_repo),
    identity_repo: IdentityRepositoryPort = Depends(get_identity_repo),
    embedding_store: FaceEmbeddingPort = Depends(get_embedding_store),
) -> list[SimilarIdentityResponse]:
    """미등록 로그의 embedding으로 Qdrant 검색 → 유사 등록 인물 반환."""
    log = await log_repo.find_by_id(log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="log not found")
    if not log.embedding:
        return []

    results = await embedding_store.search(embedding=log.embedding, limit=limit, threshold=0.0)
    identity_results = [r for r in results if r.identity_id is not None]
    if not identity_results:
        return []

    # identity별 최고 score만 남김
    best: dict = {}
    for r in identity_results:
        iid = str(r.identity_id)
        if iid not in best or r.score > best[iid].score:
            best[iid] = r

    top_results = sorted(best.values(), key=lambda x: x.score, reverse=True)[:limit]
    identity_ids = [r.identity_id for r in top_results if r.identity_id]
    identities = await identity_repo.find_by_ids(identity_ids)
    identity_map = {i.id: i for i in identities}

    return [
        SimilarIdentityResponse(
            identity_id=idt.id,
            name=idt.name,
            position=idt.position,
            department=idt.department,
            identity_type=idt.identity_type.value,
            face_image_url=idt.face_image_url,
            score=round(r.score * 100, 1),
        )
        for r in top_results
        if (idt := identity_map.get(r.identity_id)) is not None
    ]


@router.post("/recognition-logs/{log_id}/assign", status_code=200)
async def assign_recognition_log(
    log_id: UUID,
    identity_id: UUID,
    log_repo: RecognitionLogPort = Depends(get_cluster_snapshot_repo),
    identity_usecase: GetIdentityUseCase = Depends(get_identity_usecase),
) -> dict:
    """미등록 로그(및 동일 cluster)를 기존 identity에 매칭 등록."""
    log = await log_repo.find_by_id(log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="log not found")

    identity = await identity_usecase.execute(identity_id)
    if identity is None:
        raise HTTPException(status_code=404, detail="identity not found")

    if log.cluster_id:
        count = await log_repo.assign_cluster_to_identity(
            cluster_id=log.cluster_id,
            identity_id=identity_id,
            identity_name=identity.name,
            identity_type=identity.identity_type.value,
        )
    else:
        count = 0
    return {"assigned": count, "identity_name": identity.name}


@router.get("/clusters/{cluster_id}/snapshots", response_model=list[ClusterSnapshotResponse])
async def get_cluster_snapshots(
    cluster_id: UUID,
    limit: int = 50,
    log_repo: RecognitionLogPort = Depends(get_cluster_snapshot_repo),
) -> list[ClusterSnapshotResponse]:
    logs = await log_repo.find_by_cluster(cluster_id, limit)
    return [
        ClusterSnapshotResponse(
            log_id=log.id,
            image_url=f"/{log.image_path}",
            confidence=log.confidence,
            created_at=log.created_at,
        )
        for log in logs
    ]


@router.delete("/clusters/{cluster_id}/snapshots/{log_id}", status_code=204)
async def delete_cluster_snapshot(
    cluster_id: UUID,
    log_id: UUID,
    log_repo: RecognitionLogPort = Depends(get_cluster_snapshot_repo),
) -> None:
    deleted = await log_repo.delete_by_id(log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="snapshot not found")


@router.get("/clusters/{cluster_id}/outliers", response_model=list[OutlierSnapshotResponse])
async def get_cluster_outliers(
    cluster_id: UUID,
    threshold: float = 0.75,
    log_repo: RecognitionLogPort = Depends(get_cluster_snapshot_repo),
) -> list[OutlierSnapshotResponse]:
    logs = await log_repo.find_by_cluster(cluster_id, limit=200)
    logs_with_emb = [l for l in logs if l.embedding]
    if not logs_with_emb:
        return []

    similarities = compute_outlier_similarities([l.embedding for l in logs_with_emb])

    return [
        OutlierSnapshotResponse(
            log_id=log.id,
            image_url=f"/{log.image_path}",
            confidence=log.confidence,
            created_at=log.created_at,
            is_outlier=sim < threshold,
            similarity_to_mean=round(float(sim), 4),
        )
        for log, sim in zip(logs_with_emb, similarities)
    ]


@router.get("/identities/{identity_id}/faces", response_model=list[FaceDetailResponse])
async def list_identity_faces(
    identity_id: UUID,
    face_repo: FaceRepositoryPort = Depends(get_face_repo),
) -> list[FaceDetailResponse]:
    faces = await face_repo.find_by_identity_id(identity_id)
    if not faces:
        return []

    faces_with_emb = [f for f in faces if f.embedding]
    outlier_ids: set = set()
    if len(faces_with_emb) >= 3:
        similarities = compute_outlier_similarities([f.embedding for f in faces_with_emb])
        for face, sim in zip(faces_with_emb, similarities):
            if sim < 0.75:
                outlier_ids.add(face.id)

    return [
        FaceDetailResponse(
            face_id=f.id,
            image_url=f"/{f.image_path}" if f.image_path else None,
            quality_score=f.quality_score or 0.0,
            created_at=f.created_at,
            is_outlier=f.id in outlier_ids,
        )
        for f in faces
    ]


@router.delete("/identities/{identity_id}/faces/{face_id}", status_code=204)
async def delete_identity_face(
    identity_id: UUID,
    face_id: UUID,
    face_repo: FaceRepositoryPort = Depends(get_face_repo),
    embedding_store: FaceEmbeddingPort = Depends(get_embedding_store),
) -> None:
    face = await face_repo.find_by_id(face_id)
    if face is None or face.identity_id != identity_id:
        raise HTTPException(status_code=404, detail="face not found")
    if face.image_path:
        try:
            os.remove(face.image_path)
        except OSError:
            pass
    try:
        await embedding_store.delete(face_id)
    except Exception:
        pass
    await face_repo.delete(face_id)
