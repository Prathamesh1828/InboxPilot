from sqlalchemy.orm import Session

from app.repositories.action_approval_repository import (
    get_action_approval,
    update_action_approval_status,
)


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

        if approval.status != "PENDING":
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

        return (
            f"Approval {approval_id} rejected successfully."
        )