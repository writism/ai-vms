export function humanizeMediaError(e: unknown): string {
  if (e instanceof DOMException) {
    switch (e.name) {
      case "NotAllowedError":
        return "카메라 권한이 거부되었습니다. 브라우저 사이트 설정에서 허용으로 바꾸세요.";
      case "NotReadableError":
        return "카메라가 다른 프로그램에 사용 중입니다. 해당 앱을 종료한 뒤 다시 시도하세요.";
      case "NotFoundError":
        return "연결된 카메라를 찾지 못했습니다. 카메라를 연결한 뒤 다시 시도하세요.";
      case "SecurityError":
        return "비보안 컨텍스트입니다. https://localhost 로 접속하거나 인증서를 신뢰하세요.";
      case "OverconstrainedError":
        return "요청한 해상도/모드를 지원하는 카메라가 없습니다.";
      default:
        return `카메라 오류: ${e.name}${e.message ? ` (${e.message})` : ""}`;
    }
  }
  return e instanceof Error ? `카메라 오류: ${e.message}` : "카메라에 접근할 수 없습니다";
}
