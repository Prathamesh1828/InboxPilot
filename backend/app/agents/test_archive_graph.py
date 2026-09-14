from app.agents.graph import build_planning_graph
from app.agents.state import InboxPilotState
from app.db.database import SessionLocal
from app.models.email import Email
from app.schemas.action_plan import ActionType
from app.schemas.classification import (
    EmailCategory,
    EmailClassification,
)


TEST_MESSAGE_ID = "1a0a07274f6eb500"


def main() -> None:
    print("Testing InboxPilot Archive LangGraph")
    print("=" * 60)

    db = SessionLocal()

    try:
        email = (
            db.query(Email)
            .filter(
                Email.provider_message_id == TEST_MESSAGE_ID
            )
            .first()
        )

        if email is None:
            raise RuntimeError(
                "Archive test email was not found in the database."
            )

        state = InboxPilotState(
            email_id=email.id,
            subject=email.subject,
            body=email.body,
            classification=EmailClassification(
                category=EmailCategory.OTHER,
                confidence=0.98,
                reasoning=(
                    "The email is a test message intended "
                    "to verify automatic archive execution."
                ),
            ),
        )

        graph = build_planning_graph(db)

        print()
        print("Running graph...")
        print()

        result = graph.invoke(state)

        print("GRAPH RESULT")
        print("-" * 60)

        action_plan = result.get("action_plan")

        if action_plan is None:
            raise AssertionError(
                "Graph did not produce an action plan."
            )

        print(f"Action:             {action_plan.action}")
        print(f"Parameters:         {action_plan.parameters}")
        print(f"Risk level:         {action_plan.risk_level}")
        print(
            f"Requires approval:  "
            f"{action_plan.requires_approval}"
        )

        print(
            f"Workflow status:    "
            f"{result.get('workflow_status')}"
        )

        print(
            f"Execution result:   "
            f"{result.get('execution_result')}"
        )

        if action_plan.action != ActionType.ARCHIVE:
            raise AssertionError(
                f"Expected ARCHIVE action, got "
                f"{action_plan.action}."
            )

        if action_plan.requires_approval:
            raise AssertionError(
                "ARCHIVE should not require approval."
            )

        if result.get("workflow_status") != "EXECUTED":
            raise AssertionError(
                "Archive action was not executed."
            )

        execution_result = result.get("execution_result")

        if execution_result is None:
            raise AssertionError(
                "No execution result was returned."
            )

        if "Email archived successfully" not in execution_result:
            raise AssertionError(
                "Gmail archive execution did not succeed."
            )

        print()
        print("ARCHIVE GRAPH VERIFICATION")
        print("-" * 60)
        print("ARCHIVE action selected.")
        print("Safety policy allowed automatic execution.")
        print("ActionExecutor executed the archive.")
        print("Gmail archive completed successfully.")

        print()
        print("Archive graph test passed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()