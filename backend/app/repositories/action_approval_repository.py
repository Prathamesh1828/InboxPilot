from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.action_approval import ActionApproval


def create_action_approval(
    db: Session,
    email_id: int,
    action: str,
    action_plan: dict,
) -> ActionApproval:
    approval = ActionApproval(
        email_id=email_id,
        action=action,
        action_plan=action_plan,
        status="PENDING",
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    return approval


def get_action_approval(
    db: Session,
    approval_id: int,
) -> ActionApproval | None:
    return (
        db.query(ActionApproval)
        .filter(ActionApproval.id == approval_id)
        .first()
    )


def get_pending_approval_by_email_id(
    db: Session,
    email_id: int,
) -> ActionApproval | None:
    return (
        db.query(ActionApproval)
        .filter(
            ActionApproval.email_id == email_id,
            ActionApproval.status == "PENDING",
        )
        .first()
    )

def get_pending_approvals(
    db: Session,
) -> list[ActionApproval]:
    """
    Return all pending approval requests.

    Newest approval requests are returned first.
    """

    return (
        db.query(ActionApproval)
        .filter(
            ActionApproval.status == "PENDING"
        )
        .order_by(
            ActionApproval.created_at.desc()
        )
        .all()
    )


def update_action_approval_status(
    db: Session,
    approval_id: int,
    status: str,
) -> ActionApproval | None:
    approval = get_action_approval(
        db=db,
        approval_id=approval_id,
    )

    if approval is None:
        return None

    approval.status = status
    approval.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(approval)



    return approval


def atomic_transition_status(
    db: Session,
    approval_id: int,
    from_status: str,
    to_status: str,
) -> bool:
    """
    Atomically transition an approval from one status to another.

    Uses a single filtered UPDATE so only one caller wins
    when two requests race on the same approval.

    Returns True if the transition succeeded, False if the
    approval was not in the expected from_status.
    """

    rows_updated = (
        db.query(ActionApproval)
        .filter(
            ActionApproval.id == approval_id,
            ActionApproval.status == from_status,
        )
        .update(
            {
                "status": to_status,
                "resolved_at": datetime.now(timezone.utc),
            },
            synchronize_session="fetch",
        )
    )

    db.commit()

    return rows_updated > 0