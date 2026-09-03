from datetime import datetime

from pydantic import BaseModel


class EmailResponse(BaseModel):
    id: int
    provider_message_id: str
    thread_id: str | None
    sender: str
    subject: str | None
    recipients: list[str]
    body: str
    received_at: datetime
    processed_at: datetime | None
    status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }