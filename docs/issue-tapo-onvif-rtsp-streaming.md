# Tapo 카메라 ONVIF/RTSP 스트리밍 연동 이슈

**날짜**: 2026-04-24  
**영향 범위**: 백엔드 ONVIF 클라이언트, go2rtc 스트리밍, 환경설정  
**대상 카메라**: TP-Link Tapo C500 (192.168.0.199), Tapo C200 (192.168.0.240)

---

## 1. 증상

Tapo C500 카메라를 등록한 뒤 카메라 상세 페이지에서:

- "ONVIF RTSP 자동 조회" 버튼을 눌러도 RTSP URL이 설정되지 않음
- RTSP URL을 수동 설정해도 영상이 표시되지 않고 "연결 실패" 표시
- 브라우저 콘솔에 `POST /api/webrtc → 500 Internal Server Error` 발생
- go2rtc 로그에 `streams: wrong user/pass` 에러

반면 Hikvision DS-2DE2204IW-DE3 카메라는 동일한 흐름에서 정상 동작.

---

## 2. 근본 원인 (3가지)

### 2.1. ONVIF 인증 방식 불일치

| 항목 | Hikvision | Tapo |
|------|-----------|------|
| ONVIF 인증 | HTTP Digest Auth | WS-Security UsernameToken |
| ONVIF 포트 | 80 | 2020 |

기존 ONVIF 클라이언트(`app/infrastructure/onvif/client.py`)는 `httpx.DigestAuth`만 지원했다. Tapo 카메라는 SOAP 헤더에 WS-Security UsernameToken을 포함해야 ONVIF API에 응답하므로, Digest Auth로는 인증 자체가 불가능했다.

**WS-Security UsernameToken 구조:**

```xml
<s:Header>
  <Security xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
    <UsernameToken>
      <Username>sg-c500-01</Username>
      <Password Type="...#PasswordDigest">Base64(SHA1(nonce + created + password))</Password>
      <Nonce EncodingType="...#Base64Binary">Base64(random_16_bytes)</Nonce>
      <Created>2026-04-24T06:00:00.000Z</Created>
    </UsernameToken>
  </Security>
</s:Header>
```

Password Digest 계산식:
```
digest = Base64(SHA1(nonce_bytes + created_utf8 + password_utf8))
```

### 2.2. RTSP 전송 프로토콜 불일치

| 항목 | Hikvision | Tapo |
|------|-----------|------|
| RTSP 기본 전송 | UDP (정상) | UDP (인증 실패) |
| RTSP TCP 전송 | 정상 | **정상** |

Tapo C500의 RTSP 서버는 UDP 모드에서 Digest Auth 핸드셰이크 시 동일 TCP 연결에서의 재인증을 거부한다. 구체적으로:

1. 클라이언트가 `DESCRIBE` 요청 → 카메라가 `401 Unauthorized` + nonce 반환
2. 클라이언트가 **같은 연결에서** Digest 인증 포함하여 재요청 → **401 재반환 (실패)**
3. 클라이언트가 **새 연결에서** Digest 인증 포함하여 요청 → **200 OK (성공)**

```
# 실패 (같은 소켓)
sock.send(DESCRIBE)          → 401 + nonce
sock.send(DESCRIBE + Auth)   → 401 (거부)

# 성공 (새 소켓)
sock1.send(DESCRIBE)          → 401 + nonce
sock2.send(DESCRIBE + Auth)   → 200 OK + SDP
```

ffprobe, go2rtc 모두 기본적으로 같은 연결에서 재인증을 시도하므로 Tapo에서 실패한다. go2rtc의 `#tcp` 플래그를 사용하면 TCP 인터리브 모드로 전환되어 이 문제를 우회한다.

**검증 결과:**

```bash
# UDP (기본) - 실패
ffprobe "rtsp://sg-c500-01:qazwsx123@192.168.0.199:554/stream1"
# → 401 Unauthorized

# TCP - 성공
ffprobe -rtsp_transport tcp "rtsp://sg-c500-01:qazwsx123@192.168.0.199:554/stream1"
# → H264 1280x720, codec detected
```

### 2.3. 백엔드 환경설정 미로딩

`.env` 파일이 프로젝트 루트(`ai-vms/.env`)에 있지만, 백엔드는 `ai-vms/backend/`에서 실행된다. pydantic-settings의 `env_file: ".env"` 설정이 상대경로로 되어 있어 파일을 찾지 못했다.

| 설정 | 의도 | 실제 적용 |
|------|------|----------|
| `USE_DATABASE` | `true` (DB 사용) | `false` (기본값 → 인메모리) |
| `CORS_ORIGINS` | `localhost:3000, 192.168.0.42:3000` | `localhost:3000`만 |

이로 인해:
- 서버 재시작 시 인메모리 데이터 소실 → 등록된 카메라 사라짐
- LAN IP(192.168.0.42)에서의 API 요청이 CORS로 차단될 수 있음

---

## 3. 수정 내용

### 3.1. ONVIF 클라이언트 — WS-Security 인증 추가

**파일**: `backend/app/infrastructure/onvif/client.py`

- `_ws_security_header()` 함수 추가: SHA-1 기반 PasswordDigest 생성
- `_inject_ws_header()` 함수 추가: SOAP Envelope에 Security 헤더 삽입
- `_try_get_detail()` 내부 함수로 인증 시도를 분리
- `get_device_detail()`에서 WS-Security → Digest Auth 순으로 폴백

```
인증 시도 순서:
1. WS-Security UsernameToken (Tapo, 일부 Hikvision 지원)
   → 성공 시 반환
2. HTTP Digest Auth (Hikvision 등 전통적 ONVIF 장비)
   → 성공 시 반환
3. 인증 없이 시도 (공개 장비)
```

SOAP Fault 응답에서 `NotAuthorized` 또는 `Sender`를 감지하여 인증 실패를 판별하고, 실패 시 다음 방식으로 폴백한다.

### 3.2. RTSP 전송 프로토콜 — 제조사별 분기

**파일**: `backend/app/domains/camera/application/usecase/update_camera_usecase.py`

ONVIF RTSP 자동 조회(`FetchRtspUrlUseCase`) 시 제조사를 확인하여 TCP 전송이 필요한 카메라에만 `#tcp` 힌트를 RTSP URL에 추가한다.

```python
_TCP_TRANSPORT_MANUFACTURERS = {"tp-link", "tapo"}

def _needs_tcp_transport(manufacturer: str | None) -> bool:
    if not manufacturer:
        return False
    return manufacturer.lower() in _TCP_TRANSPORT_MANUFACTURERS
```

**적용 결과:**

| 제조사 | RTSP URL 예시 |
|--------|---------------|
| Hikvision | `rtsp://admin:pass@192.168.0.93:554/Streaming/Channels/101?...` |
| TP-Link (Tapo) | `rtsp://user:pass@192.168.0.199:554/stream1#tcp` |

`#tcp`는 go2rtc가 해석하는 프래그먼트이며, RTSP 서버에는 전달되지 않으므로 호환성 문제가 없다. go2rtc 외의 클라이언트는 프래그먼트를 무시한다.

### 3.3. 환경설정 경로 수정

**파일**: `backend/app/infrastructure/config/settings.py`

```python
# 변경 전
model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

# 변경 후
model_config = {"env_file": ("../.env", ".env"), "env_file_encoding": "utf-8", "extra": "ignore"}
```

- `("../.env", ".env")`: 부모 디렉토리와 현재 디렉토리 모두 탐색
- `"extra": "ignore"`: 프론트엔드 전용 변수(`NEXT_PUBLIC_*`)로 인한 ValidationError 방지

**파일**: `ai-vms/.env`

```
USE_DATABASE=true   # false → true 변경
```

---

## 4. 영향받는 파일 목록

| 파일 | 변경 유형 |
|------|----------|
| `backend/app/infrastructure/onvif/client.py` | WS-Security 인증 추가 |
| `backend/app/domains/camera/application/usecase/update_camera_usecase.py` | 제조사별 TCP 전송 분기 |
| `backend/app/infrastructure/config/settings.py` | env_file 경로, extra ignore |
| `backend/app/infrastructure/go2rtc/go2rtc_client.py` | 일괄 TCP 적용 시도 후 원복 |
| `.env` | USE_DATABASE=true |

---

## 5. Tapo 카메라 사양 참고

### ONVIF 프로필 매핑 (C500 기준)

| 프로필 | RTSP 경로 | 용도 |
|--------|-----------|------|
| profile_1 | `/stream1` | 메인 스트림 (1280x720 H264) |
| profile_2 | `/stream2` | 서브 스트림 |
| profile_3 | `/stream8` | JPEG 스냅샷 |

### 인증 체계

```
Tapo 앱 → 고급 설정 → 카메라 계정
  └─ ONVIF 인증에도 사용됨
  └─ RTSP 인증에도 사용됨 (같은 계정)
     ※ 별도의 ONVIF 계정 설정은 없음
```

### RTSP 서버 특성

- 서버 배너: `Session streamed by "TP-LINK RTSP Server"`
- 인증 지원: Basic + Digest (`realm="TP-LINK IP-Camera"`)
- TCP 전송 필수: 동일 연결 재인증 거부 (go2rtc `#tcp` 플래그로 해결)
- ONVIF 포트: 2020 (표준 80이 아님)

---

## 6. 향후 추가 카메라 연동 시 참고

새로운 제조사의 카메라가 ONVIF RTSP 자동 조회에 실패할 경우:

1. **ONVIF 인증 실패**: `client.py`의 `_is_soap_fault()` 로그 확인 → WS-Security/Digest 둘 다 실패하면 해당 제조사의 인증 방식 조사 필요
2. **RTSP 인증 실패 (go2rtc "wrong user/pass")**: 해당 카메라의 RTSP 서버가 TCP 전송을 요구하는지 확인 → `_TCP_TRANSPORT_MANUFACTURERS` 셋에 제조사 추가
3. **ONVIF 포트가 80이 아닌 경우**: 카메라 검색(WS-Discovery) 결과의 XAddrs에서 포트를 파싱하여 자동 감지 (현재 구현 완료)
