from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    import numpy as np

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


def _detect_torch_gpu() -> tuple[bool, str]:
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            return True, name
        return False, "cpu"
    except ImportError:
        return False, "cpu"


class YoloService:
    def __init__(self) -> None:
        self._model: Any = None
        self._loaded = False
        self._use_gpu = False
        self._device = "cpu"

    async def load_model(self) -> bool:
        if not settings.danger_detection_enabled:
            logger.info("Danger detection is disabled in settings")
            return False
        try:
            from ultralytics import YOLO

            loop = asyncio.get_event_loop()
            self._use_gpu, gpu_name = await loop.run_in_executor(None, _detect_torch_gpu)
            self._device = "0" if self._use_gpu else "cpu"

            self._model = YOLO(settings.danger_model_path)
            self._loaded = True
            logger.info(
                "YOLO loaded: model=%s, device=%s (%s)",
                settings.danger_model_path,
                self._device,
                gpu_name,
            )
            return True
        except Exception as e:
            logger.warning("YOLO model not available: %s", e)
            self._loaded = False
            return False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def use_gpu(self) -> bool:
        return self._use_gpu

    async def detect(self, frame: np.ndarray, confidence_threshold: float = 0.5) -> list[DangerDetection]:
        if not self._loaded:
            return []

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: self._model(frame, verbose=False, conf=confidence_threshold, device=self._device),
        )
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
