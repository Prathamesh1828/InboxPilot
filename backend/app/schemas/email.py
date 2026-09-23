from datetime import datetime

from pydantic import BaseModel


class EmailCreate(BaseModel):
    provider_message_id: str
    thread_id: str | None = None
    sender: str
    recipients: list[str]
    subject: str | None = None
    body: str
    received_at: datetime


class EmailResponse(BaseModel):
    id: int
    user_id: str | None
    provider_message_id: str
    thread_id: str | None
    sender: str
    subject: str | None
    recipients: list[str]
    body: str

    received_at: datetime
    processed_at: datetime | None
    created_at: datetime

    # Processing status
    status: str

    # AI classification
    category: str | None
    classification_confidence: float | None
    classification_reasoning: str | None
    classified_at: datetime | None

    model_config = {
        "from_attributes": True
    }


class PaginatedEmailResponse(BaseModel):
    items: list[EmailResponse]
    total: int
    page: int
    size: int


class EmailDetailResponse(EmailResponse):
    """Extended email schema with complete AI workflow state"""
    
    # Action Plan details (from PLAN_CREATED or SAFETY_EVALUATED audit events)
    action_plan: dict | None = None
    
    # Safety
    safety_result: dict | None = None
    
    # Execution
    execution_result: dict | None = None
    error_message: str | None = None
    
    # Approval
    approval_id: int | None = None
    approval_status: str | None = None