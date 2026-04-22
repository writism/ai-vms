from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass
class DetectedFaceResult:
    bbox: tuple[int, int, int, int]
    confidence: float
    embedding: list[float]
    quality_score: float


class FaceRecognitionPort(ABC):
    @abstractmethod
    async def detect_faces(self, frame: np.ndarray) -> list[DetectedFaceResult]: ...

    @abstractmethod
    def is_available(self) -> bool: ...
