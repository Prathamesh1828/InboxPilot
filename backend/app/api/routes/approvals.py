from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_api_key
from app.core.limiter import limiter
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
    dependencies=[Depends(get_api_key)],
)


# ---------------------------------------------------------
# GET PENDING APPROVALS
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[ApprovalResponse],
)
@limiter.limit("60/minute")
def read_pending_approvals(
    request: Request,
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
@limiter.limit("60/minute")
def read_approval(
    request: Request,
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
@limiter.limit("20/minute")
def approve_action(
    request: Request,
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
            "status": "EXECUTED",
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
@limiter.limit("20/minute")
def reject_action(
    request: Request,
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