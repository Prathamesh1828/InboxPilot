from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user
from app.core.limiter import limiter
from app.models.email import Email
from app.models.user import User
from app.repositories.google_account_repository import get_google_account_by_user
from app.repositories.telegram_connection_repository import get_telegram_connection_by_user_id
from app.repositories.audit_repository import get_all_audit_events

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/stats")
@limiter.limit("60/minute")
def get_dashboard_stats(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get metrics for the dashboard KPI cards, scoped to the current user.
    """
    
    # 1. Scoped KPIs
    emails_processed = db.query(func.count(Email.id)).filter(Email.user_id == current_user.id).scalar() or 0
    
    pending_approvals = (
        db.query(func.count(Email.id))
        .filter(Email.user_id == current_user.id, Email.status == "APPROVAL_PENDING")
        .scalar() or 0
    )
    
    actions_executed = (
        db.query(func.count(Email.id))
        .filter(Email.user_id == current_user.id, Email.status.in_(["EXECUTED", "COMPLETED"]))
        .scalar() or 0
    )
    
    automation_rate = 0
    if emails_processed > 0:
        automation_rate = int((actions_executed / emails_processed) * 100)

    # 2. System Status
    google_account = get_google_account_by_user(db, current_user.id)
    telegram_conn = get_telegram_connection_by_user_id(db, current_user.id)
    
    system_status = {
        "gmail_integration": "Operational" if google_account else "Not Connected",
        "google_calendar": "Operational" if google_account else "Not Connected",
        "telegram": "Operational" if telegram_conn and telegram_conn.connected_at else "Not Connected"
    }
    
    # 3. Recent Activity (Audit logs for user's emails)
    # Get recent audit logs by joining with Email to filter by user_id
    from app.models.audit_event import AuditEvent
    
    recent_events = (
        db.query(AuditEvent, Email.subject, Email.sender, Email.status, Email.category)
        .join(Email, AuditEvent.email_id == Email.id)
        .filter(Email.user_id == current_user.id)
        .order_by(AuditEvent.created_at.desc())
        .limit(100)
        .all()
    )
    
    recent_activity = []
    seen_email_ids = set()
    
    for event, subject, sender, email_status, category in recent_events:
        if event.email_id in seen_email_ids:
            continue
            
        seen_email_ids.add(event.email_id)
        
        # Generate clear, human-readable titles and descriptions
        title = "Email processed"
        desc = "Workflow completed"
        
        # If the email is pending human approval and the event is workflow completion
        if email_status == "APPROVAL_PENDING" or event.event_type == "APPROVAL_REQUESTED":
            title = "Approval required"
            desc = f"Action proposed: {event.action.replace('_', ' ').capitalize() if event.action else 'Review required'}"
        elif event.event_type == "ACTION_APPROVED":
            title = "Action approved"
            desc = "Execution initiated"
        elif event.event_type == "ACTION_REJECTED":
            title = "Action rejected"
            desc = "Workflow cancelled by user"
        elif email_status == "FAILED" or event.event_type == "EXECUTION_FAILED" or event.status == "FAILED":
            title = "Processing failed"
            desc = "An error occurred during workflow execution"
        elif event.event_type == "EXECUTION_COMPLETED" or (event.event_type == "WORKFLOW_COMPLETED" and email_status in ["PROCESSED", "EXECUTED"]):
            title = "Action completed"
            if event.action == "NO_ACTION" or event.action == "ARCHIVE":
                title = "No action required"
                desc = "Email archived" if event.action == "ARCHIVE" else "Processing complete"
            else:
                desc = f"Action: {event.action.replace('_', ' ').capitalize()}" if event.action else "Execution successful"
        elif event.action == "NO_ACTION" or event.action == "ARCHIVE":
            title = "No action required"
            desc = "Email archived" if event.action == "ARCHIVE" else "Processing complete"
        
        recent_activity.append({
            "id": event.id,
            "title": title,
            "description": desc,
            "email_subject": subject or "(No Subject)",
            "email_sender": sender,
            "email_category": category,
            "status": event.status or "INFO",
            "email_id": event.email_id,
            "created_at": event.created_at.isoformat(),
            "event_type": event.event_type
        })
        
        if len(recent_activity) >= 8:
            break

    return {
        "emails_processed": emails_processed,
        "pending_approvals": pending_approvals,
        "actions_executed": actions_executed,
        "automation_rate": automation_rate,
        "system_status": system_status,
        "recent_activity": recent_activity
    }
