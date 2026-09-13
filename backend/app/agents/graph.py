from langgraph.graph import END, START, StateGraph

from app.agents.nodes import (
    approval_node,
    execute_node,
    grounding_node,
    planning_node,
    review_node,
    route_after_grounding,
    route_after_safety,
    safety_node,
)
from app.agents.state import InboxPilotState


def build_planning_graph():
    """
    Build the InboxPilot planning, grounding,
    safety, and routing graph.
    """

    graph = StateGraph(InboxPilotState)

    graph.add_node(
        "plan",
        planning_node,
    )

    graph.add_node(
        "grounding",
        grounding_node,
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

    graph.add_node(
        "review",
        review_node,
    )

    graph.add_edge(
        START,
        "plan",
    )

    graph.add_edge(
        "plan",
        "grounding",
    )

    graph.add_conditional_edges(
        "grounding",
        route_after_grounding,
        {
            "safety": "safety",
            "review": "review",
        },
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

    graph.add_edge(
        "review",
        END,
    )

    return graph.compile()