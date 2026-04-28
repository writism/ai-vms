import logging
import os
import uuid as uuid_mod
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.domains.face.adapter.inbound.api.dependencies import (
    get_delete_identity_usecase,
    get_face_repo,
    get_identity_usecase,
    get_list_identities_usecase,
    get_list_recognition_logs_usecase,
    get_register_face_usecase,
    get_register_identity_usecase,
    get_search_face_usecase,
    get_update_identity_usecase,
)
from app.domains.face.application.request.face_request import (
    RegisterFaceRequest,
    RegisterIdentityRequest,
    SearchFaceRequest,
    UpdateIdentityRequest,
)
from app.domains.face.application.port.face_repository_port import FaceRepositoryPort
from app.domains.face.application.response.face_response import FaceMatchResponse, IdentityResponse, RecognitionLogResponse
from app.domains.face.application.usecase.face_search_usecase import RegisterFaceUseCase, SearchFaceUseCase
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
            faces = await insightface_service.detect_and_embed(frame)
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
