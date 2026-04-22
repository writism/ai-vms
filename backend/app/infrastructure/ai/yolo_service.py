import logging
from dataclasses import dataclass

import numpy as np

from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class DangerDetection:
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]


DANGER_CLASS_MAP = {
    "fire": "FIRE",
    "smoke": "SMOKE",
    "weapon": "WEAPON",
    "knife": "WEAPON",
    "gun": "WEAPON",
}


class YoloService:
    def __init__(self) -> None:
        self._model = None
        self._loaded = False

    async def load_model(self) -> bool:
        if not settings.danger_detection_enabled:
            logger.info("Danger detection is disabled in settings")
            return False
        try:
            from ultralytics import YOLO

            self._model = YOLO(settings.danger_model_path)
            self._loaded = True
            logger.info("YOLO danger detection model loaded: %s", settings.danger_model_path)
            return True
        except Exception as e:
            logger.warning("YOLO model not available: %s", e)
            self._loaded = False
            return False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    async def detect(self, frame: np.ndarray, confidence_threshold: float = 0.5) -> list[DangerDetection]:
        if not self._loaded:
            return []

        results = self._model(frame, verbose=False, conf=confidence_threshold)
        detections: list[DangerDetection] = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                conf = float(box.conf[0])
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]

                mapped_name = DANGER_CLASS_MAP.get(class_name.lower(), class_name.upper())
                detections.append(
                    DangerDetection(
                        class_name=mapped_name,
                        confidence=conf,
                        bbox=(x1, y1, x2, y2),
                    )
                )

        return detections


yolo_service = YoloService()
