from sqlalchemy.orm import Session

from app.repositories.action_approval_repository import (
    get_action_approval,
    update_action_approval_status,
)
from app.repositories.email_repository import (
    get_email_by_id,
    update_email_status,
)
from app.repositories.audit_repository import log_audit_event


class ApprovalService:
    """
    Handles human approval and rejection of
    pending InboxPilot actions.
    """

    @staticmethod
    def approve(
        db: Session,
        approval_id: int,
    ) -> str:
        approval = get_action_approval(
            db=db,
            approval_id=approval_id,
        )

        if approval is None:
            raise ValueError(
                f"Approval {approval_id} not found."
            )

        if approval.status not in ("PENDING", "EXECUTION_FAILED"):
            raise ValueError(
                f"Approval {approval_id} is already "
                f"{approval.status}."
            )

        updated = update_action_approval_status(
            db=db,
            approval_id=approval_id,
            status="APPROVED",
        )

        if updated is None:
            raise ValueError(
                f"Failed to approve action {approval_id}."
            )
            
        log_audit_event(
            db=db,
            email_id=approval.email_id,
            approval_id=approval_id,
            event_type="APPROVAL_APPROVED",
            action=approval.action,
        )

        return (
            f"Approval {approval_id} approved successfully."
        )

    @staticmethod
    def reject(
        db: Session,
        approval_id: int,
    ) -> str:
        approval = get_action_approval(
            db=db,
            approval_id=approval_id,
        )

        if approval is None:
            raise ValueError(
                f"Approval {approval_id} not found."
            )

        if approval.status != "PENDING":
            raise ValueError(
                f"Approval {approval_id} is already "
                f"{approval.status}."
            )

        updated = update_action_approval_status(
            db=db,
            approval_id=approval_id,
            status="REJECTED",
        )

        if updated is None:
            raise ValueError(
                f"Failed to reject action {approval_id}."
            )

        log_audit_event(
            db=db,
            email_id=approval.email_id,
            approval_id=approval_id,
            event_type="APPROVAL_REJECTED",
            action=approval.action,
        )
        
        email = get_email_by_id(db, approval.email_id)
        if email:
            update_email_status(db, email, "REJECTED")

        return (
            f"Approval {approval_id} rejected successfully."
        )