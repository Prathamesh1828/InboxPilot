import json

from app.integrations.llm.factory import create_llm_provider
from app.schemas.classification import EmailClassification
from app.services.classification_prompt import (
    CLASSIFICATION_SYSTEM_PROMPT,
)


class EmailClassifier:
    """
    Classifies emails using the configured LLM provider.

    The provider itself handles:
        Groq → Gemini fallback
    """

    def __init__(self):
        self.llm = create_llm_provider()

    def classify(
        self,
        sender: str,
        recipients: list[str],
        subject: str | None,
        body: str,
    ) -> EmailClassification:
        """
        Classify a single email.

        Returns:
            Validated EmailClassification object.
        """

        user_prompt = self._build_user_prompt(
            sender=sender,
            recipients=recipients,
            subject=subject,
            body=body,
        )

        response = self.llm.generate(
            system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return self._parse_response(response)

    @staticmethod
    def _build_user_prompt(
        sender: str,
        recipients: list[str],
        subject: str | None,
        body: str,
    ) -> str:
        """
        Build the email content sent to the LLM.
        """

        recipients_text = ", ".join(recipients)

        return f"""
Classify the following email.

FROM:
{sender}

TO:
{recipients_text}

SUBJECT:
{subject or "(No subject)"}

BODY:
{body}
"""

    @staticmethod
    def _parse_response(
        response: str,
    ) -> EmailClassification:
        """
        Parse and validate the LLM JSON response.
        """

        cleaned_response = response.strip()

        # Handle models that wrap JSON in markdown fences.
        if cleaned_response.startswith("```"):
            lines = cleaned_response.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned_response = "\n".join(lines).strip()

        try:
            data = json.loads(cleaned_response)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid JSON for email classification"
            ) from exc

        return EmailClassification.model_validate(data)