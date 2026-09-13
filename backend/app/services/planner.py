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
        description=(
            "Parameters required for the selected action."
        ),
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
        Ask the LLM to propose an action plan.

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
You are the planning component of InboxPilot.

Your job is to determine what action, if any, should be
taken for an email.

The email has already been classified.

CLASSIFICATION:
{category}

CLASSIFICATION REASONING:
{classification_reasoning}

SUBJECT:
{subject or "(No subject)"}

BODY:
{body}

Choose exactly one action.

Allowed actions:

- LOG_BILL
- CREATE_CALENDAR_EVENT
- CREATE_REMINDER
- DRAFT_REPLY
- ARCHIVE
- NO_ACTION

IMPORTANT PARAMETER RULES:

For LOG_BILL, use ONLY:
- amount
- currency
- vendor
- due_date

For CREATE_REMINDER, use ONLY:
- reminder_text
- reminder_date

For CREATE_CALENDAR_EVENT, use ONLY:
- title
- start_time
- end_time
- description

For DRAFT_REPLY, use ONLY:
- reply_text

For ARCHIVE, use ONLY:
- reason

For NO_ACTION:
- use an empty parameters object

IMPORTANT:

Do not mix parameters between action types.

For CREATE_REMINDER, NEVER use:
- amount
- currency
- vendor
- due_date
- title
- note
- description

Instead use:
- reminder_text
- reminder_date

For LOG_BILL, NEVER use reminder_text or reminder_date.

All parameters must be grounded in the original email.

Do not invent facts.

Provide a short reasoning.

Provide confidence between 0.0 and 1.0.

Risk level and approval are NOT your responsibility.
They will be determined by InboxPilot's deterministic
safety policy after grounding.

Return ONLY valid JSON.
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