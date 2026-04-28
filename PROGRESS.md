# AI-VMS 개발 진행 현황

> 최종 업데이트: 2026-04-28

---

## 완료된 작업 (Phase 1~6 + 추가 기능)

### Phase 1: 기반 구축

- [x] FastAPI + Next.js 15 프로젝트 초기 세팅
- [x] Hexagonal Architecture 스켈레톤 (camera, auth, face, alert, event, agent, stream 도메인)
- [x] PostgreSQL + Alembic 마이그레이션 설정 (초기 8개 테이블)
- [x] Docker Compose 개발/프로덕션 환경 구성
- [x] JWT 인증 구현 (httpOnly cookie)
- [x] 기본 UI 레이아웃 (Sidebar, Dashboard, 다크/라이트 테마)

### Phase 2: 카메라 관리

- [x] ONVIF WS-Discovery 구현 (멀티캐스트 프로브, 자동 검색)
- [x] 카메라 CRUD API + 프론트엔드 (등록/수정/삭제)
- [x] go2rtc 연동 (RTSP→WebRTC 스트리밍)
- [x] 라이브뷰 UI (싱글/멀티뷰)
- [x] 카메라 상태 모니터링 (RTSP TCP 포트 체크)
- [x] coturn 자체 STUN/TURN 서버 추가
- [x] 카메라 삭제 시 연관 데이터 보호 (409 에러)
- [x] 미디어서버 스캔/모니터링 (대시보드 섹션)

### Phase 3: ORM/리포지토리

- [x] 전 도메인 SQLAlchemy ORM + Mapper 구현
- [x] FastAPI Depends 기반 DB 세션 주입 (전 도메인)
- [x] In-memory ↔ SQLAlchemy 리포지토리 자동 전환 (`USE_DATABASE` 플래그)

### Phase 4-5: AI 추론 + Multi-Agent

- [x] InsightFace 서비스 (SCRFD 감지 + ArcFace 임베딩, ONNX Runtime)
- [x] YOLO11 위험 감지 서비스 (화재/연기/무기)
- [x] 프레임 캡처 (OpenCV RTSP + 모션 게이팅)
- [x] LangGraph Multi-Agent 그래프 (Planner→Detector→Analyzer→Dispatcher)
- [x] MQTT 클라이언트 (aiomqtt, danger/face/camera 토픽)
- [x] NotificationDispatcher (AlertRule 기반 WebSocket/MQTT/Email 선택 발송)

### Phase 6: 마이그레이션, 테스트, Docker

- [x] Alembic 초기 마이그레이션 (8개 테이블)
- [x] 구조화 로깅 (JSON 포맷)
- [x] 도메인 에러 클래스 + 글로벌 핸들러
- [x] 헬스체크 (AI 서비스 상태 포함)
- [x] pytest 단위 테스트 15개 (auth, camera, alert, event, face)
- [x] Docker 3종 (backend, frontend, GPU)
- [x] 프로덕션 entrypoint (마이그레이션→시딩→서버)

### 추가 기능 (Phase 이후)

- [x] WebRTC 스트리밍 파이프라인 완성 (CORS, 자동등록, ICE/TURN)
- [x] 서비스 헬스 체크 UI (API/go2rtc/TURN 실시간)
- [x] 다크/라이트 테마 토글 (next-themes)
- [x] 사이드바 Lucide 아이콘, 접기/펼치기
- [x] 알림 WebSocket 자동 재연결
- [x] 프론트엔드 미완성 페이지 전체 구현 (알림 규칙, 카메라 상세, 이벤트 타임라인, 미식별 얼굴)
- [x] 얼굴 인식 파이프라인 + 부트스트랩 구현
- [x] 인식 로그 도메인/리포지토리/유즈케이스
- [x] Identity 수정 다이얼로그, 사진 업로드, 타입 확장 (employee/visitor/vip/blacklist)
- [x] Alert 규칙에 얼굴 인식 연동 필드 추가
- [x] Alembic 마이그레이션 3건 추가 (identity type, recognition_logs, alert_rule 필드)

---

## 현재 구현 현황 (도메인별)

### Backend 도메인 구조

| 도메인 | Entity | UseCase | Port | Router | Repository | ORM/Mapper | 상태 |
|--------|--------|---------|------|--------|------------|------------|------|
| camera | camera, network | register, get, update, delete, discover | camera_repo, network_repo, discovery | O | sqlalchemy + in-memory | O | **완료** |
| face | identity, face, recognition_log | identity, face_search, face_recognition_pipeline, recognition_log | identity_repo, face_repo, recognition_log, face_recognition, face_embedding | O | sqlalchemy + in-memory | O | **완료** |
| alert | alert_rule, danger_event | alert_rule, danger_event | alert_rule_repo, danger_event_repo, danger_detection | O | sqlalchemy + in-memory | O | **완료** |
| event | event | event | event_repo | O | sqlalchemy + in-memory | O | **완료** |
| auth | user | login, get_user | user_repo, password, token | O | sqlalchemy + in-memory | O | **완료** |
| agent | agent_task | run_agent_pipeline | - | O | - | - | **최소 구현** |
| stream | - | stream, capture_frame | stream_port | O | go2rtc adapter | - | **완료** (stateless) |
| setting | - | - | - | - | - | - | **미구현** |
| notification | - | - | - | alert 도메인에 통합 | - | - | **부분 구현** |

### Frontend 페이지 현황

| 페이지 | 경로 | 상태 |
|--------|------|------|
| 대시보드 | `/` | **완료** (통계, 미디어서버 모니터링) |
| 카메라 목록 | `/cameras` | **완료** |
| 카메라 상세 | `/cameras/[id]` | **완료** |
| 라이브뷰 | `/live` | **완료** (멀티뷰, WebRTC) |
| 얼굴 관리 | `/faces` | **완료** (등록/수정/삭제, 사진 업로드) |
| 미식별 얼굴 | `/faces/unidentified` | **완료** (클러스터 UI) |
| 알림 목록 | `/alerts` | **완료** |
| 알림 규칙 | `/alerts/rules` | **완료** (생성/삭제) |
| 이벤트 | `/events` | **완료** (타임라인, 필터) |
| 로그인 | `/login` | **완료** |
| 설정 | `/settings` | **미구현** (빈 페이지) |

### 인프라 현황

| 구성 요소 | 파일 | 상태 |
|-----------|------|------|
| InsightFace AI | insightface_service.py | **완료** |
| YOLO 위험 감지 | yolo_service.py | **완료** |
| 프레임 캡처 | frame_capture.py | **완료** |
| 얼굴 인식 파이프라인 | face_recognition_bootstrap.py | **완료** |
| LangGraph Agent | graph_builder, runner, nodes/ | **완료** |
| go2rtc 클라이언트 | go2rtc_client.py | **완료** |
| ONVIF 디스커버리 | client.py, discovery.py | **완료** |
| MQTT 이벤트 버스 | mqtt_client.py | **완료** |
| Redis 이벤트 버스 | redis_event_bus.py | **완료** |
| WebSocket 매니저 | ws_manager.py | **완료** |
| 알림 디스패처 | notification_dispatcher.py | **완료** |
| 미디어서버 스캐너 | media_server_scanner.py | **완료** |
| 구조화 로깅 | logging_config.py | **완료** |
| 에러 핸들링 | errors.py | **완료** |
| Redis 캐시 | cache/ | **미구현** (빈 디렉토리) |

---

## 남은 작업 (TODO)

### 우선순위 1: MVP 완성을 위한 필수 작업

#### 인프라/환경

- [ ] **NVIDIA 드라이버 Secure Boot MOK 등록 완료** — 현재 `nvidia` 모듈 로드 실패 중 (`Key was rejected by service`). 리부팅 후 MOK Manager에서 키 등록 필요
- [ ] `.gitignore`에 `docker/certs/`, `backend/uploads/` 추가
- [ ] NVIDIA Container Toolkit 동작 검증 (GPU Docker 컨테이너)

#### 실시간 얼굴 인식 파이프라인 검증

- [ ] 얼굴 인식 파이프라인 end-to-end 테스트 (카메라 → 감지 → 임베딩 → Qdrant 검색 → 인식 로그)
- [ ] Qdrant 벡터 스토어 연동 검증 (임베딩 저장/검색)
- [ ] 인식 이벤트 → WebSocket 실시간 알림 연동 검증

#### 위험 감지 파이프라인 검증

- [ ] YOLO 위험 감지 end-to-end 테스트 (카메라 → 프레임 → YOLO → 이벤트)
- [ ] 위험 이벤트 → 알림 규칙 → 알림 발송 연동 검증
- [ ] 스냅샷/클립 저장 검증

#### 설정 도메인

- [ ] 시스템 설정 API (GET/PATCH `/api/v1/settings`)
- [ ] 설정 페이지 UI 구현 (go2rtc 모드, 인식 임계값, 알림 설정 등)

### 우선순위 2: 품질/안정성 개선

#### 테스트 확충

- [ ] 얼굴 인식 파이프라인 단위 테스트
- [ ] 인식 로그 유즈케이스 테스트
- [ ] WebRTC 스트리밍 통합 테스트
- [ ] 프론트엔드 테스트 (현재 0건)

#### Docker 배포 검증

- [ ] `docker-compose.yml` (프로덕션) 전체 서비스 기동 테스트
- [ ] GPU 프로필 분리 검증 (`docker-compose.dev.yml`)
- [ ] 헬스체크 동작 확인 (PostgreSQL, Redis, Qdrant, go2rtc)

#### 보안

- [ ] 카메라 패스워드 AES 암호화 저장 (현재 평문 가능성)
- [ ] RTSP URL 로그 마스킹 (크레덴셜 제거)
- [ ] Role-based 접근 제어 적용 (ADMIN/OPERATOR/VIEWER)

### 우선순위 3: 성능 최적화 (GPU 환경 준비 후)

- [ ] ONNX → TensorRT FP16 모델 변환
- [ ] SCRFD-2.5GF 감지기 적용
- [ ] 적응형 프레임 스킵 (모션 레벨 기반 3~15)
- [ ] 다중 카메라 배치 추론
- [ ] 트래커 연계 (SORT/DeepSORT) — 매 프레임 재인식 방지
- [ ] AdaFace 폴백 (저화질 카메라 자동 전환)
- [ ] 이중 임계값 판정 (높은 임계값 → 확정, 중간 → VLM 확인)
- [ ] Qdrant HNSW 튜닝 + Scalar Quantization

### 우선순위 4: MVP 이후 기능

- [ ] 행동 인식 파이프라인 (Pose Estimation + LSTM — 폭력/싸움/쓰러짐)
- [ ] VLM 장면 분석 서비스 (Qwen2.5-VL-7B / StreamingVLM)
- [ ] 미식별 얼굴 클러스터링 (DBSCAN)
- [ ] 출입 이벤트 (entry/exit) 도메인 구현
- [ ] 이벤트 기반 녹화 (전후 버퍼 클립 저장)
- [ ] PTZ 자동 추적
- [ ] Email/Push 알림 실제 연동 (SMTP, VAPID)
- [ ] 감사 로그 (얼굴 조회/등록/수정/삭제)
- [ ] 데이터 보존 정책 (스냅샷/클립/감사로그 retention)
- [ ] Redis 캐시 레이어 구현
- [ ] Prometheus 메트릭 수집
- [ ] 외부 시스템 연동 (Home Assistant, Node-RED)

---

## 커밋 이력

| 해시 | 설명 |
|------|------|
| `41b9256` | Phase 1 MVP 초기 구현 |
| `81ad896` | Phase 2 — 위험감지/알림, 이벤트, 실시간 알림, 전체 UI |
| `5b8c196` | Phase 3 — ORM/SQLAlchemy, 로그인/설정 UI |
| `33ffd5e` | Phase 4-5 — AI 추론, LangGraph, MQTT |
| `a7fff42` | Phase 6 — 마이그레이션, 테스트, 로깅, Docker |
| `f9a0fe9` | 테스트 오류 수정 (passlib→bcrypt) |
| `28e4187` | Docker Compose 인프라 완성, 프론트엔드 도메인 모델 보완 |
| `3800acd` | 프로덕션 준비 — lazy import, Docker, 시딩 스크립트 |
| `2f3c7d4` | 전 도메인 DB 세션 주입, 통합 테스트 통과 |
| `baf93d1` | 프론트엔드 미완성 페이지 구현 완료 |
| `08b1000` | WebRTC 스트리밍 파이프라인 완성, UI 현대화 |
| `1a7fb3b` | 카메라 삭제, 미디어서버 모니터링, WebRTC 안정화 |
| `22dd888` | 얼굴 인식 파이프라인, 인식 로그, Identity 관리 개선 |
