from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


@dataclass
class DangerDetectionResult:
    danger_type: str
    confidence: float
    bbox: tuple[int, int, int, int]


class DangerDetectionPort(ABC):
    @abstractmethod
    async def detect(self, frame: np.ndarray, confidence_threshold: float = 0.5) -> list[DangerDetectionResult]: ...

    @abstractmethod
    def is_available(self) -> bool: ...
