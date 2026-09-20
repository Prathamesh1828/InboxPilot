import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import engine, SessionLocal
from app.db.base import Base

client = TestClient(app)

def test_telegram_webhook_no_config(monkeypatch):
    # Ensure it returns {"status": "ignored"} when token is not set
    monkeypatch.setattr("app.core.settings.settings.telegram_bot_token", "")
    
    response = client.post(
        "/telegram/webhook",
        json={"update_id": 123}
    )
    
    assert response.status_code == 200
    assert response.json() == {"status": "ignored"}


def test_telegram_webhook_invalid_action(monkeypatch):
    monkeypatch.setattr("app.core.settings.settings.telegram_bot_token", "fake-token")
    monkeypatch.setattr("app.core.settings.settings.telegram_bot_username", "fake-username")
    
    # Mock httpx.post to avoid making actual network requests
    def mock_post(*args, **kwargs):
        pass
        
    monkeypatch.setattr("httpx.post", mock_post)

    response = client.post(
        "/telegram/webhook",
        json={
            "callback_query": {
                "id": "123",
                "data": "invalid_1",
                "message": {"message_id": 1, "text": "Do you approve this action?"}
            }
        }
    )
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_telegram_webhook_start_command(monkeypatch):
    monkeypatch.setattr("app.core.settings.settings.telegram_bot_token", "fake-token")
    monkeypatch.setattr("app.core.settings.settings.telegram_bot_username", "fake-bot")
    
    # Mock the connection service to avoid needing DB access
    class MockConnectionService:
        @staticmethod
        def connect_account(db, token, telegram_user_id, telegram_chat_id):
            if token == "invalid":
                raise ValueError("Invalid token")
            pass
            
    monkeypatch.setattr("app.api.routes.telegram.TelegramConnectionService", MockConnectionService)
    
    # Mock httpx.post
    def mock_post(*args, **kwargs):
        pass
    monkeypatch.setattr("httpx.post", mock_post)
    
    # Test valid token
    response = client.post(
        "/telegram/webhook",
        json={
            "message": {
                "message_id": 123,
                "text": "/start valid_token",
                "chat": {"id": 987},
                "from": {"id": 555}
            }
        }
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    # Test invalid token
    response_invalid = client.post(
        "/telegram/webhook",
        json={
            "message": {
                "message_id": 124,
                "text": "/start invalid",
                "chat": {"id": 987},
                "from": {"id": 555}
            }
        }
    )
    assert response_invalid.status_code == 200
    assert response_invalid.json() == {"status": "ok"}
