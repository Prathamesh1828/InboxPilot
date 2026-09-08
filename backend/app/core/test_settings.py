from app.core.settings import settings


def main():
    print("✅ Settings loaded successfully")
    print("--------------------------------")

    print(f"Primary provider: {settings.llm_provider}")
    print(f"Primary model: {settings.llm_model}")
    print(
        f"Primary API key configured: "
        f"{bool(settings.llm_api_key)}"
    )

    print()

    print(f"Fallback provider: {settings.llm_fallback_provider}")
    print(f"Fallback model: {settings.llm_fallback_model}")
    print(
        f"Fallback API key configured: "
        f"{bool(settings.llm_fallback_api_key)}"
    )

    print()

    print(
        f"Confidence threshold: "
        f"{settings.llm_confidence_threshold}"
    )
    print(
        f"Timeout: "
        f"{settings.llm_timeout_seconds}s"
    )
    print(
        f"Max retries: "
        f"{settings.llm_max_retries}"
    )


if __name__ == "__main__":
    main()