from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


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


class BillParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(gt=0)
    currency: str = Field(min_length=1, max_length=10)
    vendor: str | None = Field(
        default=None,
        max_length=255,
    )
    due_date: str | None = None


class ReminderParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reminder_text: str = Field(
        min_length=1,
        max_length=500,
    )
    reminder_date: str | None = None


class CalendarEventParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=1,
        max_length=255,
    )
    start_time: str | None = None
    end_time: str | None = None
    description: str | None = None


class DraftReplyParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reply_text: str = Field(
        min_length=1,
        max_length=5000,
    )


class ArchiveParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str | None = None


class NoActionParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BillActionPlan(BaseModel):
    action: Literal[ActionType.LOG_BILL]
    parameters: BillParameters
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


class ReminderActionPlan(BaseModel):
    action: Literal[ActionType.CREATE_REMINDER]
    parameters: ReminderParameters
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


class CalendarActionPlan(BaseModel):
    action: Literal[ActionType.CREATE_CALENDAR_EVENT]
    parameters: CalendarEventParameters
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


class DraftReplyActionPlan(BaseModel):
    action: Literal[ActionType.DRAFT_REPLY]
    parameters: DraftReplyParameters
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


class ArchiveActionPlan(BaseModel):
    action: Literal[ActionType.ARCHIVE]
    parameters: ArchiveParameters
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


class NoActionPlan(BaseModel):
    action: Literal[ActionType.NO_ACTION]
    parameters: NoActionParameters = Field(
        default_factory=NoActionParameters
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


ActionPlan = Annotated[
    (
        BillActionPlan
        | ReminderActionPlan
        | CalendarActionPlan
        | DraftReplyActionPlan
        | ArchiveActionPlan
        | NoActionPlan
    ),
    Field(discriminator="action"),
]