# Command: /implement

## 목적

사용자가 Backlog와 Todo를 입력하면
해당 Backlog를 구현하기 위한 코드를 생성한다.

이 Command는 다음을 수행한다.

- Backlog Title을 이해한다
- Success Criteria를 구현 기준으로 사용한다
- Todo 목록을 기반으로 구현 단계를 수행한다
- AI-VMS Hexagonal Architecture에 맞는 실제 동작 가능한 코드를 생성한다

이 Command는 다음 규칙을 사용한다.

.claude/skills/IMPLEMENTATION.md

---

## 중요 규칙 (Strict)

이 Command는 **Backlog 구현 명령**이다.

다음 항목을 생성하지 않는다.

- Given
- When
- Then
- Scenario
- Test Case
- Architecture 설계
- Component specification
- Props 정의 문서
- API 설계 문서

이 Command는 **문서를 생성하지 않는다.**

반드시 **코드 구현 결과만 생성한다.**

---

## 사용 방법

/implement

입력 예시

Backlog

위험 감지 엔진이 화재를 감지하고 관리자에게 알림을 발송한다

Success Criteria

- YOLO11 모델이 RTSP 프레임에서 화재/연기를 감지한다
- severity가 HIGH 이상이면 WebSocket으로 실시간 알림이 발송된다
- 감지 이벤트가 danger_events 테이블에 저장된다
- 스냅샷 이미지가 저장되고 이벤트에 연결된다

Todo

1. YOLO11 추론 서비스에서 화재/연기 감지 로직을 구현한다
2. severity 평가 로직을 적용하여 danger_event를 생성한다
3. Redis Pub/Sub + MQTT로 이벤트를 발행한다

---

## 동작 규칙

1. Backlog Title을 읽는다
2. Success Criteria를 구현 기준으로 사용한다
3. Todo 목록을 구현 순서로 사용한다
4. Todo 단위로 코드를 생성한다
5. 실제 동작 가능한 코드만 생성한다

---

## 구현 순서

Backlog Type에 따라 구현 레이어가 다르다.

### System Backlog (Backend)

1. Domain (Entity, Value Object, Domain Service)
2. Application (Port 인터페이스, UseCase, Request/Response DTO)
3. Adapter Outbound (Repository Impl, External Service Impl)
4. Adapter Inbound (FastAPI Router)
5. Infrastructure (ORM, Mapper, AI Service, Config)

### UI Backlog (Frontend)

1. Domain (Model 인터페이스, State 타입)
2. Infrastructure (API 호출)
3. Application (Atoms, Hooks)
4. UI (Components)

### Behavior Backlog (Backend + Frontend)

1. Backend: Domain → Application → Adapter → Infrastructure
2. Frontend: Domain → Infrastructure → Application → UI

모든 레이어가 필요하지 않은 경우 해당 레이어만 구현한다.

---

## 출력 형식

Implementation

설명 없이 **코드만 출력한다.**

코드는 다음 형식을 따른다.

- 파일 경로
- 코드 블록

예

backend/app/domains/alert/domain/entity/danger_event.py

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class DangerEvent:
    id: UUID
    camera_id: UUID
    danger_type: str
    severity: str
    confidence: float
    timestamp: datetime
```

backend/app/domains/alert/application/port/danger_detection_port.py

```python
from abc import ABC, abstractmethod

class DangerDetectionPort(ABC):
    @abstractmethod
    async def detect(self, frame: bytes) -> list[DetectionResult]:
        ...
```
