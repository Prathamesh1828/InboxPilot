from app.agents.nodes import route_after_grounding
from app.agents.state import InboxPilotState


def main() -> None:
    print("Testing grounding router")
    print("=" * 60)

    grounded_state = InboxPilotState(
        grounding_errors=[],
    )

    failed_state = InboxPilotState(
        grounding_errors=[
            "Vendor was not found in email body."
        ],
    )

    grounded_route = route_after_grounding(
        grounded_state
    )

    failed_route = route_after_grounding(
        failed_state
    )

    print()
    print("GROUNDED CASE")
    print("-" * 60)
    print(f"Route: {grounded_route}")

    print()
    print("FAILED CASE")
    print("-" * 60)
    print(f"Route: {failed_route}")


if __name__ == "__main__":
    main()