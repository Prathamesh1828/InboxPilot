import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ============================================================
    # Application
    # ============================================================

    app_name: str
    environment: str
    debug: bool

    # ============================================================
    # Database
    # ============================================================

    database_url: str

    # ============================================================
    # Google OAuth
    # ============================================================

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    # ============================================================
    # Session
    # ============================================================

    session_secret: str

    # ============================================================
    # OAuthlib local development
    # ============================================================

    oauthlib_insecure_transport: str = "1"

    # ============================================================
    # LLM - Primary Provider
    # ============================================================

    llm_provider: str = "groq"
    llm_model: str
    llm_api_key: str

    # ============================================================
    # LLM - Fallback Provider
    # ============================================================

    llm_fallback_provider: str = "gemini"
    llm_fallback_model: str
    llm_fallback_api_key: str

    # ============================================================
    # LLM Behaviour
    # ============================================================

    llm_confidence_threshold: float = 0.85
    llm_timeout_seconds: int = 20
    llm_max_retries: int = 2

    # ============================================================
    # Pydantic Settings Configuration
    # ============================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()


# OAuthlib needs this as an actual environment variable.
# This is only appropriate for local HTTP development.
if settings.oauthlib_insecure_transport == "1":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"