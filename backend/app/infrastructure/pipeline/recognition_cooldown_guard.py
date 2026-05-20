from datetime import datetime
from uuid import UUID


class RecognitionCooldownGuard:
    """(entity_id, camera_id) 조합 기준 인메모리 쿨다운 관리."""

    def __init__(self) -> None:
        self._last: dict[tuple[UUID, UUID], datetime] = {}

    def is_suppressed(
        self, entity_id: UUID, camera_id: UUID, cooldown_sec: float, now: datetime
    ) -> bool:
        last = self._last.get((entity_id, camera_id))
        if last is None:
            return False
        return (now - last).total_seconds() < cooldown_sec

    def elapsed_sec(self, entity_id: UUID, camera_id: UUID, now: datetime) -> float:
        last = self._last.get((entity_id, camera_id))
        return (now - last).total_seconds() if last else 0.0

    def mark(self, entity_id: UUID, camera_id: UUID, now: datetime) -> None:
        self._last[(entity_id, camera_id)] = now


identity_cooldown_guard = RecognitionCooldownGuard()
cluster_cooldown_guard = RecognitionCooldownGuard()
