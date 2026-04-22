from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.domains.auth.adapter.inbound.api.auth_router import router as auth_router
from app.domains.camera.adapter.inbound.api.camera_router import router as camera_router
from app.domains.camera.adapter.inbound.api.network_router import router as network_router
from app.domains.face.adapter.inbound.api.face_router import router as face_router
from app.domains.stream.adapter.inbound.api.stream_router import router as stream_router
from app.infrastructure.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(camera_router, prefix="/api")
app.include_router(network_router, prefix="/api")
app.include_router(stream_router, prefix="/api")
app.include_router(face_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.app_name}
