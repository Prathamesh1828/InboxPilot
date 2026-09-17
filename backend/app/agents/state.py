from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.action_plan import ActionPlan
from app.schemas.classification import EmailClassification


class InboxPilotState(BaseModel):
    email_id: int | None = None

    subject: str | None = None
    body: str = ""

    # Original email timestamp.
    # Used when grounding relative dates such as
    # "today" and "tomorrow".
    received_at: datetime | None = None

    classification: EmailClassification | None = None

    action_plan: ActionPlan | None = None

    approval_id: int | None = None

    grounding_errors: list[str] = Field(
        default_factory=list
    )

    execution_result: str | None = None

    workflow_status: str = "START"

    error: str | None = None