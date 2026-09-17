from typing import Any, cast

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from app.core.settings import settings
from app.schemas.action_plan import (
    ActionPlan,
    ActionType,
    ArchiveActionPlan,
    ArchiveParameters,
    BillActionPlan,
    BillParameters,
    CalendarActionPlan,
    CalendarEventParameters,
    DraftReplyActionPlan,
    DraftReplyParameters,
    NoActionPlan,
    NoActionParameters,
    ReminderActionPlan,
    ReminderParameters,
)


class RawActionPlan(BaseModel):
    """
    Intermediate schema used for the LLM response.

    The LLM produces a simple action + parameters structure.
    InboxPilot then converts this into a strongly typed
    ActionPlan before grounding and execution.
    """

    action: str = Field(
        description=(
            "One of: LOG_BILL, CREATE_CALENDAR_EVENT, "
            "CREATE_REMINDER, DRAFT_REPLY, ARCHIVE, NO_ACTION."
        )
    )

    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for the selected action only.",
    )

    reasoning: str = Field(
        default="",
        max_length=1000,
    )

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )


class EmailPlanner:
    def __init__(self) -> None:
        self.llm = ChatGroq(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            temperature=0,
        )

    def create_plan(
        self,
        category: str,
        classification_reasoning: str,
        subject: str | None,
        body: str,
    ) -> ActionPlan:
        """
        Ask the LLM to propose one action for the email.

        The LLM decides:
        - action
        - parameters
        - reasoning
        - confidence

        Risk and approval are determined later by the
        deterministic safety policy.
        """

        structured_llm = self.llm.with_structured_output(
            RawActionPlan,
            method="json_mode",
        )

        prompt = f"""
You are InboxPilot's action planner.

Choose exactly ONE action for this classified email.

Category: {category}

Subject: {subject or "(No subject)"}

Email:
{body}

Allowed actions:
LOG_BILL
CREATE_CALENDAR_EVENT
CREATE_REMINDER
DRAFT_REPLY
ARCHIVE
NO_ACTION

Parameter rules:

LOG_BILL:
amount, currency, vendor, due_date

CREATE_CALENDAR_EVENT:
title, start_time, end_time, description

CREATE_REMINDER:
reminder_text, reminder_date

DRAFT_REPLY:
reply_text

ARCHIVE:
reason

NO_ACTION:
{{}}

Rules:
- Use only parameters allowed for the selected action.
- Do not mix parameters between actions.
- Ground every parameter in the email.
- Do not invent facts.
- If the email does not contain enough information for an action, choose NO_ACTION.
- Return short reasoning.
- Confidence must be between 0.0 and 1.0.
- Do not determine risk or approval.

Return valid JSON only.
"""

        raw_plan = cast(
            RawActionPlan,
            structured_llm.invoke(prompt),
        )

        return self._convert_to_action_plan(raw_plan)

    @staticmethod
    def _convert_to_action_plan(
        raw_plan: RawActionPlan,
    ) -> ActionPlan:
        """
        Convert the LLM's raw output into a strongly typed
        InboxPilot ActionPlan.

        This is the validation boundary between the LLM
        and the rest of the application.
        """

        action = raw_plan.action.strip().upper()

        reasoning = (
            raw_plan.reasoning
            or "Action proposed by the InboxPilot planner."
        )

        confidence = raw_plan.confidence

        # -------------------------------------------------
        # LOG_BILL
        # -------------------------------------------------

        if action == "LOG_BILL":
            parameters = BillParameters.model_validate(
                raw_plan.parameters
            )

            return BillActionPlan(
                action=ActionType.LOG_BILL,
                parameters=parameters,
                reasoning=reasoning,
                confidence=confidence,
                risk_level="LOW",
                requires_approval=False,
            )

        # -------------------------------------------------
        # CREATE_REMINDER
        # -------------------------------------------------

        if action == "CREATE_REMINDER":
            parameters = ReminderParameters.model_validate(
                raw_plan.parameters
            )

            return ReminderActionPlan(
                action=ActionType.CREATE_REMINDER,
                parameters=parameters,
                reasoning=reasoning,
                confidence=confidence,
                risk_level="LOW",
                requires_approval=False,
            )

        # -------------------------------------------------
        # CREATE_CALENDAR_EVENT
        # -------------------------------------------------

        if action == "CREATE_CALENDAR_EVENT":
            parameters = CalendarEventParameters.model_validate(
                raw_plan.parameters
            )

            return CalendarActionPlan(
                action=ActionType.CREATE_CALENDAR_EVENT,
                parameters=parameters,
                reasoning=reasoning,
                confidence=confidence,
                risk_level="MEDIUM",
                requires_approval=True,
            )

        # -------------------------------------------------
        # DRAFT_REPLY
        # -------------------------------------------------

        if action == "DRAFT_REPLY":
            parameters = DraftReplyParameters.model_validate(
                raw_plan.parameters
            )

            return DraftReplyActionPlan(
                action=ActionType.DRAFT_REPLY,
                parameters=parameters,
                reasoning=reasoning,
                confidence=confidence,
                risk_level="MEDIUM",
                requires_approval=True,
            )

        # -------------------------------------------------
        # ARCHIVE
        # -------------------------------------------------

        if action == "ARCHIVE":
            parameters = ArchiveParameters.model_validate(
                raw_plan.parameters
            )

            return ArchiveActionPlan(
                action=ActionType.ARCHIVE,
                parameters=parameters,
                reasoning=reasoning,
                confidence=confidence,
                risk_level="LOW",
                requires_approval=False,
            )

        # -------------------------------------------------
        # NO_ACTION
        # -------------------------------------------------

        if action == "NO_ACTION":
            parameters = NoActionParameters.model_validate(
                raw_plan.parameters
            )

            return NoActionPlan(
                action=ActionType.NO_ACTION,
                parameters=parameters,
                reasoning=reasoning,
                confidence=confidence,
                risk_level="LOW",
                requires_approval=False,
            )

        raise ValueError(
            f"Unsupported planner action: {raw_plan.action}"
        )