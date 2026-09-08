from groq import Groq

from app.core.settings import settings
from app.integrations.llm.base import LLMProvider


class GroqProvider(LLMProvider):
    """
    Groq implementation of the common LLMProvider interface.
    """

    def __init__(self):
        self.client = Groq(
            api_key=settings.llm_api_key,
        )

        self.model = settings.llm_model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Send a request to Groq and return the generated text.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0,
        )

        if not response.choices:
            raise RuntimeError(
                "Groq returned no response choices"
            )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "Groq returned an empty response"
            )

        return content