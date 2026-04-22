from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DetectedFace:
    bbox: tuple[int, int, int, int]
    confidence: float
    embedding: list[float]
    quality_score: float


class InsightFaceService:
    def __init__(self) -> None:
        self._app: Any = None
        self._loaded = False

    async def load_models(self) -> bool:
        try:
            from insightface.app import FaceAnalysis

            self._app = FaceAnalysis(
                name="buffalo_l",
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
            )
            self._app.prepare(ctx_id=0, det_size=(640, 640))
            self._loaded = True
            logger.info("InsightFace models loaded successfully")
            return True
        except Exception as e:
            logger.warning("InsightFace models not available: %s", e)
            self._loaded = False
            return False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    async def detect_and_embed(self, frame: np.ndarray) -> list[DetectedFace]:
        if not self._loaded:
            return []

        faces = self._app.get(frame)
        results: list[DetectedFace] = []

        for face in faces:
            if face.det_score < settings.face_quality_threshold:
                continue

            bbox = tuple(int(v) for v in face.bbox)
            embedding = face.normed_embedding.tolist()

            h, w = frame.shape[:2]
            bw = bbox[2] - bbox[0]
            bh = bbox[3] - bbox[1]
            quality = min(1.0, (bw * bh) / (w * h) * 50)

            results.append(
                DetectedFace(
                    bbox=(bbox[0], bbox[1], bbox[2], bbox[3]),
                    confidence=float(face.det_score),
                    embedding=embedding,
                    quality_score=quality,
                )
            )

        return results


insightface_service = InsightFaceService()
