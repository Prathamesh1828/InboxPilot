from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.action_approval_repository import (
    get_action_approval,
    get_pending_approvals,
)
from app.schemas.approval import ApprovalResponse
from app.services.approval_execution_service import (
    ApprovalExecutionService,
)
from app.services.approval_service import ApprovalService


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


# ---------------------------------------------------------
# GET PENDING APPROVALS
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[ApprovalResponse],
)
def read_pending_approvals(
    db: Session = Depends(get_db),
):
    """
    Get all pending human approval requests.
    """

    return get_pending_approvals(
        db=db,
    )


# ---------------------------------------------------------
# GET SINGLE APPROVAL
# ---------------------------------------------------------

@router.get(
    "/{approval_id}",
    response_model=ApprovalResponse,
)
def read_approval(
    approval_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a single approval request.
    """

    approval = get_action_approval(
        db=db,
        approval_id=approval_id,
    )

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval not found",
        )

    return approval


# ---------------------------------------------------------
# APPROVE AND EXECUTE
# ---------------------------------------------------------

@router.post(
    "/{approval_id}/approve",
)
def approve_action(
    approval_id: int,
    db: Session = Depends(get_db),
):
    """
    Approve a pending action and execute it.

    Flow:

        PENDING
           ↓
        APPROVED
           ↓
        Re-validation
           ↓
        Safety check
           ↓
        Execution
    """

    try:
        # ---------------------------------------------
        # 1. Human approval
        # ---------------------------------------------

        ApprovalService.approve(
            db=db,
            approval_id=approval_id,
        )

        # ---------------------------------------------
        # 2. Execute approved action
        # ---------------------------------------------

        execution_result = (
            ApprovalExecutionService.execute_approved(
                db=db,
                approval_id=approval_id,
            )
        )

        return {
            "approval_id": approval_id,
            "status": "APPROVED",
            "message": "Action approved and executed successfully.",
            "execution_result": execution_result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------
# REJECT
# ---------------------------------------------------------

@router.post(
    "/{approval_id}/reject",
)
def reject_action(
    approval_id: int,
    db: Session = Depends(get_db),
):
    """
    Reject a pending action.

    Rejected actions are not executed.
    """

    try:
        message = ApprovalService.reject(
            db=db,
            approval_id=approval_id,
        )

        return {
            "approval_id": approval_id,
            "status": "REJECTED",
            "message": message,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc