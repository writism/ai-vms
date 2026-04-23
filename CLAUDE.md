# CLAUDE.md — AI-VMS

## 필수 워크플로우

### 기능 요청 시 backlog → implement

사용자가 기능 수정/변경/개선/구현을 요청하면 **반드시** 다음 순서를 따른다:

1. `/backlog` 커맨드로 백로그를 작성하여 사용자에게 보여준다
2. 사용자가 확인하면 `/implement` 커맨드로 구현한다

- backlog 없이 바로 코딩하지 않는다
- 구현 결과는 검증 가능한 형태로 보고한다 (API 동작, UI 플로우, 테스트 결과)
- 커맨드 파일: `.claude/commands/backlog.md`, `.claude/commands/implement.md`
- 스킬 정의: `.claude/skills/BACKLOG_GENERATOR.md`, `.claude/skills/IMPLEMENTATION.md`
- **주의**: 작업 디렉토리가 `ai-vms` 루트가 아닌 경우 커맨드가 로딩되지 않을 수 있음. 이 경우 스킬 파일을 직접 읽어서 동일한 형식으로 수행한다.

## 아키텍처 규칙

- Backend: Hexagonal Architecture (Domain → Application → Adapter → Infrastructure)
- Frontend: Feature-based DDD (Domain → Application → Infrastructure → UI)
- Domain 레이어는 외부 라이브러리 import 금지
- ORM 모델과 Domain Entity는 반드시 분리 (Mapper 사용)
- UseCase는 Port 인터페이스를 통해서만 외부 접근

## 개발 지시서

- 상세 설계: `INITIAL_DEVELOPMENT_PROMPT.md`
- Phase 단위로 순차 구현 (Phase 1부터)
- MVP 범위를 우선 완료한 뒤 후순위 기능 진행
