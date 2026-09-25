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
    redis_url: str = "redis://localhost:6379/0"

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
    # Email Encryption (AES-256-GCM)
    # ============================================================
    # Generate with:
    #   python -c "import secrets,base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
    # Store ONLY in environment/secret manager — never in source code.
    email_encryption_key: str = ""  # empty = no encryption (dev mode)

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
            if self.debug:
                raise ValueError("DEBUG must be False in production")
            if self.api_key == "dev-secret-key" or not self.api_key:
                raise ValueError("API_KEY must be changed and set in production")
            if not self.llm_api_key:
                raise ValueError("LLM_API_KEY must be set in production")
            if not self.session_secret or self.session_secret == "changeme":
                raise ValueError("SESSION_SECRET must be set in production")
            if not self.google_client_id or not self.google_client_secret:
                raise ValueError("Google OAuth credentials must be set in production")
            if not self.telegram_webhook_secret:
                raise ValueError("TELEGRAM_WEBHOOK_SECRET must be set in production")
            if not self.email_encryption_key:
                raise ValueError(
                    "EMAIL_ENCRYPTION_KEY must be set in production. "
                    "Generate with: python -c \"import secrets,base64; "
                    "print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())\""
                )


settings = Settings()
settings.validate_secrets()


# OAuthlib needs this as an actual environment variable.
# This is only appropriate for local HTTP development.
if settings.oauthlib_insecure_transport == "1":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"