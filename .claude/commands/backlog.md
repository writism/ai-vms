# Command: /backlog

## 목적

사용자가 Backlog Title을 입력하면
AI-VMS용 Agile Backlog를 생성한다.

Backlog는 다음 세 가지 타입을 가진다.

- Behavior Backlog
- UI Backlog
- System Backlog

이 Command는 다음 규칙을 사용한다.

.claude/skills/BACKLOG_GENERATOR.md

---

## 중요 규칙 (Strict)

반드시 **Behavior Driven Backlog Generator Skill**을 사용한다.

다음 형식은 절대 생성하지 않는다.

- Given
- When
- Then
- Scenario
- Test Case
- Component specification
- Props 정의
- API 설계

이 Command는 **테스트 시나리오 생성 명령이 아니다.**

반드시 **Backlog 형식으로만 출력한다.**

---

## 사용 방법

/backlog <Backlog Title>

예시

/backlog 관리자가 네트워크 대역을 지정하여 IP 카메라를 검색한다

또는

/backlog 라이브뷰가 멀티 카메라 그리드를 표시한다

또는

/backlog 위험 감지 엔진이 화재를 감지하고 관리자에게 알림을 발송한다

---

## 동작 규칙

1. 사용자가 입력한 Backlog Title을 읽는다
2. Actor를 분석하여 Backlog Type을 결정한다

Actor가 다음일 경우

User Actor (관리자, 운영자, 보안 담당자)
→ Behavior Backlog

System Actor (AI 에이전트, 카메라 검색 시스템, 얼굴 인식 엔진, 위험 감지 엔진, 알림 시스템, 스트림 서비스, ONVIF 클라이언트)
→ System Backlog

UI Actor (대시보드, 카메라 매니저, 라이브뷰, 얼굴 관리 패널, 알림 패널, 이벤트 타임라인, 설정 화면)
→ UI Backlog

3. Skill 규칙을 적용하여 Backlog를 생성한다

---

## 출력 형식

Backlog Type
Behavior Backlog, UI Backlog, 또는 System Backlog

Backlog Title
<입력된 제목>

Success Criteria

- ...
- ...
- ...
- ...

Todo

1. ...
2. ...
3. ...
4. ...
5. ...

Todo는 **최대 5개까지만 작성한다.**

---

## Title 검증 규칙

Title은 반드시 다음 구조여야 한다.

Actor + 행동 + 대상

Actor는 다음 중 하나여야 한다.

### User Actor

- 관리자
- 운영자
- 보안 담당자

### System Actor

- AI 에이전트
- 카메라 검색 시스템
- 얼굴 인식 엔진
- 위험 감지 엔진
- 알림 시스템
- 스트림 서비스
- ONVIF 클라이언트
- 행동 인식 엔진
- VLM 분석 서비스

### UI Actor

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

## 규칙 위반 처리

Title이 규칙을 만족하지 않으면
Backlog를 생성하지 않고 다음 가이드를 출력한다.

Backlog Title이 규칙을 만족하지 않습니다.

Backlog Title은 다음 형식을 따라야 합니다.

Actor + 행동 + 대상

예

관리자가 네트워크 대역을 지정하여 IP 카메라를 검색한다
라이브뷰가 WebRTC 멀티 카메라 그리드를 표시한다
위험 감지 엔진이 화재를 감지하고 관리자에게 알림을 발송한다
