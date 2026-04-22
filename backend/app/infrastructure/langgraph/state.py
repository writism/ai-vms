from dataclasses import dataclass, field
from typing import TypedDict


@dataclass
class DetectionResult:
    type: str
    label: str
    confidence: float
    bbox: tuple[int, int, int, int] | None = None
    embedding: list[float] | None = None
    identity_id: str | None = None
    identity_name: str | None = None


@dataclass
class AnalysisResult:
    summary: str
    severity: float
    recognized_faces: list[str] = field(default_factory=list)
    danger_types: list[str] = field(default_factory=list)
    requires_alert: bool = False


@dataclass
class Action:
    type: str
    target: str
    payload: dict = field(default_factory=dict)


class AgentState(TypedDict, total=False):
    camera_id: str
    frame_data: bytes | None
    detection_results: list[DetectionResult]
    analysis: AnalysisResult | None
    actions: list[Action]
    severity: float
    error: str | None
