function _pad2(n: number) { return String(n).padStart(2, "0"); }
function _pad3(n: number) { return String(n).padStart(3, "0"); }
function _parse(v: string | Date) { return typeof v === "string" ? new Date(v) : v; }

/** YYYY-MM-DD HH:mm:ss.mmm */
export function formatTimestamp(isoOrDate: string | Date): string {
  const d = _parse(isoOrDate);
  return (
    `${d.getFullYear()}-${_pad2(d.getMonth() + 1)}-${_pad2(d.getDate())} ` +
    `${_pad2(d.getHours())}:${_pad2(d.getMinutes())}:${_pad2(d.getSeconds())}.${_pad3(d.getMilliseconds())}`
  );
}

/** YYYY-MM-DD HH:mm:ss.mmm (formatTimestamp alias, 얼굴 인식 로그용) */
export function formatTimeOnly(isoOrDate: string | Date): string {
  return formatTimestamp(isoOrDate);
}

/** YYYY-MM-DD HH:mm (공간 부족한 곳) */
export function formatShort(isoOrDate: string | Date): string {
  const d = _parse(isoOrDate);
  return `${d.getFullYear()}-${_pad2(d.getMonth() + 1)}-${_pad2(d.getDate())} ${_pad2(d.getHours())}:${_pad2(d.getMinutes())}`;
}
