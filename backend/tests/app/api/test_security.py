import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.settings import settings
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_missing_api_key():
    """Test that missing API key blocks access to secure endpoints"""
    response = client.get("/emails")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API Key"

def test_invalid_api_key():
    """Test that invalid API key blocks access to secure endpoints"""
    response = client.get(
        "/emails",
        headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API Key"

def test_valid_api_key_passes():
    """Test that valid API key allows access"""
    # Note: the test client may get a 404 for no emails if db override fails, 
    # but the auth should pass first.
    # We just want to ensure it doesn't return 401
    response = client.get(
        "/emails",
        headers={"X-API-Key": settings.api_key}
    )
    assert response.status_code != 401

@patch("app.api.routes.telegram.is_telegram_configured", return_value=True)
def test_telegram_webhook_missing_secret(mock_is_configured):
    """Test that Telegram webhook fails if secret is missing but configured"""
    with patch("app.api.routes.telegram.settings.telegram_webhook_secret", "secret_value"):
        response = client.post("/telegram/webhook", json={})
        assert response.status_code == 200
        assert response.json() == {"status": "unauthorized"}

@patch("app.api.routes.telegram.is_telegram_configured", return_value=True)
def test_telegram_webhook_valid_secret(mock_is_configured):
    """Test that Telegram webhook passes if secret is valid"""
    with patch("app.api.routes.telegram.settings.telegram_webhook_secret", "secret_value"):
        response = client.post(
            "/telegram/webhook",
            headers={"X-Telegram-Bot-Api-Secret-Token": "secret_value"},
            json={"message": {"text": "hello"}}
        )
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

def test_rate_limit_auth_endpoint():
    """Test that the auth endpoint is heavily rate limited (5/min)"""
    client = TestClient(app)
    # The limit is 5/minute. The first 5 should succeed, the 6th should 429.
    for _ in range(5):
        # We expect a 302 redirect for gmail/login
        response = client.get("/auth/gmail/login", follow_redirects=False)
        assert response.status_code in (302, 200)

    # 6th request
    response = client.get("/auth/gmail/login", follow_redirects=False)
    assert response.status_code == 429
