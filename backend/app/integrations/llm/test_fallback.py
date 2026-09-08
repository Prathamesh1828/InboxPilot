from app.integrations.llm.base import LLMProvider
from app.integrations.llm.fallback import LLMFallback
from app.integrations.llm.gemini_client import GeminiProvider


class FailingProvider(LLMProvider):
    """
    Test provider used to simulate a primary LLM failure.

    This allows us to verify that LLMFallback correctly
    switches from the primary provider to Gemini.
    """

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        raise RuntimeError(
            "Simulated primary LLM failure"
        )


def main():
    print("Testing LLM fallback mechanism...")
    print("--------------------------------")

    try:
        primary_provider = FailingProvider()
        fallback_provider = GeminiProvider()

        provider = LLMFallback(
            primary_provider=primary_provider,
            fallback_provider=fallback_provider,
        )

        print("Primary provider: simulated failure")
        print("Fallback provider: Gemini")
        print()
        print("Sending request...")
        print()

        response = provider.generate(
            system_prompt=(
                "You are a helpful assistant. "
                "Answer briefly and clearly."
            ),
            user_prompt=(
                "Explain email classification "
                "in one sentence."
            ),
        )

        print()
        print("✅ Fallback successful")
        print("--------------------------------")
        print("Gemini response:")
        print(response)

    except Exception as e:
        print()
        print("❌ Fallback test failed")
        print("--------------------------------")
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()