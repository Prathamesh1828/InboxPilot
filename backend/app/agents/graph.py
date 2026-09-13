from langgraph.graph import END, START, StateGraph

from app.agents.nodes import (
    approval_node,
    execute_node,
    planning_node,
    route_after_safety,
    safety_node,
)
from app.agents.state import InboxPilotState


def build_planning_graph():
    """
    Build the InboxPilot planning and safety graph.
    """

    graph = StateGraph(InboxPilotState)

    graph.add_node(
        "plan",
        planning_node,
    )

    graph.add_node(
        "safety",
        safety_node,
    )

    graph.add_node(
        "execute",
        execute_node,
    )

    graph.add_node(
        "approval",
        approval_node,
    )

    graph.add_edge(
        START,
        "plan",
    )

    graph.add_edge(
        "plan",
        "safety",
    )

    graph.add_conditional_edges(
        "safety",
        route_after_safety,
        {
            "execute": "execute",
            "approval": "approval",
        },
    )

    graph.add_edge(
        "execute",
        END,
    )

    graph.add_edge(
        "approval",
        END,
    )

    return graph.compile()