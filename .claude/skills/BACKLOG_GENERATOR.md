# Skill: AI-VMS Backlog Generator

## 목적

Backlog Title을 입력하면 **행동 기반 Agile Backlog**를 생성한다.

Backlog는 다음 세 가지 타입을 가진다.

- Behavior Backlog
- UI Backlog
- System Backlog

출력 구조는 다음을 따른다.

Backlog Type
Backlog Title
Success Criteria
Todo

이 Skill은 **Behavior Driven Backlog 생성기**이며
AI-VMS 프로젝트의 FastAPI + Hexagonal Architecture + Next.js 아키텍처를 따른다.

---

# 프로젝트 컨텍스트

AI-VMS는 AI Multi-Agent 기반 영상 관리/관제 웹 서비스이다.

핵심 도메인

- **카메라 관리**: ONVIF WS-Discovery로 IP 카메라 자동 검색, 등록, 상태 모니터링
- **영상 스트리밍**: go2rtc를 통한 RTSP→WebRTC 변환, 라이브뷰
- **얼굴 인식**: InsightFace/AdaFace 기반 얼굴 감지/인식, 내부인/외부인 구별
- **위험 감지**: YOLO11 + Pose+LSTM으로 화재/폭력/무기/쓰러짐 감지
- **알림**: 위험 이벤트 발생 시 WebSocket/MQTT/Push/Email 알림
- **이벤트 관리**: 인식/위험/출입 이벤트 이력 관리
- **AI 에이전트**: LangGraph 기반 Planner→Detector→Analyzer→Dispatcher 파이프라인

아키텍처

- Backend: FastAPI + Hexagonal Architecture (Domain → Application → Adapter → Infrastructure)
- Frontend: Next.js App Router + Feature-based DDD (Domain → Application → Infrastructure → UI)
- AI/ML: InsightFace, YOLO11, MediaPipe, Qwen2.5-VL, LangGraph
- 인프라: PostgreSQL, Qdrant, Redis, MQTT, go2rtc

---

# Backlog Type

## Behavior Backlog

사용자 행동 또는 비즈니스 로직을 처리하는 Backlog

예

- 카메라 검색 및 등록
- 인물 등록 및 얼굴 사진 업로드
- 위험 이벤트 확인 및 처리
- 알림 규칙 설정
- 이벤트 이력 조회 및 필터링
- PTZ 카메라 제어

---

## UI Backlog

사용자 인터페이스 표시 및 상호작용 Backlog

예

- 멀티 카메라 라이브뷰 그리드 표시
- 대시보드 실시간 통계 표시
- 이벤트 타임라인 표시
- 카메라 디스커버리 진행 다이얼로그 표시
- 알림 배너 팝업 표시
- 얼굴 클러스터 카드 표시

---

## System Backlog

Backend 시스템 또는 AI 파이프라인 동작 Backlog

예

- ONVIF WS-Discovery 프로브 전송 및 응답 파싱
- RTSP 프레임 캡처 및 모션 감지
- InsightFace 얼굴 감지/임베딩 생성 및 Qdrant 검색
- YOLO11 화재/무기 감지 및 severity 평가
- Pose+LSTM 폭력/싸움 행동 분류
- LangGraph 에이전트 그래프 실행
- Redis Pub/Sub + MQTT 이벤트 발행

---

# Backlog Title 규칙

Backlog Title은 반드시 다음 구조를 따른다.

Actor + 행동 + 대상

---

# Actor 규칙

Actor는 다음 세 가지 중 하나여야 한다.

---

# User Actor

사용자 행동을 표현할 때 사용한다.

예

- 관리자
- 운영자
- 보안 담당자

---

# System Actor

시스템 또는 AI 엔진 동작을 표현할 때 사용한다.

예

- AI 에이전트
- 카메라 검색 시스템
- 얼굴 인식 엔진
- 위험 감지 엔진
- 알림 시스템
- 스트림 서비스
- ONVIF 클라이언트
- 행동 인식 엔진
- VLM 분석 서비스

---

# UI Actor

UI 표시 동작을 표현할 때 사용한다.

예

- 대시보드
- 카메라 매니저
- 라이브뷰
- 얼굴 관리 패널
- 알림 패널
- 이벤트 타임라인
- 설정 화면
- PTZ 컨트롤러
- 디스커버리 다이얼로그

---

# Backlog Title 예시

## Behavior Backlog

관리자가 네트워크 대역을 지정하여 IP 카메라를 검색한다
관리자가 인물을 등록하고 얼굴 사진을 업로드한다
보안 담당자가 위험 이벤트를 확인하고 처리 완료로 변경한다

---

## UI Backlog

라이브뷰가 WebRTC 멀티 카메라 그리드를 표시한다
대시보드가 실시간 인식/위험 이벤트 통계를 표시한다
알림 패널이 미확인 위험 알림 목록을 표시한다

---

## System Backlog

카메라 검색 시스템이 ONVIF 프로브를 전송하고 디바이스 목록을 반환한다
얼굴 인식 엔진이 RTSP 프레임에서 얼굴을 감지하고 내부인을 식별한다
위험 감지 엔진이 화재를 감지하고 관리자에게 알림을 발송한다

---

# 잘못된 Title 예시

다음 Title은 생성하지 않는다.

카메라 관리 기능 구현
얼굴 인식 개발
대시보드 버그 수정
알림 기능 개선

이 경우 다음 가이드를 출력한다.

Backlog Title이 규칙을 만족하지 않습니다.

Backlog Title은 다음 형식을 따라야 합니다.

Actor + 행동 + 대상

예

관리자가 네트워크 대역을 지정하여 IP 카메라를 검색한다
라이브뷰가 WebRTC 멀티 카메라 그리드를 표시한다

---

# Success Criteria 작성 규칙

Success Criteria는 **행동 성공 여부를 판단할 수 있어야 한다.**

Backlog Type에 따라 작성 방식이 다르다.

---

# Behavior Backlog Success Criteria

다음 정보를 반드시 포함해야 한다.

- 입력 조건
- 처리 과정
- 출력 결과 (사용자가 관찰 가능한 상태)

---

# UI Backlog Success Criteria

다음 기준으로 작성한다.

- 화면 표시 상태
- 사용자 상호작용 가능 여부
- UI 상태 변화
- 피드백 (토스트, 배너, 사운드 등)

---

# System Backlog Success Criteria

다음 기준으로 작성한다.

- 트리거 조건
- 처리 완료 상태
- 저장/출력 결과
- 에러 처리

---

# Todo 작성 규칙

Todo는 **행동 구현 단위 작업**으로 작성한다.

Todo는 다음 기준을 따른다.

- 기능 구현 중심
- 행동 단위 구현
- Hexagonal Architecture 레이어를 고려하되 레이어명으로 작성하지 않음

Todo는 **최대 5개까지만 작성한다.**

---

# Todo 금지 규칙

다음 항목은 Todo로 작성하면 안 된다.

Entity 작성
UseCase 작성
Router 작성
Repository 작성
Component 작성

Todo는 반드시 **행동 구현 작업**이어야 한다.

예

- ONVIF 프로브 응답에서 카메라 IP, 모델, 프로파일을 추출한다
- RTSP 프레임에서 얼굴을 감지하고 Qdrant에서 유사도를 검색한다
- severity가 HIGH 이상인 이벤트를 WebSocket + MQTT로 발행한다

---

# 출력 형식

출력은 반드시 다음 형식을 따른다.

Backlog Type
Behavior Backlog, UI Backlog, 또는 System Backlog

Backlog Title
<입력된 제목>

Success Criteria

- ...
- ...
- ...

Todo

1. ...
2. ...
3. ...
4. ...
5. ...

Todo는 필요한 만큼만 작성하며
**5개를 초과할 수 없다.**

---

# 최종 규칙

Backlog Title은 반드시 **Actor + 행동 + 대상 구조**여야 한다.

Actor는 다음 중 하나여야 한다.

- User Actor
- System Actor
- UI Actor

Backlog는 반드시 **Behavior / UI / System Backlog** 중 하나여야 한다.

Success Criteria는 **관찰 가능한 결과**여야 한다.

Todo는 **행동 구현 단위로 작성한다.**

Todo는 **최대 5개까지만 작성한다.**
