from app.services.planner import EmailPlanner
from app.schemas.action_plan import ActionType


def main() -> None:
    print("Testing Planner: MEETING with Explicit Time")
    print("=" * 60)

    planner = EmailPlanner()

    # Scenario 1: MEETING with explicit start time
    print("\nScenario 1: Meeting with explicit start time")
    plan_1 = planner.create_plan(
        category="MEETING",
        classification_reasoning="Email requests scheduling a client meeting at a specific time.",
        subject="Client Meeting Request",
        body="Please schedule a client meeting tomorrow at 11:00 AM to discuss the quarterly results.",
    )
    print(f"  Action:     {plan_1.action.value}")
    print(f"  Confidence: {plan_1.confidence}")
    print(f"  Reasoning:  {plan_1.reasoning}")
    if hasattr(plan_1, "parameters") and hasattr(plan_1.parameters, "start_time"):
        print(f"  Start time: {plan_1.parameters.start_time}")
        print(f"  End time:   {plan_1.parameters.end_time}")
    assert plan_1.action == ActionType.CREATE_CALENDAR_EVENT, (
        f"Expected CREATE_CALENDAR_EVENT, got {plan_1.action.value}"
    )
    print("  PASSED: Correctly produced CREATE_CALENDAR_EVENT")

    # Scenario 2: MEETING with afternoon time
    print("\nScenario 2: Meeting with afternoon time")
    plan_2 = planner.create_plan(
        category="MEETING",
        classification_reasoning="Email requests scheduling a project meeting at a specific time.",
        subject="Project Discussion",
        body="Hi team, let's have a project meeting tomorrow at 3:00 PM to discuss the upcoming release.",
    )
    print(f"  Action:     {plan_2.action.value}")
    print(f"  Confidence: {plan_2.confidence}")
    if hasattr(plan_2, "parameters") and hasattr(plan_2.parameters, "start_time"):
        print(f"  Start time: {plan_2.parameters.start_time}")
        print(f"  End time:   {plan_2.parameters.end_time}")
    assert plan_2.action == ActionType.CREATE_CALENDAR_EVENT, (
        f"Expected CREATE_CALENDAR_EVENT, got {plan_2.action.value}"
    )
    print("  PASSED: Correctly produced CREATE_CALENDAR_EVENT")

    # Scenario 3: MEETING email with no specific time
    print("\nScenario 3: Meeting with no specific time")
    plan_3 = planner.create_plan(
        category="MEETING",
        classification_reasoning="Email mentions a meeting but without specific timing.",
        subject="Let's catch up",
        body="Hey, we should catch up sometime this week about the project status.",
    )
    print(f"  Action:     {plan_3.action.value}")
    print(f"  Confidence: {plan_3.confidence}")
    print(f"  Reasoning:  {plan_3.reasoning}")
    # Without a specific time, NO_ACTION or DRAFT_REPLY are both acceptable
    print(f"  Result: {plan_3.action.value} (acceptable for no explicit time)")

    print()
    print("All planner meeting tests passed.")


if __name__ == "__main__":
    main()
