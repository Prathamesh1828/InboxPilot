import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ============================================================
    # Application
    # ============================================================

    app_name: str
    environment: str
    debug: bool
    frontend_url: str = "http://localhost:3000"
    api_key: str = "dev-secret-key"

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
    # Telegram
    # ============================================================

    telegram_bot_token: str = ""
    telegram_bot_username: str = ""
    telegram_webhook_secret: str = ""

    # ============================================================
    # Pydantic Settings Configuration
    # ============================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def validate_secrets(self) -> None:
        if self.environment == "production":
            if self.api_key == "dev-secret-key":
                raise ValueError("API_KEY must be changed in production")
            if not self.llm_api_key:
                raise ValueError("LLM_API_KEY must be set in production")
            if not self.session_secret or self.session_secret == "changeme":
                raise ValueError("SESSION_SECRET must be set in production")


settings = Settings()
settings.validate_secrets()


# OAuthlib needs this as an actual environment variable.
# This is only appropriate for local HTTP development.
if settings.oauthlib_insecure_transport == "1":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"