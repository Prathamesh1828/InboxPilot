from enum import Enum

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    LOG_BILL = "LOG_BILL"
    CREATE_CALENDAR_EVENT = "CREATE_CALENDAR_EVENT"
    CREATE_REMINDER = "CREATE_REMINDER"
    DRAFT_REPLY = "DRAFT_REPLY"
    ARCHIVE = "ARCHIVE"
    NO_ACTION = "NO_ACTION"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ActionPlan(BaseModel):
    action: ActionType

    parameters: dict[str, str | int | float | bool | None] = Field(
        default_factory=dict
    )

    reasoning: str = Field(
        min_length=1,
        max_length=1000,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    risk_level: RiskLevel

    requires_approval: bool