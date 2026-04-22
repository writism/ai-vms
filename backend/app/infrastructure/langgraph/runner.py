import logging

from app.infrastructure.langgraph.state import AgentState

logger = logging.getLogger(__name__)

_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        from app.infrastructure.langgraph.graph_builder import build_agent_graph
        _compiled_graph = build_agent_graph()
    return _compiled_graph


async def run_analysis(camera_id: str, frame_data: bytes | None = None) -> AgentState:
    graph = get_graph()

    initial_state: AgentState = {
        "camera_id": camera_id,
        "frame_data": frame_data,
        "detection_results": [],
        "analysis": None,
        "actions": [],
        "severity": 0.0,
        "error": None,
    }

    logger.info("Running agent pipeline for camera %s", camera_id)
    result = await graph.ainvoke(initial_state)
    logger.info(
        "Pipeline complete: severity=%.2f, actions=%d",
        result.get("severity", 0),
        len(result.get("actions", [])),
    )
    return result
