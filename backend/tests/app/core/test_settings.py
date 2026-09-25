import pytest
from app.core.settings import Settings

def test_production_rejects_debug_true():
    with pytest.raises(ValueError, match="DEBUG must be False in production"):
        s = Settings(
            app_name="InboxPilot",
            environment="production",
            debug=True,
            database_url="sqlite://",
            google_client_id="id",
            google_client_secret="secret",
            google_redirect_uri="uri",
            session_secret="valid_secret",
            llm_api_key="valid_key",
            llm_fallback_api_key="valid_key",
            telegram_webhook_secret="secret",
            api_key="valid_api_key"
        )
        s.validate_secrets()

def test_production_rejects_default_api_key():
    with pytest.raises(ValueError, match="API_KEY must be changed and set in production"):
        s = Settings(
            app_name="InboxPilot",
            environment="production",
            debug=False,
            database_url="sqlite://",
            google_client_id="id",
            google_client_secret="secret",
            google_redirect_uri="uri",
            session_secret="valid_secret",
            llm_api_key="valid_key",
            llm_fallback_api_key="valid_key",
            telegram_webhook_secret="secret",
            api_key="dev-secret-key"
        )
        s.validate_secrets()

def test_production_rejects_missing_session_secret():
    with pytest.raises(ValueError, match="SESSION_SECRET must be set in production"):
        s = Settings(
            app_name="InboxPilot",
            environment="production",
            debug=False,
            database_url="sqlite://",
            google_client_id="id",
            google_client_secret="secret",
            google_redirect_uri="uri",
            session_secret="changeme",
            llm_api_key="valid_key",
            llm_fallback_api_key="valid_key",
            telegram_webhook_secret="secret",
            api_key="valid_api_key"
        )
        s.validate_secrets()

def test_production_rejects_missing_oauth_credentials():
    with pytest.raises(ValueError, match="Google OAuth credentials must be set in production"):
        s = Settings(
            app_name="InboxPilot",
            environment="production",
            debug=False,
            database_url="sqlite://",
            google_client_id="",
            google_client_secret="",
            google_redirect_uri="uri",
            session_secret="valid",
            llm_api_key="valid_key",
            llm_fallback_api_key="valid_key",
            telegram_webhook_secret="secret",
            api_key="valid_api_key"
        )
        s.validate_secrets()

def test_production_accepts_valid_config():
    # Should not raise any exceptions
    s = Settings(
        app_name="InboxPilot",
        environment="production",
        debug=False,
        database_url="sqlite://",
        google_client_id="id",
        google_client_secret="secret",
        google_redirect_uri="uri",
        session_secret="valid_secret",
        llm_api_key="valid_key",
        llm_fallback_api_key="valid_key",
        telegram_webhook_secret="secret",
        api_key="valid_api_key",
        email_encryption_key="DWD9LuOYEgmYCFAK_-7z-CWsINGo3XAbsO7ffLaRP30=",  # test key
    )
    s.validate_secrets()

def test_development_accepts_defaults():
    # In development, it should not enforce strict secrets
    s = Settings(
        app_name="InboxPilot",
        environment="development",
        debug=True,
        database_url="sqlite://",
        google_client_id="id",
        google_client_secret="secret",
        google_redirect_uri="uri",
        session_secret="changeme",
        llm_api_key="valid_key",
        llm_fallback_api_key="valid_key",
        telegram_webhook_secret="",
        api_key="dev-secret-key"
    )
    s.validate_secrets()
