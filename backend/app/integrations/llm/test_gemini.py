from app.integrations.llm.gemini_client import GeminiProvider


def main():
    print("Testing Gemini provider...")
    print("--------------------------------")

    try:
        provider = GeminiProvider()

        print(f"Model: {provider.model}")
        print("Sending test request...")

        response = provider.generate(
            system_prompt=(
                "You are a helpful assistant. "
                "Answer briefly and clearly."
            ),
            user_prompt=(
                "What is email classification? "
                "Explain it in one sentence."
            ),
        )

        print()
        print("✅ Gemini request successful")
        print("--------------------------------")
        print("Response:")
        print(response)

    except Exception as e:
        print()
        print("❌ Gemini request failed")
        print("--------------------------------")
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()