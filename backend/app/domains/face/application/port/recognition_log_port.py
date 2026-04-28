from abc import ABC, abstractmethod

from app.domains.face.domain.entity.recognition_log import RecognitionLog


class RecognitionLogPort(ABC):
    @abstractmethod
    async def save(self, log: RecognitionLog) -> RecognitionLog: ...

    @abstractmethod
    async def find_recent(self, limit: int = 20) -> list[RecognitionLog]: ...
