import logging

from app.infrastructure.langgraph.state import Action, AgentState

logger = logging.getLogger(__name__)


async def dispatcher_node(state: AgentState) -> AgentState:
    analysis = state.get("analysis")
    if analysis is None:
        return state

    actions: list[Action] = []

    if analysis.requires_alert:
        for dtype in analysis.danger_types:
            actions.append(
                Action(
                    type="create_danger_event",
                    target="alert_service",
                    payload={
                        "camera_id": state.get("camera_id", ""),
                        "danger_type": dtype,
                        "severity": state.get("severity", 0.0),
                        "description": analysis.summary,
                    },
                )
            )
            actions.append(
                Action(
                    type="send_notification",
                    target="websocket",
                    payload={
                        "type": "DANGER_DETECTED",
                        "danger_type": dtype,
                        "camera_id": state.get("camera_id", ""),
                        "severity": state.get("severity", 0.0),
                    },
                )
            )

    for face_name in analysis.recognized_faces:
        actions.append(
            Action(
                type="create_event",
                target="event_service",
                payload={
                    "event_type": "FACE_RECOGNIZED",
                    "camera_id": state.get("camera_id", ""),
                    "identity_name": face_name,
                },
            )
        )

    logger.info("Dispatcher: %d actions queued", len(actions))
    return {**state, "actions": actions}
