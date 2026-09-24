from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.limiter import limiter
from app.repositories.audit_repository import get_all_audit_events
from app.schemas.audit import AuditEventResponse
from fastapi.responses import StreamingResponse
import asyncio
from app.core.redis import redis_client
from app.models.user import User
from datetime import datetime

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
    event_type: str | None = None,
    action: str | None = None,
    status: str | None = None,
    search: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all audit events ordered from newest to oldest for the current user.
    """
    return get_all_audit_events(
        db=db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit,
        event_type=event_type,
        action=action,
        status=status,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )

@router.get("/stream")
async def stream_audit_events(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Stream real-time audit events for the current user using Server-Sent Events (SSE).
    """
    async def event_generator():
        pubsub = redis_client.pubsub()
        channel = f"audit_logs:{current_user.id}"
        pubsub.subscribe(channel)
        
        try:
            # Yield initial connection success to establish stream
            yield f"event: connected\\ndata: {{\"status\": \"connected\"}}\\n\\n"
            
            while True:
                if await request.is_disconnected():
                    break
                    
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=0)
                if message and message['type'] == 'message':
                    data = message['data']
                    yield f"event: audit_log\\ndata: {data}\\n\\n"
                
                # Check for new messages periodically without blocking event loop
                await asyncio.sleep(0.5)
        except Exception:
            pass
        finally:
            pubsub.unsubscribe(channel)
            pubsub.close()
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

