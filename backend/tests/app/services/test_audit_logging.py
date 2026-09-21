from unittest import mock

import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.api.deps import get_db
from app.core.settings import settings
from app.main import app
from app.models.audit_event import AuditEvent
from app.models.email import Email
from app.repositories.audit_repository import log_audit_event


@pytest.fixture
def db():
    """Create an isolated SQLite in-memory database for each test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_email(db):
    from datetime import datetime, timezone
    email = Email(
        provider_message_id="test_msg_id",
        thread_id="test_thread_id",
        sender="test@example.com",
        recipients="user@example.com",
        subject="Audit Test Email",
        body="This is an audit test email",
        status="PENDING",
        received_at=datetime.now(timezone.utc),
    )
    db.add(email)
    db.commit()
    db.refresh(email)
    return email


def test_audit_event_creation_and_scrubbing(db, test_email):
    """
    Test that audit events are created successfully
    and sensitive data is scrubbed.
    """
    log_audit_event(
        db=db,
        email_id=test_email.id,
        event_type="TEST_EVENT",
        action="ARCHIVE",
        details={
            "token": "secret_abc123",
            "normal_data": "visible",
            "nested": {
                "access_token": "hidden",
                "other": "ok",
            }
        },
    )

    event = db.query(AuditEvent).filter_by(email_id=test_email.id).first()
    assert event is not None
    assert event.event_type == "TEST_EVENT"
    assert event.action == "ARCHIVE"
    assert event.details["token"] == "***"
    assert event.details["normal_data"] == "visible"
    assert event.details["nested"]["access_token"] == "***"
    assert event.details["nested"]["other"] == "ok"


def test_audit_logging_failure_safety(db, test_email):
    """
    Test that if the DB commit fails, log_audit_event catches the error
    and does NOT raise an exception, preventing workflow crashes.
    """
    with mock.patch.object(db, "add", side_effect=Exception("Simulated DB error")):
        # This should NOT raise an exception
        log_audit_event(
            db=db,
            email_id=test_email.id,
            event_type="FAILING_EVENT",
        )
    
    # Event shouldn't be in the DB
    event = db.query(AuditEvent).filter_by(event_type="FAILING_EVENT").first()
    assert event is None


def test_api_audit_trail(db, test_email):
    """
    Test the GET /emails/{email_id}/audit API endpoint.
    """
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    
    log_audit_event(
        db=db,
        email_id=test_email.id,
        event_type="EVENT_1",
    )
    log_audit_event(
        db=db,
        email_id=test_email.id,
        event_type="EVENT_2",
    )

    response = client.get(
        f"/emails/{test_email.id}/audit",
        headers={"X-API-Key": settings.api_key}
    )
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["event_type"] == "EVENT_1"
    assert data[1]["event_type"] == "EVENT_2"
    assert data[0]["email_id"] == test_email.id
