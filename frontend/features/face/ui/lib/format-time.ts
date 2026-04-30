/**
 * 밀리초까지 포함한 한국식 타임스탬프
 * 예: 04.30 14:22:05.123
 */
export function formatTimestamp(isoOrDate: string | Date): string {
  const d = typeof isoOrDate === "string" ? new Date(isoOrDate) : isoOrDate;
  const pad2 = (n: number) => String(n).padStart(2, "0");
  const pad3 = (n: number) => String(n).padStart(3, "0");
  const month = pad2(d.getMonth() + 1);
  const day = pad2(d.getDate());
  const h = pad2(d.getHours());
  const m = pad2(d.getMinutes());
  const s = pad2(d.getSeconds());
  const ms = pad3(d.getMilliseconds());
  return `${month}.${day} ${h}:${m}:${s}.${ms}`;
}

/**
 * 시:분:초.밀리초 만 (날짜 없음)
 * 예: 14:22:05.123
 */
export function formatTimeOnly(isoOrDate: string | Date): string {
  const d = typeof isoOrDate === "string" ? new Date(isoOrDate) : isoOrDate;
  const pad2 = (n: number) => String(n).padStart(2, "0");
  const pad3 = (n: number) => String(n).padStart(3, "0");
  return `${pad2(d.getHours())}:${pad2(d.getMinutes())}:${pad2(d.getSeconds())}.${pad3(d.getMilliseconds())}`;
}

/**
 * 날짜 + 시:분 (갤러리 툴팁 등 공간 부족한 곳)
 * 예: 04.30 14:22
 */
export function formatShort(isoOrDate: string | Date): string {
  const d = typeof isoOrDate === "string" ? new Date(isoOrDate) : isoOrDate;
  const pad2 = (n: number) => String(n).padStart(2, "0");
  const month = pad2(d.getMonth() + 1);
  const day = pad2(d.getDate());
  const h = pad2(d.getHours());
  const m = pad2(d.getMinutes());
  return `${month}.${day} ${h}:${m}`;
}
