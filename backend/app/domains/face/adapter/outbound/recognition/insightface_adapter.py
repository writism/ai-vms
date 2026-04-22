from __future__ import annotations

from typing import TYPE_CHECKING

from app.domains.face.application.port.face_recognition_port import (
    DetectedFaceResult,
    FaceRecognitionPort,
)
from app.infrastructure.ai.insightface_service import insightface_service

if TYPE_CHECKING:
    import numpy as np


class InsightFaceAdapter(FaceRecognitionPort):
    async def detect_faces(self, frame: np.ndarray) -> list[DetectedFaceResult]:
        detected = await insightface_service.detect_and_embed(frame)
        return [
            DetectedFaceResult(
                bbox=d.bbox,
                confidence=d.confidence,
                embedding=d.embedding,
                quality_score=d.quality_score,
            )
            for d in detected
        ]

    def is_available(self) -> bool:
        return insightface_service.is_loaded
