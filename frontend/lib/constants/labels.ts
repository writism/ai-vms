export const severityColors: Record<string, string> = {
  LOW: "bg-blue-100 text-blue-800",
  MEDIUM: "bg-yellow-100 text-yellow-800",
  HIGH: "bg-orange-100 text-orange-800",
  CRITICAL: "bg-red-100 text-red-800",
};

export const dangerLabels: Record<string, string> = {
  FIRE: "화재",
  SMOKE: "연기",
  VIOLENCE: "폭력",
  FIGHT: "싸움",
  WEAPON: "무기",
  FALL: "쓰러짐",
  INTRUSION: "침입",
  FACE_RECOGNIZED: "얼굴 인식",
};

export const eventTypeLabels: Record<string, string> = {
  FACE_RECOGNIZED: "얼굴 인식",
  FACE_UNIDENTIFIED: "미식별 얼굴",
  DANGER_DETECTED: "위험 감지",
  CAMERA_ONLINE: "카메라 온라인",
  CAMERA_OFFLINE: "카메라 오프라인",
  ACCESS_GRANTED: "출입 허용",
  ACCESS_DENIED: "출입 거부",
};

export const dangerEventStatusLabels: Record<string, string> = {
  PENDING: "대기",
  ACKNOWLEDGED: "확인",
  RESOLVED: "해결",
  FALSE_ALARM: "오탐",
};

export const cameraStatusColors: Record<string, string> = {
  ONLINE: "bg-green-500",
  OFFLINE: "bg-gray-400",
  ERROR: "bg-red-500",
};

export const cameraStatusLabels: Record<string, string> = {
  ONLINE: "온라인",
  OFFLINE: "오프라인",
  ERROR: "에러",
};
