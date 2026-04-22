import logging

from app.infrastructure.langgraph.state import AgentState

logger = logging.getLogger(__name__)


async def planner_node(state: AgentState) -> AgentState:
    camera_id = state.get("camera_id")
    if not camera_id:
        return {**state, "error": "No camera_id provided"}

    logger.info("Planner: analyzing camera %s", camera_id)

    return {
        **state,
        "detection_results": [],
        "actions": [],
        "analysis": None,
        "error": None,
    }
