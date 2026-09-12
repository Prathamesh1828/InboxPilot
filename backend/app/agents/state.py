from pydantic import BaseModel

from app.schemas.action_plan import ActionPlan
from app.schemas.classification import EmailClassification


class InboxPilotState(BaseModel):
    email_id: int | None = None

    subject: str | None = None

    body: str = ""

    classification: EmailClassification | None = None

    action_plan: ActionPlan | None = None

    workflow_status: str = "START"

    error: str | None = None