from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
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
    dependencies=[Depends(get_current_user)],
)

import html
import logging
from app.models.email import Email
from app.repositories.telegram_connection_repository import get_telegram_connection_by_user_id
from app.integrations.telegram.bot import edit_message_text

logger = logging.getLogger(__name__)

def _sync_telegram_status(db: Session, approval_id: int, status_text: str):
    try:
        approval = get_action_approval(db, approval_id)
        if approval and approval.telegram_message_id:
            email_record = db.query(Email).get(approval.email_id)
            if email_record and email_record.user_id:
                connection = get_telegram_connection_by_user_id(db, user_id=email_record.user_id)
                if connection and connection.telegram_chat_id:
                    subject = email_record.subject or "(No subject)"
                    escaped_subject = html.escape(subject)
                    new_text = (
                        f"🚨 <b>Action Approval Required</b>\n\n"
                        f"<b>Action:</b> {approval.action}\n"
                        f"<b>Email:</b> {escaped_subject}\n\n"
                        f"<b>Status:</b> {status_text}"
                    )
                    edit_message_text(str(connection.telegram_chat_id), approval.telegram_message_id, new_text)
    except Exception as e:
        logger.error("Failed to sync web approval to telegram: %s", e)

# ---------------------------------------------------------
# GET PENDING APPROVALS
# ---------------------------------------------------------

from app.models.user import User

@router.get(
    "",
    response_model=list[ApprovalResponse],
)
@limiter.limit("60/minute")
def read_pending_approvals(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all pending human approval requests for the current user.
    """

    return get_pending_approvals(
        db=db,
        user_id=current_user.id,
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
        # 2. Execute approved action asynchronously
        # ---------------------------------------------
        
        from app.workers.tasks import execute_approved_action
        execute_approved_action.delay(approval_id=approval_id)

        _sync_telegram_status(db, approval_id, "✅ Approved via Web. Executing...")

        return {
            "approval_id": approval_id,
            "status": "APPROVED",
            "message": "Action approved successfully. Execution started.",
            "execution_result": None,
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

        _sync_telegram_status(db, approval_id, "❌ Rejected via Web")

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