from app.integrations.llm.base import LLMProvider


class LLMFallback(LLMProvider):
    """
    Handles fallback from the primary LLM provider
    to the secondary provider.
    """

    def __init__(
        self,
        primary_provider: LLMProvider,
        fallback_provider: LLMProvider | None,
    ):
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Try the primary provider first.

        If the primary provider fails, use the fallback
        provider if one is configured.
        """

        try:
            return self.primary_provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

        except Exception as primary_error:

            if self.fallback_provider is None:
                raise primary_error

            try:
                return self.fallback_provider.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )

            except Exception as fallback_error:
                raise RuntimeError(
                    "Both primary and fallback LLM providers failed"
                ) from fallback_error