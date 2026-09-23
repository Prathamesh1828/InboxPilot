from datetime import datetime

from pydantic import BaseModel


class ApprovalResponse(BaseModel):
    id: int
    email_id: int
    email_subject: str | None = None
    email_sender: str | None = None
    action: str
    action_plan: dict
    status: str
    created_at: datetime
    resolved_at: datetime | None

    model_config = {
        "from_attributes": True
    }