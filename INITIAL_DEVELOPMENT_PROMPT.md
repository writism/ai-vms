# AI Multi-Agent 기반 영상 관리/관제 시스템 (AI-VMS) 초기 개발 프롬프트

> **이 문서는 AI 코딩 도구 기준으로 검토 및 보완하였습니다.**
> 기존 초안의 방향은 유지하되, 실제 구현 지시서로 바로 사용할 수 있도록 표기 충돌, 우선순위, 검증 기준을 정리했습니다.
> 다른 AI 모델 또는 사람 리뷰어와의 교차검증을 통해 내용의 정확성과 설계 적합성을 최종 확인하시기 바랍니다.
> 작성일: 2026-04-22

## 1. 프로젝트 개요

### 1.1 목적
AI Multi-Agent 기반 영상 관리/관제 웹 서비스를 개발한다.
기존 VMS(Video Management System)의 기능에 AI 에이전트를 결합하여 IP 카메라 자동 검색, 얼굴 인식 기반 내부/외부인 구별, 위험 상황(화재, 폭력, 싸움 등) 자동 인식 및 관리자 알림 기능을 제공한다.

### 1.2 핵심 기능
1. **IP 카메라 자동 검색 및 등록**: 지정 네트워크에서 ONVIF WS-Discovery를 통해 IP 카메라를 자동 검색하고 DB에 등록
2. **얼굴 인식 기반 출입 관리**: 영상 스트림에서 실시간 얼굴 인식 → 등록된 내부인/미등록 외부인 구별
3. **위험 상황 감지 및 알림**: 화재, 폭력, 싸움, 침입 등 이상 상황 AI 감지 → 관리자에게 즉시 알림/경고

### 1.3 기술 스택

| 레이어 | 기술 | 비고 |
|--------|------|------|
| **Backend** | Python 3.12+ / FastAPI | 비동기 ASGI, Hexagonal Architecture |
| **Frontend** | Next.js 15+ / TypeScript / React 19 | App Router, Feature-based DDD |
| **얼굴 인식** | InsightFace (SCRFD + ArcFace) | 감지: SCRFD (경량), 임베딩: ArcFace 512d |
| **얼굴 인식 (저화질)** | AdaFace | 저해상도/야간 카메라 대응 (CVPR 2022) |
| **객체 탐지** | Ultralytics YOLO11 | 화재/연기/무기 등 커스텀 학습 |
| **행동 인식** | Pose Estimation + LSTM | 폭력/싸움/쓰러짐 감지 (MediaPipe/MMPose) |
| **장면 분석 (VLM)** | Qwen2.5-VL-7B / StreamingVLM | 실시간 영상 스트림 장면 이해 |
| **Multi-Agent** | LangGraph | Planner→Detector→Analyzer→Dispatcher |
| **Vector DB** | Qdrant | 얼굴 임베딩 유사도 검색 (512차원, HNSW) |
| **RDBMS** | PostgreSQL 16 | 구조화 데이터 |
| **Cache/Pub-Sub** | Redis 7 | 세션, 실시간 이벤트 브로커 |
| **이벤트 버스** | MQTT (mosquitto) | IoT/카메라 생태계 표준, 외부 시스템 연동 |
| **영상 스트리밍** | go2rtc | RTSP→WebRTC/HLS 트랜스코딩 (내장 또는 외부 서버 연동) |
| **ONVIF** | python-onvif-zeep-async | 비동기 WS-Discovery, PTZ, 프로파일 |
| **GPU 추론 최적화** | ONNX Runtime / TensorRT | 모델 추론 가속 (NVIDIA GPU) |
| **컨테이너** | Docker Compose | GPU(NVIDIA Container Toolkit) 지원 |
| **상태관리 (FE)** | Jotai + SWR | 경량 atom 기반 + 서버 상태 |
| **UI** | Tailwind CSS + shadcn/ui | 반응형, 다크모드 |

### 1.4 AI 코딩 도구 실행 원칙
이 문서를 개발 지시서로 사용할 때 AI 코딩 도구는 아래 원칙을 따른다.

1. **Phase 단위로 구현**: Phase 1부터 순차 진행하고, 선행 단계의 산출물 없이 다음 단계로 점프하지 않는다.
2. **MVP 우선 구현**: 카메라 검색, 라이브뷰, 얼굴 등록/검색, 위험 이벤트 생성/알림까지를 우선 완료한다.
3. **결정 사항은 문서에 환류**: 구현 중 설계 변경이 발생하면 "왜 바뀌었는지"를 이 문서 또는 별도 ADR에 남긴다.
4. **런타임 모델과 편집 모델을 분리**: AI 코딩 도구는 문서 작성/코드 생성용이며, 실제 LangGraph/VLM 런타임 모델은 환경변수로 분리 관리한다.
5. **검증 가능한 결과만 보고**: "구현 완료"라고 쓰지 말고 API 동작, UI 플로우, 테스트/수동 검증 결과를 함께 남긴다.

### 1.5 MVP 범위와 후순위 범위

**MVP에 포함:**
- ONVIF 카메라 검색 및 수동 등록
- go2rtc 기반 WebRTC 라이브뷰
- 인물/얼굴 등록, 얼굴 검색, 미식별 얼굴 클러스터 관리
- 위험 이벤트 감지, 저장, 실시간 WebSocket 알림
- 관리자 로그인, 기본 대시보드, 이벤트 타임라인

**MVP 이후로 미루기:**
- PTZ 자동 추적
- 멀티 에이전트의 복잡한 자율 계획 기능
- VLM 기반 상세 상황 설명의 상시 실행
- 외부 시스템 양방향 제어(Home Assistant, Node-RED 자동 액션)

---

## 2. 시스템 아키텍처

### 2.1 전체 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Dashboard │ │Camera Mgr│ │Face Mgr  │ │Alert Mgr │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
│       └─────────────┴────────────┴─────────────┘               │
│              HTTP/REST + WebSocket + SSE                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│                     Backend (FastAPI)                            │
│                                                                  │
│  ┌─────────────────────── Domains ──────────────────────────┐   │
│  │  camera/  │  face/  │  alert/  │  event/  │  auth/       │   │
│  │  stream/  │  agent/ │  notification/  │  setting/        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────── Infrastructure ──────────────────────────┐   │
│  │  LangGraph Agent  │  InsightFace  │  YOLO11  │  VLM     │   │
│  │  Qdrant Client    │  Redis Client │  go2rtc  │  ONVIF   │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────┬──────────┬──────────┬──────────┬─────────────────────┘
           │          │          │          │
     ┌─────┴───┐ ┌───┴───┐ ┌───┴───┐ ┌───┴────┐
     │PostgreSQL│ │Qdrant │ │ Redis │ │ go2rtc │
     └─────────┘ └───────┘ └───────┘ └────────┘
                                          │
                                    ┌─────┴─────┐
                                    │ IP Cameras │
                                    │ (ONVIF/    │
                                    │  RTSP)     │
                                    └───────────┘
```

### 2.2 AI Multi-Agent 아키텍처 (LangGraph)

```
START
  │
  ▼
┌─────────────┐
│   Planner   │  사용자 요청 또는 스케줄 이벤트를 분석하여
│   Agent     │  어떤 카메라의 어떤 분석을 수행할지 결정
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Detector   │  영상 프레임에서 AI 모델 실행
│  Agent      │  - 얼굴 감지/인식 (InsightFace)
│             │  - 위험 상황 감지 (YOLO11 + Custom)
│             │  - 장면 분석 (VLM)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Analyzer   │  감지 결과를 종합 분석
│  Agent      │  - 내부인/외부인 판별
│             │  - 위험도 평가 (severity scoring)
│             │  - 이전 이벤트 컨텍스트 참조
└──────┬──────┘
       │
       ▼ (conditional)
┌─────────────┐
│ Dispatcher  │  분석 결과에 따라 액션 실행
│ Agent       │  - 알림 발송 (WebSocket, Push, Email)
│             │  - 이벤트 저장 (DB)
│             │  - 카메라 PTZ 제어 (자동 추적)
│             │  - 녹화 트리거
└─────────────┘
       │
       ▼
      END
```

**에이전트 상태 (AgentState):**
```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    camera_id: str
    frame_data: bytes | None
    detection_results: list[DetectionResult]
    analysis: AnalysisResult | None
    actions: list[Action]
    severity: float  # 0.0 ~ 1.0
    error: str | None
```

---

## 3. Hexagonal Architecture 상세 설계

### 3.1 도메인별 디렉토리 구조

```
backend/
├── app/
│   ├── domains/
│   │   ├── camera/                      # 카메라 관리 도메인
│   │   │   ├── domain/
│   │   │   │   ├── entity/
│   │   │   │   │   ├── camera.py        # Camera 엔티티
│   │   │   │   │   └── network.py       # Network 엔티티
│   │   │   │   ├── value_object/
│   │   │   │   │   └── camera_status.py # 상태 VO (ONLINE/OFFLINE/ERROR)
│   │   │   │   └── service/
│   │   │   │       └── camera_discovery_service.py
│   │   │   ├── application/
│   │   │   │   ├── usecase/
│   │   │   │   │   ├── discover_cameras_usecase.py
│   │   │   │   │   ├── register_camera_usecase.py
│   │   │   │   │   └── get_cameras_usecase.py
│   │   │   │   ├── port/
│   │   │   │   │   ├── camera_repository_port.py    # 아웃바운드 포트
│   │   │   │   │   └── onvif_discovery_port.py      # 아웃바운드 포트
│   │   │   │   ├── request/
│   │   │   │   │   └── discover_request.py
│   │   │   │   └── response/
│   │   │   │       └── camera_response.py
│   │   │   ├── adapter/
│   │   │   │   ├── inbound/
│   │   │   │   │   └── api/
│   │   │   │   │       └── camera_router.py         # FastAPI 라우터
│   │   │   │   └── outbound/
│   │   │   │       ├── persistence/
│   │   │   │       │   └── camera_repository_impl.py
│   │   │   │       └── onvif/
│   │   │   │           └── onvif_discovery_adapter.py
│   │   │   └── infrastructure/
│   │   │       ├── orm/
│   │   │       │   └── camera_orm.py
│   │   │       └── mapper/
│   │   │           └── camera_mapper.py
│   │   │
│   │   ├── face/                        # 얼굴 인식 도메인
│   │   │   ├── domain/
│   │   │   │   ├── entity/
│   │   │   │   │   ├── identity.py      # 등록된 인물
│   │   │   │   │   └── face.py          # 얼굴 임베딩
│   │   │   │   ├── value_object/
│   │   │   │   │   └── person_type.py   # INTERNAL / EXTERNAL / UNKNOWN
│   │   │   │   └── service/
│   │   │   │       └── face_matching_service.py
│   │   │   ├── application/
│   │   │   │   ├── usecase/
│   │   │   │   │   ├── register_face_usecase.py
│   │   │   │   │   ├── recognize_face_usecase.py
│   │   │   │   │   └── search_similar_faces_usecase.py
│   │   │   │   └── port/
│   │   │   │       ├── face_repository_port.py
│   │   │   │       ├── vector_store_port.py
│   │   │   │       └── face_recognition_port.py
│   │   │   ├── adapter/
│   │   │   │   ├── inbound/api/
│   │   │   │   │   └── face_router.py
│   │   │   │   └── outbound/
│   │   │   │       ├── persistence/
│   │   │   │       │   └── face_repository_impl.py
│   │   │   │       ├── vector/
│   │   │   │       │   └── qdrant_adapter.py
│   │   │   │       └── recognition/
│   │   │   │           └── insightface_adapter.py
│   │   │   └── infrastructure/
│   │   │       ├── orm/
│   │   │       └── mapper/
│   │   │
│   │   ├── alert/                       # 위험 감지/알림 도메인
│   │   │   ├── domain/
│   │   │   │   ├── entity/
│   │   │   │   │   ├── alert.py         # 알림
│   │   │   │   │   └── alert_rule.py    # 알림 규칙
│   │   │   │   ├── value_object/
│   │   │   │   │   ├── danger_type.py   # FIRE / VIOLENCE / FIGHT / INTRUSION
│   │   │   │   │   └── severity.py      # LOW / MEDIUM / HIGH / CRITICAL
│   │   │   │   └── service/
│   │   │   │       └── alert_evaluation_service.py
│   │   │   ├── application/
│   │   │   │   ├── usecase/
│   │   │   │   │   ├── create_alert_usecase.py
│   │   │   │   │   ├── evaluate_danger_usecase.py
│   │   │   │   │   └── get_alerts_usecase.py
│   │   │   │   └── port/
│   │   │   │       ├── alert_repository_port.py
│   │   │   │       ├── danger_detection_port.py
│   │   │   │       └── notification_port.py
│   │   │   ├── adapter/
│   │   │   │   ├── inbound/api/
│   │   │   │   │   └── alert_router.py
│   │   │   │   └── outbound/
│   │   │   │       ├── persistence/
│   │   │   │       │   └── alert_repository_impl.py
│   │   │   │       ├── detection/
│   │   │   │       │   ├── yolo_danger_adapter.py
│   │   │   │       │   └── vlm_scene_adapter.py
│   │   │   │       └── notification/
│   │   │   │           ├── websocket_notification_adapter.py
│   │   │   │           ├── email_notification_adapter.py
│   │   │   │           └── push_notification_adapter.py
│   │   │   └── infrastructure/
│   │   │       ├── orm/
│   │   │       └── mapper/
│   │   │
│   │   ├── stream/                      # 영상 스트리밍 도메인
│   │   │   ├── domain/
│   │   │   │   └── entity/
│   │   │   │       └── stream_session.py
│   │   │   ├── application/
│   │   │   │   ├── usecase/
│   │   │   │   │   ├── start_stream_usecase.py
│   │   │   │   │   ├── capture_frame_usecase.py
│   │   │   │   │   └── manage_recording_usecase.py
│   │   │   │   └── port/
│   │   │   │       ├── stream_provider_port.py
│   │   │   │       └── recording_storage_port.py
│   │   │   └── adapter/
│   │   │       ├── inbound/api/
│   │   │       │   └── stream_router.py
│   │   │       └── outbound/
│   │   │           ├── go2rtc/
│   │   │           │   └── go2rtc_adapter.py
│   │   │           └── rtsp/
│   │   │               └── rtsp_capture_adapter.py
│   │   │
│   │   ├── event/                       # 이벤트/이력 도메인
│   │   │   ├── domain/entity/
│   │   │   │   ├── recognition_event.py
│   │   │   │   ├── danger_event.py
│   │   │   │   └── entry_exit_event.py
│   │   │   ├── application/usecase/
│   │   │   │   ├── log_event_usecase.py
│   │   │   │   └── query_events_usecase.py
│   │   │   └── adapter/
│   │   │       ├── inbound/api/
│   │   │       │   └── event_router.py
│   │   │       └── outbound/persistence/
│   │   │           └── event_repository_impl.py
│   │   │
│   │   ├── agent/                       # AI Multi-Agent 도메인
│   │   │   ├── domain/entity/
│   │   │   │   └── agent_task.py
│   │   │   ├── application/usecase/
│   │   │   │   └── run_agent_pipeline_usecase.py
│   │   │   └── adapter/
│   │   │       ├── inbound/api/
│   │   │       │   └── agent_router.py
│   │   │       └── outbound/
│   │   │           └── langgraph/
│   │   │               └── agent_graph_adapter.py
│   │   │
│   │   ├── auth/                        # 인증/인가 도메인
│   │   │   └── ...
│   │   │
│   │   └── setting/                     # 시스템 설정 도메인
│   │       └── ...
│   │
│   └── infrastructure/
│       ├── config/
│       │   └── settings.py              # Pydantic BaseSettings
│       ├── database/
│       │   ├── session.py               # AsyncSession (asyncpg)
│       │   └── base.py                  # DeclarativeBase
│       ├── cache/
│       │   └── redis_client.py
│       ├── langgraph/                   # Multi-Agent 그래프 정의
│       │   ├── state.py                 # AgentState
│       │   ├── graph_builder.py         # StateGraph 빌드
│       │   ├── runner.py                # 그래프 실행기
│       │   └── nodes/
│       │       ├── planner.py
│       │       ├── detector.py
│       │       ├── analyzer.py
│       │       └── dispatcher.py
│       ├── ai/
│       │   ├── insightface_service.py   # 얼굴 인식 엔진
│       │   ├── yolo_service.py          # 위험 감지 엔진
│       │   └── vlm_service.py           # 장면 분석 엔진
│       ├── onvif/
│       │   └── onvif_client.py          # ONVIF WS-Discovery + PTZ
│       ├── go2rtc/
│       │   └── go2rtc_client.py         # go2rtc REST API 클라이언트 (내장/외부 서버 모두 지원)
│       └── event_bus/
│           └── redis_event_bus.py       # Redis Pub/Sub 이벤트 버스
│
├── alembic/                             # DB 마이그레이션
├── docker/
│   ├── docker-compose.yml
│   ├── docker-compose.dev.yml
│   └── Dockerfile
├── main.py                              # FastAPI 엔트리포인트
├── pyproject.toml
└── .env.example
```

### 3.2 Frontend 디렉토리 구조

```
frontend/
├── app/                                 # Next.js App Router
│   ├── layout.tsx                       # Root Layout (Providers)
│   ├── page.tsx                         # Dashboard
│   ├── cameras/
│   │   ├── page.tsx                     # 카메라 목록/검색
│   │   └── [id]/page.tsx               # 카메라 상세/라이브뷰
│   ├── faces/
│   │   ├── page.tsx                     # 등록 인물 관리
│   │   └── unidentified/page.tsx        # 미식별 얼굴 관리
│   ├── alerts/
│   │   ├── page.tsx                     # 알림 목록
│   │   └── rules/page.tsx              # 알림 규칙 설정
│   ├── events/page.tsx                  # 이벤트 이력
│   ├── live/page.tsx                    # 멀티 카메라 라이브뷰
│   ├── settings/page.tsx                # 시스템 설정
│   └── login/page.tsx                   # 로그인
│
├── features/                            # Feature-based DDD
│   ├── camera/
│   │   ├── domain/
│   │   │   ├── model/                   # Camera, Network 인터페이스
│   │   │   └── state/                   # CameraState (discriminated union)
│   │   ├── application/
│   │   │   ├── atoms/                   # Jotai atoms
│   │   │   └── hooks/                   # useCamera, useCameraDiscovery
│   │   ├── infrastructure/
│   │   │   └── api/                     # cameraApi.ts
│   │   └── ui/
│   │       └── components/              # CameraCard, CameraGrid, DiscoveryDialog
│   │
│   ├── face/
│   │   ├── domain/model/                # Identity, Face 인터페이스
│   │   ├── application/hooks/           # useFaceRegister, useFaceSearch
│   │   ├── infrastructure/api/          # faceApi.ts
│   │   └── ui/components/              # FaceCard, IdentityDialog, FaceCluster
│   │
│   ├── alert/
│   │   ├── domain/
│   │   │   ├── model/                   # Alert, AlertRule 인터페이스
│   │   │   └── state/                   # AlertState
│   │   ├── application/
│   │   │   ├── atoms/                   # alertAtom, unreadCountAtom
│   │   │   └── hooks/                   # useAlerts, useAlertRules
│   │   ├── infrastructure/api/          # alertApi.ts
│   │   └── ui/components/              # AlertBanner, AlertList, AlertRuleForm
│   │
│   ├── stream/
│   │   ├── application/hooks/           # useStream, useWebRTC
│   │   ├── infrastructure/api/          # streamApi.ts
│   │   └── ui/components/              # VideoPlayer, MultiView, StreamOverlay
│   │
│   ├── event/
│   │   ├── application/hooks/           # useEvents, useEventFilter
│   │   ├── infrastructure/api/          # eventApi.ts
│   │   └── ui/components/              # EventTimeline, EventDetail
│   │
│   ├── auth/
│   │   └── ...
│   │
│   └── notification/
│       ├── application/hooks/           # useNotification, useWebSocket
│       └── ui/components/              # NotificationBell, NotificationPanel
│
├── infrastructure/
│   ├── config/env.ts
│   ├── http/httpClient.ts
│   └── ws/wsClient.ts                  # WebSocket 클라이언트
│
├── ui/
│   ├── components/                      # shadcn/ui 기반 공통 컴포넌트
│   └── layout/                          # AppLayout, Sidebar, Navbar
│
├── components/
│   ├── providers/
│   │   ├── AuthProvider.tsx
│   │   ├── JotaiProvider.tsx
│   │   ├── SWRProvider.tsx
│   │   └── NotificationProvider.tsx
│   └── ...
│
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.ts
```

---

## 4. 데이터베이스 스키마

### 4.1 PostgreSQL ERD

```sql
-- 네트워크 (카메라 검색 대상)
CREATE TABLE networks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    subnet VARCHAR(50) NOT NULL,           -- e.g. "192.168.1.0/24"
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- IP 카메라
CREATE TABLE cameras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    network_id UUID REFERENCES networks(id),
    name VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    mac_address VARCHAR(17),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    firmware_version VARCHAR(50),
    onvif_xaddr VARCHAR(255),              -- ONVIF 서비스 주소
    rtsp_url VARCHAR(500),                 -- 메인 RTSP 스트림 URL
    rtsp_sub_url VARCHAR(500),             -- 서브 스트림 URL (분석용)
    username VARCHAR(100),
    password_encrypted VARCHAR(255),        -- AES 암호화 저장
    profiles JSONB,                         -- ONVIF 프로파일 목록
    ptz_supported BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'OFFLINE',   -- ONLINE / OFFLINE / ERROR
    location VARCHAR(200),                  -- 설치 위치 설명
    zone VARCHAR(50),                       -- 구역 (entrance, hallway, office 등)
    last_seen_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(ip_address)
);
CREATE INDEX idx_cameras_network ON cameras(network_id);
CREATE INDEX idx_cameras_status ON cameras(status);
CREATE INDEX idx_cameras_zone ON cameras(zone);

-- 등록된 인물 (내부인)
CREATE TABLE identities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    employee_id VARCHAR(50) UNIQUE,
    department VARCHAR(100),
    person_type VARCHAR(20) DEFAULT 'INTERNAL',  -- INTERNAL / VIP / BLACKLIST
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_identities_name ON identities(name);
CREATE INDEX idx_identities_type ON identities(person_type);

-- 얼굴 데이터 (임베딩 참조)
CREATE TABLE faces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identity_id UUID REFERENCES identities(id) ON DELETE CASCADE,
    vector_id VARCHAR(100) UNIQUE NOT NULL,     -- Qdrant 벡터 ID
    image_path VARCHAR(500),
    thumbnail BYTEA,
    quality_score FLOAT,
    is_primary BOOLEAN DEFAULT false,
    cluster_id VARCHAR(100),                     -- 미식별 얼굴 클러스터링용
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_faces_identity ON faces(identity_id);
CREATE INDEX idx_faces_cluster ON faces(cluster_id);

-- 인식 이벤트
CREATE TABLE recognition_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    camera_id UUID REFERENCES cameras(id),
    identity_id UUID REFERENCES identities(id),  -- NULL이면 미식별
    face_id UUID REFERENCES faces(id),
    confidence FLOAT NOT NULL,
    person_type VARCHAR(20),                      -- 인식 시점 인물 유형
    bbox FLOAT[] NOT NULL,                        -- [x, y, w, h]
    snapshot_path VARCHAR(500),
    timestamp TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_recog_camera ON recognition_events(camera_id);
CREATE INDEX idx_recog_identity ON recognition_events(identity_id);
CREATE INDEX idx_recog_timestamp ON recognition_events(timestamp);

-- 위험 감지 이벤트
CREATE TABLE danger_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    camera_id UUID REFERENCES cameras(id),
    danger_type VARCHAR(30) NOT NULL,             -- FIRE / VIOLENCE / FIGHT / INTRUSION / FALL / WEAPON
    severity VARCHAR(10) NOT NULL,                -- LOW / MEDIUM / HIGH / CRITICAL
    confidence FLOAT NOT NULL,
    description TEXT,                              -- AI 장면 분석 결과
    bbox FLOAT[],
    snapshot_path VARCHAR(500),
    video_clip_path VARCHAR(500),                 -- 전후 영상 클립
    is_acknowledged BOOLEAN DEFAULT false,
    acknowledged_by UUID,
    acknowledged_at TIMESTAMPTZ,
    timestamp TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_danger_camera ON danger_events(camera_id);
CREATE INDEX idx_danger_type ON danger_events(danger_type);
CREATE INDEX idx_danger_severity ON danger_events(severity);
CREATE INDEX idx_danger_timestamp ON danger_events(timestamp);
CREATE INDEX idx_danger_unacked ON danger_events(is_acknowledged) WHERE NOT is_acknowledged;

-- 알림
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(30) NOT NULL,              -- RECOGNITION / DANGER / CAMERA_OFFLINE
    event_id UUID,                                -- recognition_events.id 또는 danger_events.id
    title VARCHAR(200) NOT NULL,
    message TEXT,
    severity VARCHAR(10) NOT NULL,
    channel VARCHAR(20) NOT NULL,                 -- WEBSOCKET / EMAIL / PUSH
    recipient_id UUID,
    is_read BOOLEAN DEFAULT false,
    sent_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_alerts_recipient ON alerts(recipient_id);
CREATE INDEX idx_alerts_unread ON alerts(is_read) WHERE NOT is_read;
CREATE INDEX idx_alerts_sent ON alerts(sent_at);

-- 알림 규칙
CREATE TABLE alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    event_type VARCHAR(30) NOT NULL,
    condition JSONB NOT NULL,                     -- {"danger_type": "FIRE", "min_severity": "HIGH"}
    channels VARCHAR(20)[] NOT NULL,              -- ["WEBSOCKET", "EMAIL"]
    recipients UUID[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 출입 이벤트
CREATE TABLE entry_exit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    camera_id UUID REFERENCES cameras(id),
    identity_id UUID REFERENCES identities(id),
    event_type VARCHAR(20) NOT NULL,              -- ENTRY / EXIT
    direction VARCHAR(10),                        -- 진입 방향
    face_recognized BOOLEAN DEFAULT false,
    person_type VARCHAR(20),
    snapshot_path VARCHAR(500),
    timestamp TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_entry_exit_camera ON entry_exit_events(camera_id);
CREATE INDEX idx_entry_exit_timestamp ON entry_exit_events(timestamp);

-- 사용자 (관리자)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'OPERATOR',          -- ADMIN / OPERATOR / VIEWER
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### 4.2 Qdrant Collection

```python
# Collection: face_embeddings
{
    "name": "face_embeddings",
    "vectors": {
        "size": 512,         # ArcFace 임베딩 차원
        "distance": "Cosine"
    },
    "hnsw_config": {
        "m": 16,
        "ef_construct": 100
    },
    "payload_schema": {
        "identity_id": "keyword",
        "cluster_id": "keyword",
        "person_type": "keyword",
        "created_at": "datetime"
    }
}
```

---

## 5. API 설계

### 5.1 REST API 엔드포인트

```
# 인증
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me

# 카메라 관리
POST   /api/v1/cameras/discover             # ONVIF 디스커버리 실행
GET    /api/v1/cameras                       # 카메라 목록 (필터, 페이지네이션)
POST   /api/v1/cameras                       # 카메라 수동 등록
GET    /api/v1/cameras/{id}                  # 카메라 상세
PATCH  /api/v1/cameras/{id}                  # 카메라 수정
DELETE /api/v1/cameras/{id}                  # 카메라 삭제
GET    /api/v1/cameras/{id}/status           # 카메라 연결 상태
POST   /api/v1/cameras/{id}/ptz             # PTZ 제어

# 영상 스트리밍
GET    /api/v1/streams/{camera_id}/webrtc    # WebRTC SDP 교환
GET    /api/v1/streams/{camera_id}/snapshot  # 현재 프레임 스냅샷
GET    /api/v1/streams/{camera_id}/mjpeg     # MJPEG 폴백 스트림

# 얼굴/인물 관리
POST   /api/v1/identities                   # 인물 등록
GET    /api/v1/identities                    # 인물 목록
GET    /api/v1/identities/{id}               # 인물 상세
PATCH  /api/v1/identities/{id}               # 인물 수정
DELETE /api/v1/identities/{id}               # 인물 삭제
POST   /api/v1/faces/register               # 얼굴 등록 (이미지 업로드)
POST   /api/v1/faces/search                 # 얼굴 유사도 검색
GET    /api/v1/faces/unidentified            # 미식별 얼굴 클러스터
POST   /api/v1/faces/{cluster_id}/assign     # 클러스터 → 인물 할당

# 위험 감지/알림
GET    /api/v1/alerts                        # 알림 목록
PATCH  /api/v1/alerts/{id}/read              # 알림 읽음 처리
GET    /api/v1/alerts/rules                  # 알림 규칙 목록
POST   /api/v1/alerts/rules                  # 알림 규칙 생성
PATCH  /api/v1/alerts/rules/{id}             # 알림 규칙 수정
DELETE /api/v1/alerts/rules/{id}             # 알림 규칙 삭제
GET    /api/v1/danger-events                 # 위험 이벤트 이력
POST   /api/v1/danger-events/{id}/ack        # 위험 이벤트 확인 처리

# 이벤트 이력
GET    /api/v1/events/recognition            # 인식 이벤트 이력
GET    /api/v1/events/entry-exit             # 출입 이벤트 이력
GET    /api/v1/events/timeline               # 통합 타임라인
GET    /api/v1/events/stats                  # 통계 (대시보드용)

# AI 에이전트
POST   /api/v1/agent/analyze                 # 수동 분석 요청
GET    /api/v1/agent/status                  # 에이전트 상태

# 시스템 설정
GET    /api/v1/settings                      # 설정 조회
PATCH  /api/v1/settings                      # 설정 변경
```

### 5.2 WebSocket 이벤트

```
# 실시간 이벤트 스트림
WS /api/v1/ws/events

# 이벤트 타입:
{
    "type": "recognition",           # 얼굴 인식
    "data": {
        "camera_id": "...",
        "identity": { "name": "...", "person_type": "INTERNAL" },
        "confidence": 0.95,
        "timestamp": "..."
    }
}

{
    "type": "danger",                # 위험 감지
    "data": {
        "camera_id": "...",
        "danger_type": "FIRE",
        "severity": "CRITICAL",
        "confidence": 0.92,
        "description": "1층 로비에서 화염 감지",
        "snapshot_url": "/api/v1/snapshots/...",
        "timestamp": "..."
    }
}

{
    "type": "camera_status",         # 카메라 상태 변경
    "data": {
        "camera_id": "...",
        "status": "OFFLINE",
        "timestamp": "..."
    }
}

{
    "type": "entry_exit",            # 출입 이벤트
    "data": {
        "camera_id": "...",
        "event_type": "ENTRY",
        "identity": { "name": "...", "person_type": "INTERNAL" },
        "timestamp": "..."
    }
}
```

---

## 6. AI/ML 파이프라인 상세

### 6.1 영상 처리 파이프라인

```
RTSP 프레임 수집 (OpenCV, 서브스트림 사용)
     │
     ▼
[Stage 1] Motion Detection (MOG2 배경 차분) ← CPU 경량 처리
     │ 움직임 감지됨?
     │ No → 대기 (IDLE 간격, 0.2초)
     │ Yes ↓
     ▼
[Stage 2] 움직임 영역(ROI) 크롭 → AI 추론 큐에 전달
     │
     ▼ (GPU/NPU에서 병렬 처리)
┌──────────────────────────────────────────────────────────────┐
│                       병렬 AI 파이프라인                      │
│                                                              │
│  ┌─ 얼굴 파이프라인 ──────┐  ┌─ 위험 감지 파이프라인 ────┐  │
│  │                         │  │                            │  │
│  │ SCRFD 얼굴 감지         │  │ YOLO11 객체 탐지           │  │
│  │   ↓                     │  │ (화재/연기/무기)           │  │
│  │ 품질 평가               │  │   ↓                        │  │
│  │ (선명도, 크기, 각도)    │  │ Pose Estimation            │  │
│  │   ↓                     │  │ (MediaPipe/MMPose)         │  │
│  │ ArcFace 임베딩 (512d)   │  │   ↓                        │  │
│  │ (저화질: AdaFace 전환)  │  │ 행동 분류 LSTM             │  │
│  │   ↓                     │  │ (폭력/싸움/쓰러짐)        │  │
│  │ Qdrant 유사도 검색      │  │   ↓                        │  │
│  │   ↓                     │  │ severity ≥ HIGH 시         │  │
│  │ 인물 식별 결과          │  │ VLM 장면 분석 (확인용)     │  │
│  │   ↓                     │  │   ↓                        │  │
│  │ 인식 이벤트 생성        │  │ 위험 이벤트 생성           │  │
│  └─────────────────────────┘  └────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
     │
     ▼
Redis Pub/Sub + MQTT → WebSocket Manager → Frontend 실시간 업데이트
                     → Alert Rule Engine → Notification Dispatcher
                     → Event Repository (DB 저장)
```

> **설계 근거 (Frigate NVR 패턴 참조):**
> CPU 기반 모션 감지를 1차 필터로 사용하여, AI 추론은 움직임이 감지된 ROI에서만 실행한다.
> 이 2단계 파이프라인은 GPU 부하를 80%+ 절감하며, 동시 처리 가능한 카메라 수를 극대화한다.
> VLM은 비용이 높으므로 severity ≥ HIGH인 이벤트에 대해서만 확인 용도로 호출한다.

### 6.2 위험 감지 모델

| 위험 유형 | 감지 방법 | 모델 | 참고 오픈소스 |
|-----------|----------|------|--------------|
| **화재/연기** | 객체 감지 | YOLO11 Custom (fire-smoke dataset) | fire-detection-cnn, FireNET |
| **폭력/싸움** | 포즈 추정 → 시퀀스 분류 | MediaPipe Pose + LSTM | imsoo/fight_detection (227★) |
| **침입** | 금지 구역 진입 | 얼굴 미등록 + Zone 규칙 | Frigate zone-based detection |
| **쓰러짐** | 다중 인물 포즈 추정 | AlphaPose/MediaPipe + 규칙/ML | HumanFallDetection (336★) |
| **무기** | 객체 감지 | YOLO11 Custom (weapon dataset) | Weapons-and-Knives-Detector |
| **이상 행동** | 약지도 학습 이상 감지 | CLIP + MIL (PE-MIL, CVPR 2024) | PE-MIL — 범주 미정의 이상 감지 |
| **복합 판단** | 장면 종합 분석 (확인용) | Qwen2.5-VL-7B / StreamingVLM | StreamingVLM (MIT, 962★) |

#### 얼굴 인식 모델 선택 기준

| 모델 | 용도 | LFW 정확도 | 저화질 성능 | 비고 |
|------|------|-----------|------------|------|
| **InsightFace (SCRFD + ArcFace)** | 기본 인식 엔진 | 99.83% | Good | 프로덕션 표준, ONNX 지원 |
| **AdaFace** | 저화질 카메라 보조 | 99.4% | Best (75%+ TinyFace) | 품질 적응형 마진 (CVPR 2022) |
| **DeepFace** | 프로토타이핑/비교 | 모델별 상이 | 모델별 상이 | 멀티 백엔드 래퍼 |

> **전략:** 기본 엔진은 InsightFace (SCRFD 감지 + ArcFace 임베딩). 프레임 품질 점수가 임계값 이하일 때
> 자동으로 AdaFace로 폴백하여 저화질 환경에서의 인식률을 보완한다.

#### 행동 인식 파이프라인 (폭력/싸움/쓰러짐)

```
프레임 입력
  ↓
Pose Estimation (MediaPipe Pose / MMPose)
  → 키포인트 17~33개 추출 (관절 좌표 + confidence)
  ↓
시퀀스 버퍼 (sliding window, 30~60 프레임)
  ↓
행동 분류 LSTM
  → 입력: 키포인트 시퀀스 (T × J × 3)
  → 출력: {normal, violence, fight, fall} + confidence
  ↓
severity 임계값 판정 → 이벤트 생성
```

> **설계 근거:** YOLO 단독으로는 "사람이 있다"는 감지 가능하지만 "싸우고 있다"는 판별 불가.
> 포즈 추정 → 시간축 분류(LSTM)의 2단계 접근이 행동 인식의 업계 표준 패턴이다.

### 6.3 위험도 평가 (Severity Scoring)

```python
# 위험도 결정 로직
severity_matrix = {
    ("FIRE", confidence >= 0.8):     "CRITICAL",
    ("FIRE", confidence >= 0.5):     "HIGH",
    ("WEAPON", confidence >= 0.7):   "CRITICAL",
    ("VIOLENCE", confidence >= 0.8): "HIGH",
    ("VIOLENCE", confidence >= 0.5): "MEDIUM",
    ("FIGHT", confidence >= 0.7):    "HIGH",
    ("FIGHT", confidence >= 0.5):    "MEDIUM",
    ("INTRUSION", confidence >= 0.6):"HIGH",
    ("FALL", confidence >= 0.7):     "MEDIUM",
}

# CRITICAL → 즉시 알림 (WebSocket + Push + Email + 사이렌)
# HIGH     → 즉시 알림 (WebSocket + Push)
# MEDIUM   → 대기열 알림 (WebSocket)
# LOW      → 로그만 기록
```

### 6.4 얼굴 인식 성능 보강 전략

> **배경:** face-pass.cc 프로젝트에서 InsightFace 기반 얼굴 인식을 구현했으나, 실시간 RTSP 스트림 환경에서
> 인식 속도와 정확도 모두 프로덕션 수준에 미달하였다. 아래 전략으로 성능을 보강한다.

#### A. 추론 속도 최적화

| 단계 | 방법 | 예상 효과 |
|------|------|----------|
| **1. 모델 변환** | ONNX → TensorRT FP16 변환 | 추론 속도 2~4배 향상 |
| **2. 감지기 교체** | RetinaFace → **SCRFD-2.5GF** | 감지 속도 3배 향상 (정확도 유지) |
| **3. 동적 배치** | 다중 카메라 프레임을 모아 배치 추론 | GPU 활용률 극대화 |
| **4. 프레임 전략** | 서브스트림(CIF/D1) 사용 + 적응형 프레임 스킵 | 입력 해상도 75% 감소 |
| **5. ROI 크롭** | 모션 감지 영역만 AI에 전달 (Frigate 패턴) | 처리량 80%+ 절감 |
| **6. 추적 연계** | 인식 후 트래커(SORT/DeepSORT)로 추적, 매 프레임 재인식 방지 | 인식 호출 90% 감소 |

```python
# 적응형 프레임 스킵 예시
# 움직임 활발 → 매 3프레임마다 인식 (빠른 반응)
# 움직임 적음 → 매 15프레임마다 인식 (GPU 절약)
# 움직임 없음 → 인식 중단 (모션 감지만 동작)

if motion_level == "HIGH":
    frame_skip = 3
elif motion_level == "LOW":
    frame_skip = 15
else:
    frame_skip = None  # skip recognition entirely
```

#### B. 인식 정확도 향상

| 단계 | 방법 | 상세 |
|------|------|------|
| **1. 품질 필터링** | 품질 점수 임계값 이하 프레임은 인식 스킵 | Laplacian 분산(선명도) + 얼굴 크기 + 감지 confidence |
| **2. 다중 프레임 앙상블** | 동일 트래킹 ID의 최근 N개 임베딩 평균 | 단일 프레임 노이즈 제거, 정확도 2~5% 향상 |
| **3. AdaFace 폴백** | 품질 점수 < 임계값 시 AdaFace로 자동 전환 | 저화질(야간, 역광, 원거리)에서 인식률 대폭 개선 |
| **4. 갤러리 품질 관리** | 등록 시 다각도/다조건 얼굴 5장 이상 권장 | 갤러리 다양성이 인식률에 직결 |
| **5. 임계값 이중화** | 높은 임계값(0.75) → 즉시 확정, 중간(0.55~0.75) → VLM 확인 | 오탐 감소 + 미탐 보완 |

```python
# 이중 임계값 판정
if similarity >= HIGH_THRESHOLD:      # 0.75
    result = MatchResult.CONFIRMED
elif similarity >= LOW_THRESHOLD:     # 0.55
    result = MatchResult.NEEDS_VLM_VERIFICATION
    # VLM에 "이 두 얼굴이 같은 사람인가?" 질의
else:
    result = MatchResult.UNKNOWN
```

#### C. Qdrant 벡터 검색 최적화

| 설정 | 기본값 | 최적화 값 | 효과 |
|------|--------|----------|------|
| **HNSW ef_construct** | 100 | 200 | 인덱스 품질 향상 (빌드 시간 증가) |
| **HNSW ef (검색 시)** | 128 | 256 | 검색 정확도 향상 |
| **양자화** | 없음 | Scalar Quantization (INT8) | 메모리 75% 절감, 속도 향상 |
| **페이로드 인덱스** | identity_id | + person_type, is_active | 필터 검색 속도 향상 |
| **샤딩** | 1 | 등록 인원 10,000명 초과 시 2+ | 병렬 검색 |

#### D. 파이프라인 아키텍처 (face-pass.cc 대비 개선)

```
face-pass.cc (기존)                    ai-vms (개선)
─────────────────                      ─────────────────
매 프레임 풀 해상도 처리               서브스트림 + 모션 기반 ROI
RetinaFace (무거움)                    SCRFD-2.5GF (3배 빠름)
ONNX CPU/CUDA                         TensorRT FP16 (2~4배 빠름)
매 프레임 Qdrant 검색                  트래커 연계, 신규 ID만 검색
단일 임계값 판정                       이중 임계값 + VLM 확인
ArcFace만 사용                         ArcFace + AdaFace 자동 전환
프레임 스킵 고정 (5)                   적응형 프레임 스킵 (3~15)
```

---

## 7. 핵심 구현 패턴

### 7.1 Hexagonal Architecture 의존성 규칙

```
Domain (Entity, VO, Domain Service)
    ↑ 의존성 없음 (순수 Python)
    │
Application (UseCase, Port 인터페이스, Request/Response DTO)
    ↑ Domain만 의존
    │
Adapter (Router, Repository Impl, External Service Impl)
    ↑ Application의 Port를 구현
    │
Infrastructure (ORM, Config, 3rd Party Client)
    ↑ 기술 구현 상세
```

**규칙:**
- Domain 레이어는 외부 라이브러리 import 금지 (dataclass만 사용)
- UseCase는 Port 인터페이스를 통해서만 외부 접근
- Adapter는 Port를 implements하며, FastAPI DI로 주입
- ORM 모델과 Domain Entity는 반드시 분리 (Mapper로 변환)

### 7.2 실시간 이벤트 흐름

```
[AI Worker] ──→ Redis Pub/Sub ──→ [Event Handler] ──→ WebSocket Manager → [Frontend]
      │                                  │
      └──→ MQTT Broker ──→ 외부 시스템    ├→ Alert Rule Engine → Notification Dispatcher
           (Home Assistant,              │                          ├→ WebSocket
            NVR 연동 등)                 │                          ├→ Push Notification
                                         │                          ├→ Email
                                         │                          └→ MQTT (IoT 연동)
                                         └→ Event Repository (DB 저장)
```

> **이중 이벤트 버스 설계:**
> - **Redis Pub/Sub**: 내부 마이크로서비스 간 저지연 통신 (< 1ms)
> - **MQTT**: 외부 시스템 연동 표준 (Home Assistant, 다른 NVR, IoT 디바이스).
>   Frigate NVR 등 업계 주요 프로젝트가 MQTT를 이벤트 배포 표준으로 채택하고 있음.

### 7.3 카메라 검색 흐름

```
1. 사용자가 네트워크 대역 지정 (e.g., 192.168.1.0/24)
2. ONVIF WS-Discovery 프로브 전송 (멀티캐스트)
   - 4회 재시도, 인터페이스별 병렬 스캔
   - 2~5초 타임아웃 per probe
3. ProbeMatch 응답에서 디바이스 정보 추출
   - XAddr, IP, 모델, 프로파일
4. 각 디바이스에 GetCapabilities 호출
   - 미디어 프로파일, PTZ 지원 여부
5. GetStreamUri로 RTSP URL 획득
6. DB 저장 (신규/업데이트 구분)
7. go2rtc에 스트림 등록
8. 프론트엔드에 결과 반환 (WebSocket 진행 상황 포함)
```

---

## 8. Docker Compose 구성

```yaml
# docker-compose.yml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://aivms:aivms@postgres:5432/aivms
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
      - GO2RTC_URL=http://go2rtc:1984
      - MQTT_BROKER_URL=mqtt://mosquitto:1883
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data/snapshots:/app/data/snapshots
      - ./data/recordings:/app/data/recordings
    depends_on:
      - postgres
      - redis
      - qdrant
      - mosquitto
      - go2rtc
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: aivms
      POSTGRES_USER: aivms
      POSTGRES_PASSWORD: aivms
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

  mosquitto:
    image: eclipse-mosquitto:2
    ports:
      - "1883:1883"    # MQTT
      - "9001:9001"    # WebSocket (MQTT over WS)
    volumes:
      - ./config/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - mosquitto_data:/mosquitto/data

  # go2rtc는 내장(Docker) 또는 외부 서버 중 선택 가능
  # 외부 go2rtc 서버를 사용할 경우:
  #   1. 이 서비스 블록을 주석 처리
  #   2. backend 환경변수에서 GO2RTC_URL을 외부 서버 주소로 변경
  #   3. backend의 depends_on에서 go2rtc 제거
  #   4. 프론트엔드의 GO2RTC_DIRECT_URL을 외부 서버 주소로 변경
  go2rtc:
    image: alexxit/go2rtc
    ports:
      - "1984:1984"     # API
      - "8555:8555/tcp"  # WebRTC TCP
      - "8555:8555/udp"  # WebRTC UDP
    volumes:
      - ./config/go2rtc.yaml:/config/go2rtc.yaml

volumes:
  pgdata:
  qdrant_data:
  mosquitto_data:
```

### 8.1 go2rtc 배포 모드

go2rtc는 두 가지 모드로 운영할 수 있다. `GO2RTC_MODE` 환경변수로 전환하며, 백엔드의 go2rtc 클라이언트는 어느 모드든 동일한 REST API로 통신한다.

#### 모드 A: 내장 (기본값)
Docker Compose에 go2rtc 서비스를 포함하여 로컬에서 실행한다.
```env
GO2RTC_MODE=embedded
GO2RTC_URL=http://go2rtc:1984          # 백엔드 → go2rtc (Docker 내부 통신)
GO2RTC_DIRECT_URL=http://localhost:1984 # 프론트엔드 → go2rtc (WebRTC SDP 교환)
```

#### 모드 B: 외부 서버 연동
이미 운영 중인 외부 go2rtc 서버가 있는 경우, 설정만 변경하여 연동한다.
```env
GO2RTC_MODE=external
GO2RTC_URL=http://192.168.1.100:1984          # 외부 go2rtc API 주소
GO2RTC_DIRECT_URL=http://192.168.1.100:1984   # 프론트엔드에서 접근 가능한 주소
```

변경 사항:
1. `docker-compose.yml`에서 go2rtc 서비스 블록 주석 처리
2. `backend.depends_on`에서 go2rtc 제거
3. 위 환경변수를 외부 서버 주소로 설정

#### go2rtc 클라이언트 설계 원칙
```python
# go2rtc_client.py는 모드에 무관하게 동일한 인터페이스를 제공한다.
# GO2RTC_URL만 바꾸면 내장/외부 모두 동작한다.

class Go2RtcClient:
    async def add_stream(self, name: str, rtsp_url: str) -> None: ...
    async def remove_stream(self, name: str) -> None: ...
    async def get_streams(self) -> list[StreamInfo]: ...
    async def get_webrtc_offer(self, name: str) -> str: ...
    async def health_check(self) -> bool: ...
```

| 항목 | 내장 모드 | 외부 모드 |
|------|----------|----------|
| Docker Compose | go2rtc 서비스 포함 | go2rtc 서비스 제거 |
| GO2RTC_URL | `http://go2rtc:1984` | `http://<외부IP>:1984` |
| GO2RTC_DIRECT_URL | `http://localhost:1984` | `http://<외부IP>:1984` |
| 스트림 등록 | 백엔드가 자동 등록 | 백엔드가 자동 등록 (동일) |
| WebRTC 재생 | 프론트엔드 → localhost | 프론트엔드 → 외부 서버 |

---

## 9. 개발 단계별 구현 계획

### Phase 1: 기반 구축 (2주)
- [ ] 프로젝트 초기 세팅 (Backend FastAPI + Frontend Next.js)
- [ ] Hexagonal Architecture 스켈레톤 (camera, auth 도메인)
- [ ] PostgreSQL + Alembic 마이그레이션 설정
- [ ] Docker Compose 개발 환경 구성
- [ ] JWT 인증 구현
- [ ] 기본 UI 레이아웃 (Sidebar, Dashboard shell)

### Phase 2: 카메라 관리 (2주)
- [ ] ONVIF WS-Discovery 구현 (카메라 검색)
- [ ] 카메라 CRUD API + 프론트엔드
- [ ] go2rtc 연동 (RTSP→WebRTC 스트리밍)
- [ ] 라이브뷰 UI (싱글/멀티)
- [ ] PTZ 제어 (선택)
- [ ] 카메라 상태 모니터링

### Phase 3: 얼굴 인식 (2주)
- [ ] InsightFace 엔진 통합 (ArcFace 512d)
- [ ] Qdrant 벡터 스토어 연동
- [ ] 인물 등록/관리 UI
- [ ] 실시간 얼굴 인식 파이프라인 (RTSP 프레임 처리)
- [ ] 내부인/외부인 구별 로직
- [ ] 미식별 얼굴 클러스터링 (DBSCAN)
- [ ] 인식 이벤트 기록 + WebSocket 실시간 알림

### Phase 4: 위험 감지 (2주)
- [ ] YOLO11 위험 감지 모델 통합 (화재, 폭력, 무기)
- [ ] VLM 장면 분석 서비스 (LLaVA / Qwen2.5-VL)
- [ ] 위험도 평가 엔진 (severity scoring)
- [ ] 위험 이벤트 기록 + 스냅샷/클립 저장
- [ ] 알림 규칙 엔진
- [ ] 알림 발송 (WebSocket + Push + Email)
- [ ] 알림 관리 UI

### Phase 5: AI Multi-Agent (1주)
- [ ] LangGraph 에이전트 그래프 구축 (Planner→Detector→Analyzer→Dispatcher)
- [ ] 에이전트 상태 관리 (AgentState)
- [ ] 스케줄 기반 자동 분석 (APScheduler)
- [ ] 에이전트 SSE 스트리밍 (분석 진행 상황)

### Phase 6: 대시보드 및 마무리 (1주)
- [ ] 대시보드 (실시간 통계, 카메라 현황, 최근 이벤트)
- [ ] 이벤트 타임라인 (통합 이력)
- [ ] 시스템 설정 UI
- [ ] 성능 최적화 (모션 게이팅, 프레임 스킵)
- [ ] 에러 핸들링 + 로깅 정리

### Phase 공통 완료 기준 (Definition of Done)
- [ ] API/이벤트 스펙이 문서와 코드에 모두 반영됨
- [ ] Docker Compose 기준으로 로컬 재현 가능
- [ ] 정상 흐름과 대표 실패 흐름(인증 실패, 카메라 오프라인, 모델 미응답)을 확인함
- [ ] 구조 로그, 핵심 메트릭, 에러 메시지가 운영자가 해석 가능한 수준으로 남음
- [ ] 사용자/운영자 관점의 수동 검증 시나리오를 최소 1회 수행함
- [ ] 개인정보/민감정보가 로그, 응답, 프론트엔드 스토리지에 과도하게 노출되지 않음

---

## 10. 환경 변수 (.env.example)

```env
# Database
DATABASE_URL=postgresql+asyncpg://aivms:aivms@localhost:5432/aivms

# Redis
REDIS_URL=redis://localhost:6379

# Qdrant
QDRANT_URL=http://localhost:6333

# Security
SECRET_KEY=your-secret-key-min-32-chars-here
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=http://localhost:3000

# AI Models
RECOGNITION_THRESHOLD=0.68
FACE_QUALITY_THRESHOLD=0.4
EMBEDDING_DIMENSION=512
CUDA_VISIBLE_DEVICES=0
USE_ADAFACE_FALLBACK=true

# MQTT (외부 시스템 연동)
MQTT_BROKER_URL=mqtt://localhost:1883
MQTT_TOPIC_PREFIX=ai-vms

# LLM (for VLM + Multi-Agent; AI 코딩 도구 편집 모델과는 별도 런타임 설정)
OPENAI_API_KEY=
LANGGRAPH_MODEL=gpt-4.1-mini
LLM_PROVIDER=openai

# VLM
USE_VLM=true
VLM_MODEL=Qwen/Qwen2.5-VL-7B-Instruct

# go2rtc (embedded: 내장 Docker / external: 외부 서버 연동)
GO2RTC_MODE=embedded
GO2RTC_URL=http://localhost:1984
GO2RTC_DIRECT_URL=http://localhost:1984

# Motion Detection
MOTION_GATE_ENABLED=true
PROCESS_INTERVAL_ACTIVE=0.01
PROCESS_INTERVAL_IDLE=0.2
FRAME_SKIP=3

# Danger Detection
DANGER_DETECTION_ENABLED=true
DANGER_MODEL_PATH=./models/yolo11-danger.pt
ACTION_RECOGNITION_ENABLED=true
POSE_MODEL=mediapipe

# Notification
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
PUSH_VAPID_KEY=

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## 11. 비기능 요구사항

### 성능
- 카메라당 프레임 처리: 최소 5 FPS (서브스트림 기준)
- 얼굴 인식 지연: < 200ms per face (GPU)
- 위험 감지 지연: < 500ms per frame (GPU)
- 동시 카메라 스트림: 최소 16채널
- WebSocket 이벤트 전달: < 100ms

### 보안
- JWT 토큰 기반 인증 (httpOnly cookie)
- 카메라 패스워드 AES 암호화 저장
- CORS 화이트리스트
- RTSP URL 로그 마스킹 (크레덴셜 제거)
- Role-based 접근 제어 (ADMIN / OPERATOR / VIEWER)

### 안정성
- RTSP 연결 자동 재접속 (2초 간격)
- 카메라 오프라인 감지 + 알림
- AI 모델 lazy loading (메모리 절약)
- 그레이스풀 셧다운 (영상 처리 워커 안전 종료)

### 운영/관측성
- 구조 로그(JSON) 기반으로 `camera_id`, `event_id`, `trace_id`, `agent_node`를 공통 필드로 남긴다
- Prometheus 또는 동등 수준의 메트릭으로 카메라별 FPS, 추론 지연, 큐 적체, 알림 성공률을 수집한다
- `/health/live`, `/health/ready` 및 외부 의존성(PostgreSQL, Redis, Qdrant, go2rtc) 헬스체크를 분리한다
- 장애 재현을 위해 최근 N분의 이벤트 흐름과 워커 에러를 상관관계 있게 조회할 수 있어야 한다

### 개인정보/감사
- 얼굴 이미지, 스냅샷, 임베딩은 모두 민감정보로 취급하고 접근 권한을 역할 기반으로 제한한다
- 인물 삭제 시 PostgreSQL, Qdrant, 스냅샷/썸네일 파일이 함께 정리되도록 삭제 정책을 일관되게 유지한다
- 얼굴 조회/등록/수정/삭제와 위험 이벤트 열람은 감사 로그에 남긴다
- 보존 기간(`snapshot retention`, `clip retention`, `audit retention`)은 환경변수 또는 설정 UI에서 관리 가능해야 한다

---

## 12. 참고 소스 매핑 (내부)

| 기능 | 참고 소스 | 활용 포인트 |
|------|----------|------------|
| 얼굴 인식 파이프라인 | face-pass.cc | InsightFace, Qdrant, 스트림 처리, 클러스터링 (성능 보강 필요 → §6.4 참조) |
| ONVIF 카메라 검색 | onvif-standalone | WS-Discovery, RTSP URI 추출, PTZ, go2rtc 연동 |
| **UI 디자인/레이아웃** | **onvif-standalone (workspace-ui)** | **Vue 3 + Element Plus + Naive UI 기반 UI 패턴 참고 (§12.1 참조)** |
| Hexagonal Architecture | alpha-terminal-ai-server | 도메인 분리, Port/Adapter, UseCase 패턴 |
| AI Multi-Agent | alpha-terminal-ai-server | LangGraph, StateGraph, 노드별 에이전트 |
| Frontend DDD | alpha-terminal-frontend | Feature-based 구조, Jotai, 상태 머신 패턴 |
| 영상 스트리밍 | onvif-standalone | go2rtc WebRTC, 프록시 설정 |
| 실시간 이벤트 | face-pass.cc | WebSocket, Redis Pub/Sub, 이벤트 구조 |

### 12.1 UI 참고: onvif-standalone (workspace-ui)

AI-VMS의 프론트엔드 UI는 onvif-standalone 프로젝트의 workspace-ui를 참고한다.

**onvif-standalone workspace-ui 기술 스택:**
- Vue 3 + Vite + TypeScript
- Element Plus + Naive UI (UI 컴포넌트)
- Pinia (상태 관리)
- Vue Router + vite-plugin-pages (파일 기반 라우팅)
- vue-i18n (다국어)
- vue3-apexcharts (차트/통계)
- go2rtc WebRTC 플레이어 (영상 재생)

**참고할 UI 패턴 및 페이지:**

| onvif-standalone 페이지 | AI-VMS 대응 | 참고 포인트 |
|------------------------|------------|------------|
| ONVIF Manager (discover-onvif.vue) | 카메라 검색/등록 | 디스커버리 다이얼로그, 진행 상태 표시, 결과 테이블 |
| Device List | 카메라 목록 | 카드/테이블 뷰 전환, 상태 뱃지(ONLINE/OFFLINE), 필터 |
| Stream Player (go2rtc WebRTC) | 라이브뷰 | WebRTC 플레이어 컴포넌트, 멀티 그리드 레이아웃 |
| PTZ Control | PTZ 제어 | 방향 버튼, 줌 슬라이더, 프리셋 목록 |
| Flow Editor | (향후) AI 파이프라인 편집기 | 노드 기반 비주얼 에디터 패턴 |
| Dashboard | 대시보드 | ApexCharts 통계, 실시간 이벤트 피드 |

**참고 소스 경로:**
```
/home/sulee/dev/onvif-standalone/sdh-workspace-legacy-onvif-ws/workspace-ui/
├── src/pages/device/                    # 디바이스 관리 UI
│   ├── onvif-manager/                   # ONVIF 검색/관리
│   │   └── fragment/discover/discover-onvif.vue  # 디스커버리 UI
│   └── ...
├── src/composables/                     # API 호출 훅 (useDeviceDiscovery 등)
├── src/pages/dashboard/                 # 대시보드
└── src/layouts/                         # 레이아웃 (사이드바, 네비게이션)
```

> **Note:** 이 문서의 프론트엔드 기본안은 `Next.js 15 + React 19`로 고정한다.
> `onvif-standalone`은 프레임워크 선택지가 아니라, 페이지 구성/레이아웃/상태 표현 방식의 참고 레퍼런스로만 사용한다.

---

## 13. 참고 오픈소스 프로젝트

### 13.1 NVR/VMS 플랫폼 (아키텍처 참고)

| 프로젝트 | Stars | 핵심 참고 포인트 |
|----------|-------|-----------------|
| **[Frigate NVR](https://github.com/blakeblackshear/frigate)** | 31.5K | 2단계 감지 파이프라인(모션→AI), go2rtc 통합, MQTT 이벤트, Zone 기반 감지 |
| **[DeepCamera (SharpAI)](https://github.com/SharpAI/DeepCamera)** | 2.7K | VLM 에이전트형 카메라, 플러그인 AI 스킬, YOLO26+VLM 하이브리드 |
| **[Viseron](https://github.com/roflcoopter/viseron)** | 2.8K | Python 올인원 NVR, 멀티 AI 백엔드, 컴포넌트 기반 설계 |
| **[CompreFace](https://github.com/exadel-inc/CompreFace)** | 7.9K | 얼굴인식 마이크로서비스 REST API, Docker 배포, 역할 관리 |
| **[Kerberos.io](https://github.com/kerberos-io/agent)** | 1.0K | Agent-Hub-Vault 분산 아키텍처, 카메라당 에이전트 패턴 |
| **[Moonfire NVR](https://github.com/scottlamb/moonfire-nvr)** | 1.7K | Rust, 무디코딩 녹화 (raw H.264), 메타데이터/영상 분리 저장 |

### 13.2 AI/ML 모델 및 라이브러리

| 프로젝트 | Stars | 용도 |
|----------|-------|------|
| **[Ultralytics YOLO](https://github.com/ultralytics/ultralytics)** | 56.3K | YOLO11/YOLO26 — 객체 탐지, 포즈 추정, 세그멘테이션 통합 |
| **[InsightFace](https://github.com/deepinsight/insightface)** | 28.5K | SCRFD (감지) + ArcFace (인식), ONNX 배포 |
| **[AdaFace](https://github.com/mk-minchul/AdaFace)** | 913 | 저화질 영상 얼굴 인식 (CVPR 2022), 감시카메라 특화 |
| **[DeepFace](https://github.com/serengil/deepface)** | 22.6K | 멀티 백엔드 래퍼, REST API 내장, 프로토타이핑 |
| **[MMAction2](https://github.com/open-mmlab/mmaction2)** | 5.0K | 행동 인식 (SlowFast, TSN, VideoMAE 등 20+ 아키텍처) |
| **[LangGraph](https://github.com/langchain-ai/langgraph)** | 30.0K | Multi-Agent 그래프, 상태 관리, 조건 분기 |

### 13.3 VLM (Vision Language Model)

| 프로젝트 | Stars | 특징 |
|----------|-------|------|
| **[Qwen2.5-VL](https://github.com/QwenLM/Qwen2-VL)** | 19.0K | 1시간+ 영상 이해, 7B/72B, 이벤트 시간 위치 파악 |
| **[StreamingVLM (MIT)](https://github.com/mit-han-lab/streaming-vlm)** | 962 | 무한 비디오 스트림 실시간 VLM — 감시카메라 직접 적용 가능 |
| **[InternVL](https://github.com/OpenGVLab/InternVL)** | 10.0K | GPT-4o 대안, 멀티모달 (CVPR 2024 Oral) |
| **[Video-LLaVA](https://github.com/PKU-YuanGroup/Video-LLaVA)** | 3.5K | 경량 비디오 VLM (EMNLP 2024) |

### 13.4 위험/이상 감지

| 프로젝트 | Stars | 용도 |
|----------|-------|------|
| **[fight_detection](https://github.com/imsoo/fight_detection)** | 227 | OpenPose + LSTM 실시간 싸움 감지 |
| **[HumanFallDetection](https://github.com/taufeeque9/HumanFallDetection)** | 336 | 다중 인물/다중 카메라 쓰러짐 감지 |
| **[fire-detection-cnn](https://github.com/tobybreckon/fire-detection-cnn)** | 571 | CNN 기반 화재 감지 (96% 정확도) |
| **[PE-MIL](https://github.com/Junxi-Chen/PE-MIL)** | 26 | CLIP + MIL 약지도 이상 감지 (CVPR 2024) |
| **[Weapons-and-Knives-Detector](https://github.com/JoaoAssalim/Weapons-and-Knives-Detector-with-YOLOv8)** | - | YOLOv8 기반 무기/칼 감지 |

### 13.5 영상 스트리밍 인프라

| 프로젝트 | Stars | 용도 |
|----------|-------|------|
| **[go2rtc](https://github.com/AlexxIT/go2rtc)** | 12.9K | RTSP→WebRTC 변환, 감시카메라 특화, Frigate 내장 |
| **[MediaMTX](https://github.com/bluenviron/mediamtx)** | 18.5K | 범용 미디어 라우터 (SRT/WebRTC/RTSP/HLS), 무트랜스코딩 |
| **[aiortc](https://github.com/aiortc/aiortc)** | 5.0K | Pure Python WebRTC — 서버 사이드 프레임 추출 + ML 추론 |
| **[python-onvif-zeep-async](https://github.com/openvideolibs/python-onvif-zeep-async)** | ~39 | 비동기 ONVIF 클라이언트 (Home Assistant 사용) |

### 13.6 핵심 아키텍처 벤치마크

조사 결과 도출된 업계 베스트 프랙티스:

1. **2단계 감지 파이프라인 (Frigate 패턴)**
   - CPU 모션 감지 → ROI 크롭 → GPU AI 추론
   - GPU 부하 80%+ 절감, 동시 카메라 수 극대화

2. **VLM 하이브리드 추론 (DeepCamera 패턴)**
   - 로컬 YOLO로 빠른 1차 감지 → VLM으로 장면 이해/확인
   - 로컬+클라우드 하이브리드 시 98% 정확도 달성 가능

3. **이벤트 기반 녹화 (Frigate/Moonfire 패턴)**
   - 이벤트 발생 시 전후 버퍼 포함 저장 (연속 녹화 대비 저장 공간 90%+ 절감)
   - 메타데이터(SSD)와 영상 데이터(HDD) 분리 저장

4. **MQTT 이벤트 배포 (업계 표준)**
   - 감시 분야 외부 시스템 연동 사실상 표준
   - Home Assistant, Node-RED, 다른 NVR과 즉시 연동 가능

5. **카메라당 에이전트 패턴 (Kerberos.io)**
   - 수평 확장에 유리, 카메라 추가/제거 시 다른 카메라에 영향 없음
   - 카메라당 ~50MB RAM, 2% CPU (1080p 기준)

6. **얼굴 인식 품질 적응 (AdaFace 연구 결과)**
   - 고화질 영상: ArcFace (99.83% LFW)
   - 저화질/야간: AdaFace (75%+ TinyFace — ArcFace 대비 현저히 우수)
   - 프레임 품질 점수 기반 자동 모델 전환
