from enum import Enum

from pydantic import BaseModel, Field


class EmailCategory(str, Enum):
    BILL = "BILL"
    MEETING = "MEETING"
    FORM = "FORM"
    REMINDER = "REMINDER"
    SPAM = "SPAM"
    OTHER = "OTHER"


class EmailClassification(BaseModel):
    category: EmailCategory

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Model confidence between 0 and 1.",
    )

    reasoning: str = Field(
        min_length=1,
        max_length=1000,
        description="Short explanation for the classification.",
    )