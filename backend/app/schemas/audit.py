from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email_id: int
    approval_id: int | None
    event_type: str
    action: str | None
    status: str | None
    details: dict | None
    created_at: datetime
