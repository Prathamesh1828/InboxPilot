from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.limiter import limiter
from app.repositories.audit_repository import get_all_audit_events
from app.schemas.audit import AuditEventResponse

router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
    dependencies=[Depends(get_current_user)],
)

@router.get(
    "",
    response_model=list[AuditEventResponse],
)
@limiter.limit("60/minute")
def read_audit_events(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Get all audit events ordered from newest to oldest.
    """
    return get_all_audit_events(db=db, skip=skip, limit=limit)
