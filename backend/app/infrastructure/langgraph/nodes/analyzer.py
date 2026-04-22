import logging

from app.infrastructure.langgraph.state import AgentState, AnalysisResult

logger = logging.getLogger(__name__)

DANGER_SEVERITY = {
    "FIRE": 0.9,
    "SMOKE": 0.7,
    "WEAPON": 0.95,
    "VIOLENCE": 0.8,
    "FIGHT": 0.75,
    "FALL": 0.6,
    "INTRUSION": 0.85,
}


async def analyzer_node(state: AgentState) -> AgentState:
    detections = state.get("detection_results", [])

    face_names: list[str] = []
    danger_types: list[str] = []
    max_severity = 0.0

    for det in detections:
        if det.type == "face" and det.identity_name:
            face_names.append(det.identity_name)
        elif det.type == "danger":
            danger_types.append(det.label)
            sev = DANGER_SEVERITY.get(det.label, 0.5) * det.confidence
            max_severity = max(max_severity, sev)

    requires_alert = max_severity >= 0.5

    parts: list[str] = []
    if face_names:
        parts.append(f"인식된 인물: {', '.join(face_names)}")
    if danger_types:
        parts.append(f"위험 감지: {', '.join(danger_types)}")
    if not parts:
        parts.append("이상 없음")

    analysis = AnalysisResult(
        summary=" / ".join(parts),
        severity=max_severity,
        recognized_faces=face_names,
        danger_types=danger_types,
        requires_alert=requires_alert,
    )

    logger.info("Analyzer: severity=%.2f, alert=%s", max_severity, requires_alert)

    return {**state, "analysis": analysis, "severity": max_severity}
