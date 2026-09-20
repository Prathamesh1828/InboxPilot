from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
import pytest

from app.db.database import SessionLocal, engine
from app.db.base import Base
from app.models.google_account import GoogleAccount
from app.models.telegram_connection import TelegramConnection
from app.services.telegram_connection_service import TelegramConnectionService
from app.repositories.telegram_connection_repository import get_telegram_connection_by_user_id

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        # Cleanup
        db.query(TelegramConnection).delete()
        db.query(GoogleAccount).filter(GoogleAccount.email.in_(["test_telegram@example.com", "test1@example.com", "test2@example.com"])).delete()
        db.commit()
        db.close()


@pytest.fixture(scope="function")
def test_user(db: Session):
    # Ensure cleanup before
    db.query(TelegramConnection).delete()
    db.query(GoogleAccount).filter(GoogleAccount.email == "test_telegram@example.com").delete()
    db.commit()
    db.commit()
    
    # Create a dummy user (GoogleAccount) for testing
    account = GoogleAccount(
        email="test_telegram@example.com",
        access_token="dummy_access",
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def test_generate_connection_link(db: Session, test_user: GoogleAccount, monkeypatch):
    monkeypatch.setattr("app.core.settings.settings.telegram_bot_username", "InboxPilotBot")
    
    link = TelegramConnectionService.generate_connection_link(db, user_id=test_user.id)
    assert link.startswith("https://t.me/InboxPilotBot?start=")
    
    # Check that it's in the database
    token = link.split("=")[-1]
    conn = get_telegram_connection_by_user_id(db, user_id=test_user.id)
    assert conn is not None
    assert conn.connection_token == token
    assert conn.connected_at is None


def test_connect_account_success(db: Session, test_user: GoogleAccount, monkeypatch):
    monkeypatch.setattr("app.core.settings.settings.telegram_bot_username", "InboxPilotBot")
    TelegramConnectionService.generate_connection_link(db, user_id=test_user.id)
    
    # Fetch the previously generated token
    conn = get_telegram_connection_by_user_id(db, user_id=test_user.id)
    token = conn.connection_token
    
    TelegramConnectionService.connect_account(
        db=db,
        token=token,
        telegram_user_id="12345",
        telegram_chat_id="67890",
    )
    
    db.refresh(conn)
    assert conn.connected_at is not None
    assert conn.telegram_user_id == "12345"
    assert conn.telegram_chat_id == "67890"


def test_connect_account_already_connected(db: Session, test_user: GoogleAccount, monkeypatch):
    monkeypatch.setattr("app.core.settings.settings.telegram_bot_username", "InboxPilotBot")
    TelegramConnectionService.generate_connection_link(db, user_id=test_user.id)
    
    # Fetch the previously generated token
    conn = get_telegram_connection_by_user_id(db, user_id=test_user.id)
    token = conn.connection_token
    
    # Connect once
    TelegramConnectionService.connect_account(db, token, "123", "456")
    
    with pytest.raises(ValueError, match="This token has already been used."):
        TelegramConnectionService.connect_account(
            db=db,
            token=token,
            telegram_user_id="12345",
            telegram_chat_id="67890",
        )


def test_connect_account_invalid_token(db: Session):
    with pytest.raises(ValueError, match="Invalid or unrecognized token."):
        TelegramConnectionService.connect_account(
            db=db,
            token="invalid_token",
            telegram_user_id="111",
            telegram_chat_id="222",
        )


def test_connect_account_expired_token(db: Session, test_user: GoogleAccount, monkeypatch):
    monkeypatch.setattr("app.core.settings.settings.telegram_bot_username", "InboxPilotBot")
    TelegramConnectionService.generate_connection_link(db, user_id=test_user.id)
    
    import secrets
    from app.repositories.telegram_connection_repository import update_telegram_connection

    conn = get_telegram_connection_by_user_id(db, user_id=test_user.id)
    
    # Reset connection for this test
    conn.connected_at = None
    conn.connection_token = secrets.token_urlsafe(32)
    conn.token_expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    update_telegram_connection(db, conn)

    with pytest.raises(ValueError, match="This token has expired."):
        TelegramConnectionService.connect_account(
            db=db,
            token=conn.connection_token,
            telegram_user_id="111",
            telegram_chat_id="222",
        )


def test_connect_account_already_linked_chat(db: Session, monkeypatch):
    monkeypatch.setattr("app.core.settings.settings.telegram_bot_username", "InboxPilotBot")
    
    # Clean up any leftover users from previous failed runs
    db.query(TelegramConnection).delete()
    db.query(GoogleAccount).filter(GoogleAccount.email.in_(["test1@example.com", "test2@example.com"])).delete()
    db.commit()

    # Two users, same chat id
    user1 = GoogleAccount(email="test1@example.com", access_token="1")
    user2 = GoogleAccount(email="test2@example.com", access_token="2")
    db.add_all([user1, user2])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    # Link user1 to chat "999"
    link1 = TelegramConnectionService.generate_connection_link(db, user_id=user1.id)
    token1 = link1.split("=")[-1]
    TelegramConnectionService.connect_account(db, token1, "userA", "999")

    # Try to link user2 to chat "999"
    link2 = TelegramConnectionService.generate_connection_link(db, user_id=user2.id)
    token2 = link2.split("=")[-1]
    
    with pytest.raises(ValueError, match="This Telegram account is already linked to another user."):
        TelegramConnectionService.connect_account(db, token2, "userB", "999")

    # Cleanup
    db.query(TelegramConnection).filter(TelegramConnection.user_id.in_([user1.id, user2.id])).delete()
    db.query(GoogleAccount).filter(GoogleAccount.id.in_([user1.id, user2.id])).delete()
    db.commit()
