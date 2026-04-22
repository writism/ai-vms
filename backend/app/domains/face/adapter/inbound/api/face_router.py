from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.domains.face.adapter.inbound.api.dependencies import (
    get_identity_usecase,
    get_list_identities_usecase,
    get_register_face_usecase,
    get_register_identity_usecase,
    get_search_face_usecase,
)
from app.domains.face.application.request.face_request import (
    RegisterFaceRequest,
    RegisterIdentityRequest,
    SearchFaceRequest,
)
from app.domains.face.application.response.face_response import FaceMatchResponse, IdentityResponse
from app.domains.face.application.usecase.face_search_usecase import RegisterFaceUseCase, SearchFaceUseCase
from app.domains.face.application.usecase.identity_usecase import (
    GetIdentityUseCase,
    ListIdentitiesUseCase,
    RegisterIdentityUseCase,
)

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
