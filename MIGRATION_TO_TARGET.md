# AI-VMS 타겟 시스템 이전 가이드

## 1. 시스템 정보

### 개발 시스템 (현재)
- CPU: Intel (노트북)
- RAM: 제한적
- GPU: NVIDIA GeForce MX250 (2GB VRAM, Compute Capability 6.1 / Pascal)
- OS: Ubuntu 24.04 (Linux 6.17.0)
- NVIDIA Driver: 580.126.09, CUDA: 13.0

### 타겟 시스템
- CPU: Intel i9
- RAM: 48GB
- GPU: NVIDIA RTX 3060 (12GB VRAM, CC 8.6) + Quadro 4000 (8GB VRAM, CC 7.5)
- 목표: GPU 가속 AI 추론 + 개발/빌드/배포 통합

## 2. 타겟 시스템 초기 설정

### 2.1 필수 패키지

```bash
# NVIDIA 드라이버 + Container Toolkit
sudo apt install nvidia-driver-550 nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 확인
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

### 2.2 프로젝트 클론 및 환경 설정

```bash
git clone <repo-url> ~/dev/ai-vms
cd ~/dev/ai-vms
cp .env.example .env
```

### 2.3 .env 설정 (타겟 시스템용)

MX250에서는 저사양 설정을 사용했지만, RTX 3060에서는 고성능 설정 사용:

```env
# 고정밀 모델 (RTX 3060에서 GPU 가속)
FACE_MODEL_NAME=buffalo_l
FACE_DET_SIZE=640

# 나머지는 .env.example과 동일
```

현재 개발 시스템의 .env는 MX250에 맞춰 `buffalo_sc` / `det_size=320`으로 되어 있음.

### 2.4 서비스 기동

```bash
# GPU 프로필로 전체 서비스 시작
docker-compose -f docker/docker-compose.dev.yml --profile gpu up -d

# GPU 백엔드만 사용 (CPU backend 충돌 방지)
docker-compose -f docker/docker-compose.dev.yml up -d postgres redis qdrant mosquitto go2rtc
docker-compose -f docker/docker-compose.dev.yml --profile gpu up -d backend-gpu
docker-compose -f docker/docker-compose.dev.yml up -d --no-deps frontend
```

### 2.5 데이터베이스 마이그레이션

```bash
docker-compose -f docker/docker-compose.dev.yml exec backend-gpu alembic upgrade head
```

## 3. 오늘 수행한 변경사항 (2026-04-28)

### 3.1 Dockerfile.gpu 개선

**파일**: `docker/Dockerfile.gpu`

**변경 전**: `python:3.12-slim` 기반 (CUDA 라이브러리 없음)
**변경 후**: `nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04` 기반

- ONNX Runtime GPU가 `libcublasLt.so.12` 등 CUDA 런타임 라이브러리를 요구
- python:3.12-slim에는 이 라이브러리가 없어 CUDAExecutionProvider 로드 실패
- NVIDIA CUDA 베이스 이미지로 변경하여 GPU 추론 지원

**타겟 시스템 영향**: RTX 3060(CC 8.6)에서는 CUDAExecutionProvider가 정상 동작할 것으로 예상. Conv 테스트도 통과할 것.

### 3.2 InsightFace GPU 감지 개선

**파일**: `backend/app/infrastructure/ai/insightface_service.py`

**문제**: 기존 `_detect_gpu()`가 단순 `Identity` 연산으로만 GPU 테스트 → cuDNN Conv 연산이 실제로 지원되는지 검증 못함
**해결**: Conv 연산을 실행하여 cuDNN이 실제로 작동하는지 검증. 실패 시 CPU 폴백.

- MX250(CC 6.1): cuDNN 9가 Pascal 아키텍처 미지원 → Conv 테스트 실패 → CPU 폴백
- RTX 3060(CC 8.6): Ampere 아키텍처 완벽 지원 → Conv 테스트 통과 → GPU 사용

### 3.3 RTSP 프레임 캡처 개선

**파일**: `backend/app/infrastructure/ai/frame_capture.py`

- RTSP URL에서 `#tcp` 접미사 제거 (go2rtc 전용 힌트, OpenCV에서 404 유발)
- `cv2.CAP_FFMPEG` 백엔드 명시
- 연결/읽기 타임아웃 5초 설정 (오프라인 카메라로 인한 파이프라인 지연 방지)
- RTSP 연결 실패 시 디버그 로깅 추가

### 3.4 Qdrant 클라이언트 API 업데이트

**파일**: `backend/app/domains/face/adapter/outbound/external/qdrant_embedding_adapter.py`

- `qdrant-client` 1.17에서 `client.search()` 제거됨
- `client.query_points()` 로 마이그레이션
- 반환값: `results` → `response.points`

### 3.5 WebSocket 알림 수정

**파일**: `frontend/features/alert/application/hooks/useAlerts.ts`

**문제**: 환경변수 `NEXT_PUBLIC_WS_URL`이 `wss://192.168.0.42:8000`으로 하드코딩되어 있어, `https://localhost:3000`에서 접속 시 SSL 인증서 호스트 불일치로 WebSocket 연결 실패
**해결**: 현재 페이지의 `window.location.hostname`에서 WebSocket URL을 동적 생성

### 3.6 알림 메시지 타입 수정

**파일**: `backend/app/infrastructure/event_bus/notification_dispatcher.py`

- 백엔드가 `DANGER_ALERT` 타입으로 브로드캐스트, 프론트엔드가 `DANGER_EVENT`를 기대
- `DANGER_ALERT` → `DANGER_EVENT`로 통일

### 3.7 파이프라인 디버그 로깅 추가

**파일**: `backend/app/domains/face/application/usecase/face_recognition_pipeline.py`

- 프레임 캡처 실패 시 로깅
- 얼굴 검출 성공 시 개수 로깅
- 품질 필터로 스킵된 얼굴 로깅

## 4. 현재 알려진 이슈 및 상태

### 4.1 MX250 GPU 제약 (타겟에서 해결됨)

| 컴포넌트 | MX250 상태 | RTX 3060 예상 |
|----------|-----------|--------------|
| ONNX Runtime (InsightFace) | CPU 폴백 (cuDNN CC 6.1 미지원) | GPU 가속 |
| PyTorch (YOLO) | CPU 전용 (CC >= 7.5 필요) | GPU 가속 |
| buffalo_l 모델 | VRAM 부족으로 buffalo_sc 사용 | buffalo_l 사용 가능 |
| det_size=640 | VRAM 부족으로 320 사용 | 640 사용 가능 |

### 4.2 카메라 상태

| 카메라 | IP | RTSP | 상태 |
|--------|-----|------|------|
| HIKVISION DS-2DE2204IW-DE3 | 192.168.0.93 | OK | 프레임 캡처 정상 |
| Tapo C500 | 192.168.0.199 | OK | 프레임 캡처 정상 |
| Tapo C200 | 192.168.0.240 | 불안정 | RTSP 404 간헐 발생 |

- 카메라 status가 DB에서 `OFFLINE`으로 초기화되는 문제 있음 (수동으로 `ONLINE` 설정 필요)
- 타겟 시스템에서도 동일 네트워크(192.168.0.x)에 있어야 카메라 접근 가능

### 4.3 얼굴 인식 파이프라인

- **동작 확인됨**: 카메라에서 프레임 캡처 → InsightFace 검출 → Qdrant 검색 → recognition_log 생성
- **Qdrant 임베딩**: 이승욱 1건 수동 등록 완료 (face_image에서 추출)
- **알림 규칙**: "Face Recognition Alert" 규칙 생성됨 (`enable_face_recognition=true`)
- **미확인**: 등록된 인물과 카메라 영상 매칭이 실제로 알림을 트리거하는지 (MX250 CPU 환경에서 검증 한계)

### 4.4 YOLO 위험 감지

- 커스텀 모델 `models/yolo11-danger.pt` 파일 없음
- 표준 YOLO11 모델은 화재/무기 등 커스텀 클래스 미포함
- 커스텀 학습 또는 사전 학습된 위험 감지 모델 필요

### 4.5 프론트엔드 이슈

- 콘솔에 Mixed Content 경고 (HTTPS 페이지에서 HTTP 리소스 요청)
- 개발 환경 자체 서명 인증서 사용 중
- `NEXT_PUBLIC_API_URL`이 `https://192.168.0.42:8000`으로 설정됨 → 타겟 시스템 IP로 변경 필요

## 5. 타겟 시스템에서 즉시 이어할 작업

### 5.1 환경 설정 변경

```bash
# .env 수정
FACE_MODEL_NAME=buffalo_l      # 고정밀 모델
FACE_DET_SIZE=640               # 고해상도 검출

# docker-compose.dev.yml의 frontend 환경변수 수정
NEXT_PUBLIC_API_URL=https://<타겟IP>:8000
NEXT_PUBLIC_WS_URL=wss://<타겟IP>:8000
NEXT_PUBLIC_GO2RTC_URL=http://<타겟IP>:1984
```

### 5.2 SSL 인증서 재생성 (타겟 IP 포함)

```bash
cd docker/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout localhost.key -out localhost.crt \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:<타겟IP>"
```

### 5.3 GPU 동작 검증

```bash
# 빌드 및 시작
docker-compose -f docker/docker-compose.dev.yml --profile gpu up -d --build backend-gpu

# 헬스 체크 — insightface_gpu: true 확인
curl -sk https://localhost:8000/health | python3 -m json.tool

# 기대 결과:
# "insightface_gpu": true   (RTX 3060에서 CUDAExecutionProvider 사용)
# "yolo_gpu": true           (PyTorch CUDA 지원)
```

### 5.4 얼굴 임베딩 재등록

Qdrant 데이터는 Docker 볼륨에 저장되므로, 타겟 시스템에서 새로 등록 필요:

```bash
# 컨테이너 내부에서 실행
docker-compose -f docker/docker-compose.dev.yml exec backend-gpu python3 -c "
import asyncio
from uuid import uuid4

async def register_all():
    import cv2, os
    from app.infrastructure.ai.insightface_service import InsightFaceService
    from app.domains.face.adapter.outbound.external.qdrant_embedding_adapter import QdrantEmbeddingAdapter

    svc = InsightFaceService()
    await svc.load_models()
    store = QdrantEmbeddingAdapter()

    # 이승욱
    img = cv2.imread('/app/uploads/faces/489299da-f1c4-492c-9dc6-2e5f5556c31f.jpg')
    if img is not None:
        faces = await svc.detect_and_embed(img)
        if faces:
            await store.store(face_id=uuid4(), identity_id='c0900a5a-9c36-48e2-92f4-62d1c6a79057', embedding=faces[0].embedding)
            print(f'이승욱: registered (conf={faces[0].confidence:.3f})')

    # 추가 Identity가 있으면 동일 패턴으로 등록

asyncio.run(register_all())
"
```

### 5.5 카메라 상태 ONLINE 설정

```bash
docker-compose -f docker/docker-compose.dev.yml exec backend-gpu python3 -c "
import asyncio
async def fix():
    from app.infrastructure.database.session import async_session_factory
    from app.domains.camera.infrastructure.orm.camera_orm import CameraORM
    from sqlalchemy import update
    async with async_session_factory() as session:
        async with session.begin():
            await session.execute(update(CameraORM).values(status='ONLINE'))
            print('All cameras set to ONLINE')
asyncio.run(fix())
"
```

### 5.6 남은 개발 과제

1. **YOLO 위험 감지 모델**: `models/yolo11-danger.pt` 커스텀 학습 또는 사전 학습 모델 확보
2. **카메라 상태 자동 관리**: RTSP 연결 성공/실패에 따라 카메라 status를 자동 업데이트
3. **얼굴 등록 플로우 개선**: 웹 UI에서 사진 업로드 시 자동으로 Qdrant에 임베딩 저장
4. **듀얼 GPU 활용**: RTX 3060(InsightFace) + Quadro 4000(YOLO) 분리 배치 검토
5. **알림 규칙 편집 기능**: 기존 규칙의 수정 UI 없음 (현재 삭제 후 재생성만 가능)
6. **WebSocket 안정화**: 자체 서명 인증서 + Mixed Content 이슈 해결

## 6. 아키텍처 참조

```
Backend:  Hexagonal Architecture (Domain → Application → Adapter → Infrastructure)
Frontend: Feature-based DDD (Domain → Application → Infrastructure → UI)

주요 AI 서비스:
- InsightFace: backend/app/infrastructure/ai/insightface_service.py
- YOLO:        backend/app/infrastructure/ai/yolo_service.py
- 프레임 캡처:  backend/app/infrastructure/ai/frame_capture.py
- 파이프라인:   backend/app/infrastructure/pipeline/face_recognition_bootstrap.py
- 파이프라인 워커: backend/app/domains/face/application/usecase/face_recognition_pipeline.py
- Qdrant 어댑터: backend/app/domains/face/adapter/outbound/external/qdrant_embedding_adapter.py
- 알림 디스패처: backend/app/infrastructure/event_bus/notification_dispatcher.py
```

## 7. Docker Compose 프로필

```bash
# CPU 백엔드 (기본)
docker-compose -f docker/docker-compose.dev.yml up -d

# GPU 백엔드 (--profile gpu)
docker-compose -f docker/docker-compose.dev.yml --profile gpu up -d backend-gpu

# 주의: backend와 backend-gpu는 같은 포트(8000) 사용 → 동시 실행 불가
# frontend는 backend에 의존하므로, GPU만 사용 시 --no-deps로 시작
docker-compose -f docker/docker-compose.dev.yml up -d --no-deps frontend
```
