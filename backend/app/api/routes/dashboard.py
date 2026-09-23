from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user
from app.core.limiter import limiter
from app.models.email import Email
from app.models.action_approval import ActionApproval
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
        db.query(func.count(ActionApproval.id))
        .join(Email, ActionApproval.email_id == Email.id)
        .filter(Email.user_id == current_user.id, ActionApproval.status == "PENDING")
        .scalar() or 0
    )
    
    actions_executed = (
        db.query(func.count(Email.id))
        .filter(Email.user_id == current_user.id, Email.status == "PROCESSED")
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
        db.query(AuditEvent)
        .join(Email, AuditEvent.email_id == Email.id)
        .filter(Email.user_id == current_user.id)
        .order_by(AuditEvent.created_at.desc())
        .limit(5)
        .all()
    )
    
    recent_activity = []
    for event in recent_events:
        recent_activity.append({
            "id": event.id,
            "event_type": event.event_type,
            "action": event.action,
            "status": event.status,
            "email_id": event.email_id,
            "created_at": event.created_at.isoformat()
        })

    return {
        "emails_processed": emails_processed,
        "pending_approvals": pending_approvals,
        "actions_executed": actions_executed,
        "automation_rate": automation_rate,
        "system_status": system_status,
        "recent_activity": recent_activity
    }
