import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    environment: str
    debug: bool
    database_url: str

    # Google OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    # Session
    session_secret: str

    # OAuthlib local development
    oauthlib_insecure_transport: str = "1"

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