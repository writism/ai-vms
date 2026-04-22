# Skill: AI-VMS Implementation

## 목적

Backlog와 Todo를 입력하면
**AI-VMS의 Hexagonal Architecture 규칙에 따라 실제 동작 가능한 코드를 생성한다.**

---

# 아키텍처 준수 규칙

이 Skill이 생성하는 모든 코드는 다음 레이어 규칙을 따른다.

## Backend 구조 (Hexagonal Architecture)

```
Domain (순수 Python)
    ↑ 외부 의존 없음
Application (UseCase, Port)
    ↑ Domain만 의존
Adapter (Router, Repository Impl)
    ↑ Port를 구현
Infrastructure (ORM, AI Service, Config)
    ↑ 기술 상세
```

---

## Backend 디렉토리

```
backend/app/
├── domains/
│   └── <domain>/
│       ├── domain/
│       │   ├── entity/          # 도메인 엔티티 (dataclass)
│       │   ├── value_object/    # 값 객체
│       │   └── service/         # 도메인 서비스
│       ├── application/
│       │   ├── usecase/         # 유스케이스
│       │   ├── port/            # 아웃바운드 포트 (ABC)
│       │   ├── request/         # 입력 DTO
│       │   └── response/        # 출력 DTO
│       ├── adapter/
│       │   ├── inbound/api/     # FastAPI Router
│       │   └── outbound/
│       │       ├── persistence/ # Repository 구현
│       │       └── external/    # 외부 서비스 구현
│       └── infrastructure/
│           ├── orm/             # SQLAlchemy ORM 모델
│           └── mapper/          # Entity ↔ ORM 변환
└── infrastructure/
    ├── config/                  # Pydantic Settings
    ├── database/                # AsyncSession
    ├── ai/                      # InsightFace, YOLO, VLM 서비스
    ├── langgraph/               # Multi-Agent 그래프
    ├── onvif/                   # ONVIF 클라이언트
    ├── go2rtc/                  # go2rtc 클라이언트
    ├── cache/                   # Redis 클라이언트
    └── event_bus/               # Redis Pub/Sub + MQTT
```

---

## Domain 레이어

위치: `domains/<domain>/domain/`

역할

- 엔티티 정의 (dataclass)
- 값 객체 정의
- 도메인 비즈니스 규칙

금지 사항

- 외부 라이브러리 import 금지 (dataclass, typing, uuid, datetime만)
- ORM 모델 import 금지
- FastAPI 의존 금지

패턴

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class Camera:
    id: UUID
    name: str
    ip_address: str
    status: str
    rtsp_url: str | None = None
```

---

## Application 레이어

위치: `domains/<domain>/application/`

역할

- UseCase: 비즈니스 흐름 조율
- Port: 아웃바운드 인터페이스 (ABC)
- Request/Response: 입출력 DTO

패턴

```python
# Port (인터페이스)
from abc import ABC, abstractmethod

class CameraRepositoryPort(ABC):
    @abstractmethod
    async def save(self, camera: Camera) -> Camera: ...

    @abstractmethod
    async def find_by_id(self, id: UUID) -> Camera | None: ...

# UseCase
class RegisterCameraUseCase:
    def __init__(self, repo: CameraRepositoryPort):
        self._repo = repo

    async def execute(self, request: RegisterCameraRequest) -> CameraResponse:
        camera = Camera(...)
        saved = await self._repo.save(camera)
        return CameraResponse.from_entity(saved)
```

---

## Adapter 레이어

위치: `domains/<domain>/adapter/`

역할

- Inbound: FastAPI Router (HTTP 엔드포인트)
- Outbound: Port 구현체 (Repository, External Service)

패턴

```python
# Inbound (Router)
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/cameras", tags=["camera"])

@router.post("")
async def register_camera(
    request: RegisterCameraRequest,
    usecase: RegisterCameraUseCase = Depends(get_register_camera_usecase),
) -> CameraResponse:
    return await usecase.execute(request)

# Outbound (Repository)
class CameraRepositoryImpl(CameraRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, camera: Camera) -> Camera:
        orm = CameraMapper.to_orm(camera)
        self._session.add(orm)
        await self._session.flush()
        return CameraMapper.to_entity(orm)
```

---

## Infrastructure 레이어

위치: `domains/<domain>/infrastructure/` 및 `app/infrastructure/`

역할

- ORM 모델 (SQLAlchemy)
- Entity ↔ ORM Mapper
- AI 서비스 (InsightFace, YOLO, VLM)
- 외부 클라이언트 (go2rtc, ONVIF, Redis, MQTT)

패턴

```python
# ORM
from sqlalchemy.orm import Mapped, mapped_column

class CameraORM(Base):
    __tablename__ = "cameras"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    ip_address: Mapped[str] = mapped_column(String(45), unique=True)

# Mapper
class CameraMapper:
    @staticmethod
    def to_entity(orm: CameraORM) -> Camera:
        return Camera(id=orm.id, name=orm.name, ...)

    @staticmethod
    def to_orm(entity: Camera) -> CameraORM:
        return CameraORM(id=entity.id, name=entity.name, ...)
```

---

## Frontend 구조 (Feature-based DDD)

```
frontend/
├── app/                         # Next.js App Router (페이지)
├── features/
│   └── <feature>/
│       ├── domain/
│       │   ├── model/           # TypeScript 인터페이스
│       │   └── state/           # 상태 타입 (discriminated union)
│       ├── application/
│       │   ├── atoms/           # Jotai Atoms
│       │   └── hooks/           # Custom Hooks
│       ├── infrastructure/
│       │   └── api/             # API 호출 함수
│       └── ui/
│           └── components/      # React 컴포넌트
├── infrastructure/
│   ├── http/                    # httpClient
│   └── ws/                      # WebSocket 클라이언트
└── ui/
    └── components/              # 공통 UI (shadcn/ui)
```

---

## Frontend 패턴

```typescript
// domain/model
export interface Camera {
  id: string
  name: string
  ipAddress: string
  status: "ONLINE" | "OFFLINE" | "ERROR"
}

// domain/state (discriminated union)
export type CameraListState =
  | { status: "LOADING" }
  | { status: "LOADED"; cameras: Camera[] }
  | { status: "ERROR"; message: string }

// infrastructure/api
export const cameraApi = {
  discover: (subnet: string) =>
    httpClient.post<Camera[]>("/cameras/discover", { subnet }),
  list: () =>
    httpClient.get<Camera[]>("/cameras"),
}

// application/hooks
export function useCameraDiscovery() {
  const [state, setState] = useAtom(discoveryStateAtom)
  const discover = async (subnet: string) => {
    setState({ status: "LOADING" })
    const cameras = await cameraApi.discover(subnet)
    setState({ status: "LOADED", cameras })
  }
  return { state, discover }
}
```

---

# 도메인 목록

Backend 도메인

- camera (카메라 관리)
- face (얼굴 인식)
- alert (위험 감지/알림)
- stream (영상 스트리밍)
- event (이벤트/이력)
- agent (AI Multi-Agent)
- auth (인증/인가)
- setting (시스템 설정)

Frontend 피처

- camera (카메라)
- face (얼굴/인물)
- alert (알림)
- stream (영상)
- event (이벤트)
- auth (인증)
- notification (실시간 알림)

---

# 코드 생성 규칙

## 의존성 방향

- Domain은 외부 의존 없음
- Application은 Domain만 의존
- Adapter는 Application의 Port를 구현
- Infrastructure는 기술 상세 구현
- **역방향 의존 금지**

## 타입 안전

- Backend: Pydantic 모델 + dataclass
- Frontend: TypeScript strict mode

## 비동기

- Backend: async/await 전면 사용 (AsyncSession, httpx)
- Frontend: React hooks + SWR/Jotai

## 의존성 주입

- FastAPI의 Depends()를 사용하여 UseCase에 Port 구현체 주입

---

# 출력 규칙

출력은 **코드만 포함한다.**

설명, 주석, 문서는 생성하지 않는다.

출력 형식

파일 경로
코드 블록

예

backend/app/domains/camera/domain/entity/camera.py

```python
from dataclasses import dataclass
from uuid import UUID

@dataclass
class Camera:
    id: UUID
    name: str
    ip_address: str
```

frontend/features/camera/domain/model/camera.ts

```typescript
export interface Camera {
  id: string
  name: string
  ipAddress: string
  status: "ONLINE" | "OFFLINE" | "ERROR"
}
```

---

# 구현 순서

### System Backlog

1. Domain (Entity, Value Object)
2. Application (Port, UseCase, DTO)
3. Adapter Outbound (Repository Impl, External Impl)
4. Adapter Inbound (FastAPI Router)
5. Infrastructure (ORM, Mapper)

### UI Backlog

1. Domain (Model, State)
2. Infrastructure (API)
3. Application (Atoms, Hooks)
4. UI (Components)

### Behavior Backlog

1. Backend 전체 (Domain → Adapter)
2. Frontend 전체 (Domain → UI)

---

# 최종 규칙

모든 코드는 **AI-VMS의 Hexagonal Architecture를 준수한다.**

Domain 레이어에서 **외부 라이브러리를 import하면 안 된다.**

ORM 모델과 Domain Entity는 **반드시 분리한다.** (Mapper 사용)

UseCase는 **Port 인터페이스를 통해서만 외부에 접근한다.**

출력은 **코드만 생성한다.**
