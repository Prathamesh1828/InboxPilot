from typing import cast

from langchain_groq import ChatGroq

from app.core.settings import settings
from app.schemas.action_plan import ActionPlan


class EmailPlanner:
    """
    Creates an action plan for an email using an LLM.
    """

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

        structured_llm = self.llm.with_structured_output(
            ActionPlan
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

Choose only an appropriate action supported by the
ActionPlan schema.

Do not invent facts.
Do not perform the action.
Only create the proposed action plan.
"""

        return cast(
    ActionPlan,
    structured_llm.invoke(prompt),
)