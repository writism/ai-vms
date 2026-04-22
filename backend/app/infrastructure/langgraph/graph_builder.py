from langgraph.graph import END, StateGraph

from app.infrastructure.langgraph.nodes.analyzer import analyzer_node
from app.infrastructure.langgraph.nodes.detector import detector_node
from app.infrastructure.langgraph.nodes.dispatcher import dispatcher_node
from app.infrastructure.langgraph.nodes.planner import planner_node
from app.infrastructure.langgraph.state import AgentState


def should_dispatch(state: AgentState) -> str:
    analysis = state.get("analysis")
    if analysis and (analysis.requires_alert or analysis.recognized_faces):
        return "dispatcher"
    return "end"


def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("detector", detector_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("dispatcher", dispatcher_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "detector")
    graph.add_edge("detector", "analyzer")
    graph.add_conditional_edges(
        "analyzer",
        should_dispatch,
        {"dispatcher": "dispatcher", "end": END},
    )
    graph.add_edge("dispatcher", END)

    return graph.compile()
