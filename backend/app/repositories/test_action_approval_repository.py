from app.db.database import SessionLocal

from app.repositories.action_approval_repository import (
    create_action_approval,
    get_action_approval,
    get_pending_approval_by_email_id,
    update_action_approval_status,
)


def main() -> None:
    print("Testing Action Approval Repository")
    print("=" * 60)

    db = SessionLocal()

    try:
        approval = create_action_approval(
            db=db,
            email_id=2,
            action="DRAFT_REPLY",
            action_plan={
                "action": "DRAFT_REPLY",
                "parameters": {
                    "reply_text": "Thank you for your email."
                },
                "reasoning": "A reply draft requires user approval.",
                "confidence": 0.95,
                "risk_level": "MEDIUM",
                "requires_approval": True,
            },
        )

        print()
        print("CREATED APPROVAL")
        print("-" * 60)
        print(f"ID:       {approval.id}")
        print(f"Email ID: {approval.email_id}")
        print(f"Action:   {approval.action}")
        print(f"Status:   {approval.status}")

        fetched = get_action_approval(
            db=db,
            approval_id=approval.id,
        )

        print()
        print("FETCHED APPROVAL")
        print("-" * 60)
        print(f"ID:       {fetched.id if fetched else None}")
        print(f"Status:   {fetched.status if fetched else None}")

        pending = get_pending_approval_by_email_id(
            db=db,
            email_id=2,
        )

        print()
        print("PENDING APPROVAL")
        print("-" * 60)
        print(f"ID:       {pending.id if pending else None}")
        print(f"Status:   {pending.status if pending else None}")

        updated = update_action_approval_status(
            db=db,
            approval_id=approval.id,
            status="APPROVED",
        )

        print()
        print("UPDATED APPROVAL")
        print("-" * 60)
        print(f"ID:       {updated.id if updated else None}")
        print(f"Status:   {updated.status if updated else None}")
        print(f"Resolved: {updated.resolved_at if updated else None}")

    finally:
        db.close()


if __name__ == "__main__":
    main()