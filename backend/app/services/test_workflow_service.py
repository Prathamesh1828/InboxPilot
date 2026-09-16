from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.email import Email
from app.services.workflow_service import WorkflowService


def test_workflow_service():
    print("Testing InboxPilot workflow service")
    print("=" * 60)

    db: Session = SessionLocal()

    try:
        email = (
            db.query(Email)
            .filter(Email.status == "CLASSIFIED")
            .order_by(Email.id.desc())
            .first()
        )

        if email is None:
            raise RuntimeError("No CLASSIFIED email found in database.")

        print(f"Email ID:       {email.id}")
        print(f"Subject:        {email.subject}")
        print(f"Category:       {email.category}")
        print(f"Confidence:     {email.classification_confidence}")
        print(f"Status:         {email.status}")
        print()

        print("Sending classified email to workflow...")
        print()

        service = WorkflowService()

        result = service.process_email(
            db=db,
            email_id=email.id,
        )

        print("=" * 60)
        print("WORKFLOW RESULT")
        print("=" * 60)

        print(f"Workflow status: {result.workflow_status}")

        if result.classification:
            print(f"Category:        {result.classification.category}")
            print(f"Confidence:      {result.classification.confidence}")

        if result.action_plan:
            print(f"Action:          {result.action_plan.action}")
            print(f"Risk level:      {result.action_plan.risk_level}")
            print(f"Approval needed: {result.action_plan.requires_approval}")

        if result.approval_id:
            print(f"Approval ID:     {result.approval_id}")

        if result.execution_result:
            print(f"Execution result: {result.execution_result}")

        if result.error:
            print(f"Error:            {result.error}")

        print()
        print("✅ Workflow service test completed")

    finally:
        db.close()


if __name__ == "__main__":
    test_workflow_service()