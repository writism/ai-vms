import numpy as np

from app.domains.alert.application.port.danger_detection_port import (
    DangerDetectionPort,
    DangerDetectionResult,
)
from app.infrastructure.ai.yolo_service import yolo_service


class YoloDangerAdapter(DangerDetectionPort):
    async def detect(self, frame: np.ndarray, confidence_threshold: float = 0.5) -> list[DangerDetectionResult]:
        detections = await yolo_service.detect(frame, confidence_threshold)
        return [
            DangerDetectionResult(
                danger_type=d.class_name,
                confidence=d.confidence,
                bbox=d.bbox,
            )
            for d in detections
        ]

    def is_available(self) -> bool:
        return yolo_service.is_loaded
