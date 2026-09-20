"""
Idempotency and external API failure handling tests.

All tests use an isolated SQLite in-memory database.
They never touch the development PostgreSQL database.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.email import Email
from app.models.action_approval import ActionApproval
from app.repositories.action_approval_repository import (
    atomic_transition_status,
    create_action_approval,
    get_action_approval,
    get_pending_approval_by_email_id,
    update_action_approval_status,
)
from app.repositories.email_repository import (
    create_email,
    create_email_if_not_exists,
    get_email_by_id,
)
from app.services.approval_execution_service import ApprovalExecutionService
from app.services.approval_service import ApprovalService


# ---------------------------------------------------------
# Isolated test database fixture
# ---------------------------------------------------------

@pytest.fixture
def db():
    """Create an isolated SQLite in-memory database for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_email(db):
    """Create a sample email in the test database."""
    email = create_email(
        db=db,
        provider_message_id="test-msg-001",
        thread_id="test-thread-001",
        sender="sender@example.com",
        recipients=["user@example.com"],
        subject="Test Email",
        body="This is a test email body.",
        received_at=datetime.now(timezone.utc),
    )
    return email


@pytest.fixture
def sample_approval(db, sample_email):
    """Create a sample PENDING approval in the test database."""
    approval = create_action_approval(
        db=db,
        email_id=sample_email.id,
        action="LOG_BILL",
        action_plan={
            "action": "LOG_BILL",
            "parameters": {
                "amount": 100.0,
                "currency": "INR",
                "vendor": "Test",
                "due_date": None,
            },
            "reasoning": "Test bill.",
            "confidence": 0.95,
            "risk_level": "LOW",
            "requires_approval": False,
        },
    )
    return approval


# ---------------------------------------------------------
# Test 1: Duplicate email ingestion
# ---------------------------------------------------------

def test_duplicate_email_ingestion(db):
    """Inserting the same provider_message_id twice returns the
    existing email, not a duplicate."""

    email_1, created_1 = create_email_if_not_exists(
        db=db,
        provider_message_id="dedup-test-001",
        thread_id="thread",
        sender="a@example.com",
        recipients=["b@example.com"],
        subject="Dedup Test",
        body="Body",
        received_at=datetime.now(timezone.utc),
    )

    email_2, created_2 = create_email_if_not_exists(
        db=db,
        provider_message_id="dedup-test-001",
        thread_id="thread",
        sender="a@example.com",
        recipients=["b@example.com"],
        subject="Dedup Test",
        body="Body",
        received_at=datetime.now(timezone.utc),
    )

    assert created_1 is True
    assert created_2 is False
    assert email_1.id == email_2.id


# ---------------------------------------------------------
# Test 2: Duplicate approval creation
# ---------------------------------------------------------

def test_duplicate_approval_prevented(db, sample_email):
    """Only one PENDING approval should exist per email.
    Calling get_pending_approval_by_email_id prevents duplicates."""

    # First approval
    approval_1 = create_action_approval(
        db=db,
        email_id=sample_email.id,
        action="LOG_BILL",
        action_plan={"action": "LOG_BILL", "parameters": {}},
    )

    # Check for existing before creating second
    existing = get_pending_approval_by_email_id(
        db=db,
        email_id=sample_email.id,
    )

    assert existing is not None
    assert existing.id == approval_1.id


# ---------------------------------------------------------
# Test 3: Double-execution guard
# ---------------------------------------------------------

def test_double_execution_blocked(db, sample_email, sample_approval):
    """An EXECUTED approval cannot be executed again."""

    # Manually set status to EXECUTED
    update_action_approval_status(
        db=db,
        approval_id=sample_approval.id,
        status="EXECUTED",
    )

    with pytest.raises(ValueError, match="cannot be executed"):
        ApprovalExecutionService.execute_approved(
            db=db,
            approval_id=sample_approval.id,
        )


# ---------------------------------------------------------
# Test 4: Atomic execution race condition
# ---------------------------------------------------------

def test_atomic_transition_race(db, sample_email, sample_approval):
    """Two concurrent atomic transitions — only one succeeds."""

    # Set to APPROVED first
    update_action_approval_status(
        db=db,
        approval_id=sample_approval.id,
        status="APPROVED",
    )

    # First transition: APPROVED → EXECUTING
    first = atomic_transition_status(
        db=db,
        approval_id=sample_approval.id,
        from_status="APPROVED",
        to_status="EXECUTING",
    )

    # Second transition: same APPROVED → EXECUTING (should fail)
    second = atomic_transition_status(
        db=db,
        approval_id=sample_approval.id,
        from_status="APPROVED",
        to_status="EXECUTING",
    )

    assert first is True
    assert second is False

    # Verify final state
    approval = get_action_approval(db, sample_approval.id)
    assert approval.status == "EXECUTING"


# ---------------------------------------------------------
# Test 5: Execution failure → EXECUTION_FAILED
# ---------------------------------------------------------

def test_execution_failure_marks_failed(db, sample_email):
    """When the external API fails, approval status should be
    EXECUTION_FAILED, not EXECUTED or PENDING."""

    approval = create_action_approval(
        db=db,
        email_id=sample_email.id,
        action="CREATE_CALENDAR_EVENT",
        action_plan={
            "action": "CREATE_CALENDAR_EVENT",
            "parameters": {
                "title": "Test",
                "start_time": "invalid-time",
                "end_time": None,
                "description": None,
            },
            "reasoning": "Test.",
            "confidence": 0.95,
            "risk_level": "MEDIUM",
            "requires_approval": True,
        },
    )

    # Approve it
    ApprovalService.approve(db=db, approval_id=approval.id)

    # Execute — should fail because start_time is invalid
    with pytest.raises(Exception):
        ApprovalExecutionService.execute_approved(
            db=db,
            approval_id=approval.id,
        )

    # Verify status is EXECUTION_FAILED, not PENDING
    db.refresh(approval)
    assert approval.status == "EXECUTION_FAILED"


# ---------------------------------------------------------
# Test 6: Bill idempotency
# ---------------------------------------------------------

def test_bill_idempotency(db, sample_email):
    """Executing LOG_BILL twice for the same email returns
    'already exists' on the second call."""

    from app.models.bill import Bill
    # Ensure bill table exists in SQLite
    Base.metadata.create_all(bind=db.get_bind())

    from app.services.executor import ActionExecutor
    from app.schemas.action_plan import BillActionPlan, BillParameters

    plan = BillActionPlan(
        action="LOG_BILL",
        parameters=BillParameters(
            amount=100.0,
            currency="INR",
            vendor="Test Vendor",
            due_date=None,
        ),
        reasoning="Test",
        confidence=0.95,
        risk_level="LOW",
        requires_approval=False,
    )

    executor = ActionExecutor()

    result_1 = executor.execute(plan=plan, db=db, email_id=sample_email.id)
    assert "successfully" in result_1.lower()

    result_2 = executor.execute(plan=plan, db=db, email_id=sample_email.id)
    assert "already exists" in result_2.lower()


# ---------------------------------------------------------
# Test 7: Reminder idempotency
# ---------------------------------------------------------

def test_reminder_idempotency(db, sample_email):
    """Executing CREATE_REMINDER twice for the same email
    returns 'already exists' on the second call."""

    from app.models.reminder import Reminder
    Base.metadata.create_all(bind=db.get_bind())

    from app.services.executor import ActionExecutor
    from app.schemas.action_plan import ReminderActionPlan, ReminderParameters

    plan = ReminderActionPlan(
        action="CREATE_REMINDER",
        parameters=ReminderParameters(
            reminder_text="Test reminder",
            reminder_date="2026-12-01",
        ),
        reasoning="Test",
        confidence=0.95,
        risk_level="LOW",
        requires_approval=False,
    )

    executor = ActionExecutor()

    result_1 = executor.execute(plan=plan, db=db, email_id=sample_email.id)
    assert "successfully" in result_1.lower()

    result_2 = executor.execute(plan=plan, db=db, email_id=sample_email.id)
    assert "already exists" in result_2.lower()


# ---------------------------------------------------------
# Test 8: Approval retry after failure
# ---------------------------------------------------------

def test_approval_retry_after_failure(db, sample_email):
    """An EXECUTION_FAILED approval can be re-approved."""

    approval = create_action_approval(
        db=db,
        email_id=sample_email.id,
        action="LOG_BILL",
        action_plan={
            "action": "LOG_BILL",
            "parameters": {
                "amount": 100.0,
                "currency": "INR",
                "vendor": "Test",
                "due_date": None,
            },
            "reasoning": "Test.",
            "confidence": 0.95,
            "risk_level": "LOW",
            "requires_approval": False,
        },
    )

    # Simulate: approve → fail → EXECUTION_FAILED
    update_action_approval_status(
        db=db,
        approval_id=approval.id,
        status="EXECUTION_FAILED",
    )

    # Re-approve should succeed (not raise)
    result = ApprovalService.approve(
        db=db,
        approval_id=approval.id,
    )

    assert "approved" in result.lower()

    # Verify status is APPROVED
    db.refresh(approval)
    assert approval.status == "APPROVED"


# ---------------------------------------------------------
# Test 9: Celery skips terminal statuses
# ---------------------------------------------------------

def test_terminal_status_skipped():
    """The Celery task should skip emails in terminal statuses."""

    from app.workers.tasks import _TERMINAL_STATUSES

    assert "COMPLETED" in _TERMINAL_STATUSES
    assert "APPROVAL_PENDING" in _TERMINAL_STATUSES
    assert "GROUNDING_REVIEW" in _TERMINAL_STATUSES
    assert "EXECUTED" in _TERMINAL_STATUSES


# ---------------------------------------------------------
# Test 10: Telegram failure doesn't block approval creation
# ---------------------------------------------------------

def test_telegram_failure_non_fatal(db, sample_email):
    """If Telegram notification fails, the approval should
    still be created in the database."""

    from app.agents.nodes import approval_node
    from app.agents.state import InboxPilotState
    from app.schemas.action_plan import BillActionPlan, BillParameters

    plan = BillActionPlan(
        action="LOG_BILL",
        parameters=BillParameters(
            amount=100.0,
            currency="INR",
            vendor="Test",
            due_date=None,
        ),
        reasoning="Test",
        confidence=0.95,
        risk_level="LOW",
        requires_approval=True,
    )

    state = InboxPilotState(
        email_id=sample_email.id,
        subject="Test",
        body="Test body",
        action_plan=plan,
        workflow_status="SAFETY_EVALUATED",
    )

    # Patch Telegram to raise an exception
    with patch(
        "app.integrations.telegram.bot.send_approval_notification",
        side_effect=RuntimeError("Telegram API down"),
    ):
        result = approval_node(state, db)

    # Approval should still be created
    assert result["approval_id"] is not None
    assert result["workflow_status"] == "APPROVAL_PENDING"

    # Verify it's in the database
    approval = get_action_approval(db, result["approval_id"])
    assert approval is not None
    assert approval.status == "PENDING"
