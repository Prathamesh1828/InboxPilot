from app.core.settings import settings
from app.integrations.llm.base import LLMProvider
from app.integrations.llm.fallback import LLMFallback
from app.integrations.llm.gemini_client import GeminiProvider
from app.integrations.llm.groq_client import GroqProvider


def create_primary_provider() -> LLMProvider:
    """
    Create the configured primary LLM provider.
    """

    if settings.llm_provider.lower() == "groq":
        return GroqProvider()

    raise ValueError(
        f"Unsupported primary LLM provider: "
        f"{settings.llm_provider}"
    )


def create_fallback_provider() -> LLMProvider | None:
    """
    Create the configured fallback LLM provider.

    Returns None if fallback is disabled or not configured.
    """

    if not settings.llm_fallback_api_key:
        return None

    if settings.llm_fallback_provider.lower() == "gemini":
        return GeminiProvider()

    raise ValueError(
        f"Unsupported fallback LLM provider: "
        f"{settings.llm_fallback_provider}"
    )


def create_llm_provider() -> LLMProvider:
    """
    Create the complete LLM provider with fallback support.

    Primary:
        Groq

    Fallback:
        Gemini
    """

    primary_provider = create_primary_provider()
    fallback_provider = create_fallback_provider()

    return LLMFallback(
        primary_provider=primary_provider,
        fallback_provider=fallback_provider,
    )