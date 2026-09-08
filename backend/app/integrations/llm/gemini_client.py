from google import genai

from app.core.settings import settings
from app.integrations.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    """
    Gemini implementation of the common LLMProvider interface.
    """

    def __init__(self):
        if not settings.llm_fallback_api_key:
            raise RuntimeError(
                "Gemini API key is not configured"
            )

        self.client = genai.Client(
            api_key=settings.llm_fallback_api_key,
        )

        self.model = settings.llm_fallback_model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Send a request to Gemini and return the generated text.
        """

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config={
                "system_instruction": system_prompt,
                "temperature": 0,
            },
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response"
            )

        return response.text