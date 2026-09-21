from sqlalchemy.orm import Session

from app.agents.state import InboxPilotState
from app.repositories.action_approval_repository import (
    create_action_approval,
    get_pending_approval_by_email_id,
)
from app.services.action_safety import evaluate_action_safety
from app.services.executor import ActionExecutor
from app.services.parameter_grounding import validate_action_parameters
from app.services.planner import EmailPlanner
from app.repositories.audit_repository import log_audit_event


def planning_node(
    state: InboxPilotState,
    db: Session,
) -> dict:
    """
    Create an action plan for the classified email.
    """

    classification = state.classification

    if classification is None:
        raise ValueError(
            "Classification is required before planning"
        )

    planner = EmailPlanner()

    action_plan = planner.create_plan(
        category=classification.category.value,
        classification_reasoning=classification.reasoning,
        subject=state.subject,
        body=state.body,
    )
    
    log_audit_event(
        db=db,
        # pyrefly: ignore [bad-argument-type]
        email_id=state.email_id,
        event_type="PLAN_CREATED",
        action=action_plan.action.value,
        details={
            "risk_level": action_plan.risk_level.value,
            "requires_approval": action_plan.requires_approval,
            "parameters": action_plan.parameters,
        }
    )

    return {
        "action_plan": action_plan,
        "workflow_status": "PLANNED",
    }


def grounding_node(
    state: InboxPilotState,
    db: Session,
) -> dict:
    """
    Validate that important action parameters
    are grounded in the original email.
    """

    action_plan = state.action_plan

    if action_plan is None:
        raise ValueError(
            "Action plan is required before grounding"
        )

    errors = validate_action_parameters(
        plan=action_plan,
        subject=state.subject,
        body=state.body,
        reference_time=state.received_at,
    )

    if errors:
        log_audit_event(
            db=db,
            # pyrefly: ignore [bad-argument-type]
            email_id=state.email_id,
            event_type="GROUNDING_FAILED",
            action=action_plan.action.value,
            details={"grounding_errors": errors},
        )
        return {
            "grounding_errors": errors,
            "workflow_status": "GROUNDING_FAILED",
        }

    log_audit_event(
        db=db,
        # pyrefly: ignore [bad-argument-type]
        email_id=state.email_id,
        event_type="GROUNDING_PASSED",
        action=action_plan.action.value,
    )

    return {
        "grounding_errors": [],
        "workflow_status": "GROUNDED",
    }


def route_after_grounding(
    state: InboxPilotState,
) -> str:
    """
    Decide whether the workflow can continue
    to safety evaluation after grounding.
    """

    if state.grounding_errors:
        return "review"

    return "safety"


def safety_node(
    state: InboxPilotState,
    db: Session,
) -> dict:
    """
    Apply the deterministic safety policy
    to the proposed action plan.
    """

    action_plan = state.action_plan

    if action_plan is None:
        raise ValueError(
            "Action plan is required before safety evaluation"
        )

    safe_plan = evaluate_action_safety(action_plan)
    
    log_audit_event(
        db=db,
        # pyrefly: ignore [bad-argument-type]
        email_id=state.email_id,
        event_type="SAFETY_EVALUATED",
        action=safe_plan.action.value,
        details={
            "risk_level": safe_plan.risk_level.value,
            "requires_approval": safe_plan.requires_approval,
        },
    )

    return {
        "action_plan": safe_plan,
        "workflow_status": "SAFETY_EVALUATED",
    }


def route_after_safety(
    state: InboxPilotState,
) -> str:
    """
    Decide where the workflow should go
    after safety evaluation.
    """

    action_plan = state.action_plan

    if action_plan is None:
        raise ValueError(
            "Action plan is required for routing"
        )

    if action_plan.requires_approval:
        return "approval"

    return "execute"


def execute_node(
    state: InboxPilotState,
    db: Session,
) -> dict:
    """
    Execute a safe action through the ActionExecutor.
    """

    action_plan = state.action_plan

    if action_plan is None:
        raise ValueError(
            "Action plan is required before execution"
        )

    if state.email_id is None:
        raise ValueError(
            "Email ID is required before execution"
        )

    executor = ActionExecutor()

    log_audit_event(
        db=db,
        email_id=state.email_id,
        event_type="EXECUTION_STARTED",
        action=action_plan.action.value,
    )

    try:
        result = executor.execute(
            plan=action_plan,
            db=db,
            email_id=state.email_id,
        )
        
        log_audit_event(
            db=db,
            email_id=state.email_id,
            event_type="EXECUTION_COMPLETED",
            action=action_plan.action.value,
            details={"execution_result": result},
        )
        
        return {
            "workflow_status": "EXECUTED",
            "execution_result": result,
        }
    except Exception as exc:
        log_audit_event(
            db=db,
            email_id=state.email_id,
            event_type="EXECUTION_FAILED",
            action=action_plan.action.value,
            details={"error": str(exc)},
        )
        raise


def approval_node(
    state: InboxPilotState,
    db: Session,
) -> dict:
    """
    Create a persistent approval request for
    actions that require human approval.
    """

    action_plan = state.action_plan

    if action_plan is None:
        raise ValueError(
            "Action plan is required before requesting approval"
        )

    if state.email_id is None:
        raise ValueError(
            "Email ID is required before requesting approval"
        )

    existing_approval = get_pending_approval_by_email_id(
        db=db,
        email_id=state.email_id,
    )

    if existing_approval is not None:
        return {
            "approval_id": existing_approval.id,
            "workflow_status": "APPROVAL_PENDING",
        }

    approval = create_action_approval(
        db=db,
        email_id=state.email_id,
        action=action_plan.action.value,
        action_plan=action_plan.model_dump(mode="json"),
    )
    
    log_audit_event(
        db=db,
        email_id=state.email_id,
        approval_id=approval.id,
        event_type="APPROVAL_CREATED",
        action=action_plan.action.value,
    )

    from app.integrations.telegram.bot import send_approval_notification
    from app.repositories.telegram_connection_repository import get_telegram_connection_by_user_id
    from app.models.google_account import GoogleAccount
    from app.models.email import Email
    
    try:
        # In the single-user setup, the user_id corresponds to the first GoogleAccount
        account = db.query(GoogleAccount).first()
        if account:
            connection = get_telegram_connection_by_user_id(db, user_id=int(account.id)) # type: ignore
            if connection and connection.telegram_chat_id:
                email_record = db.query(Email).get(state.email_id)
                gmail_thread_id = email_record.thread_id if email_record else None
                gmail_message_id = email_record.provider_message_id if email_record else None
                
                send_approval_notification(
                    chat_id=str(connection.telegram_chat_id), # type: ignore
                    approval_id=approval.id,
                    action=action_plan.action.value,
                    email_subject=state.subject,
                    risk_level=action_plan.risk_level.value,
                    gmail_thread_id=gmail_thread_id,
                    gmail_message_id=gmail_message_id,
                )
    except Exception as telegram_exc:
        import logging
        logging.getLogger(__name__).error(
            "Telegram notification failed for approval %d (non-fatal): %s",
            approval.id,
            telegram_exc,
        )

    return {
        "approval_id": approval.id,
        "workflow_status": "APPROVAL_PENDING",
    }


def review_node(
    state: InboxPilotState,
) -> dict:
    """
    Handle an action plan that failed grounding.

    No external action is performed.
    """

    return {
        "workflow_status": "GROUNDING_REVIEW",
    }