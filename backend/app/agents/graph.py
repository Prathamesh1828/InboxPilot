from langgraph.graph import END, START, StateGraph

from app.agents.nodes import planning_node
from app.agents.state import InboxPilotState


def build_planning_graph():
    """
    Build the initial InboxPilot planning graph.
    """

    graph = StateGraph(InboxPilotState)

    graph.add_node(
        "plan",
        planning_node,
    )

    graph.add_edge(
        START,
        "plan",
    )

    graph.add_edge(
        "plan",
        END,
    )

    return graph.compile()