from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class FaceMatch:
    identity_id: UUID
    face_id: UUID
    score: float
    identity_name: str

    @property
    def is_confirmed(self) -> bool:
        return self.score >= 0.75

    @property
    def needs_verification(self) -> bool:
        return 0.55 <= self.score < 0.75
