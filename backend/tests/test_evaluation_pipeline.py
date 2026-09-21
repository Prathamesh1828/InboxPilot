import json
import logging
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.email import Email
from app.models.google_account import GoogleAccount
from app.services.email_pipeline import EmailPipeline
from app.repositories.email_repository import create_email_if_not_exists

logger = logging.getLogger(__name__)

# Load the dataset
DATASET_PATH = Path(__file__).parent / "eval_dataset.json"
with open(DATASET_PATH, "r", encoding="utf-8") as f:
    EVAL_DATASET = json.load(f)

# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------

@pytest.fixture
def db():
    """Create an isolated SQLite in-memory database for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    # Create a mock GoogleAccount to satisfy Telegram/Calendar checks
    account = GoogleAccount(
        email="test@inboxpilot.com",
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
    )
    session.add(account)
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------
# Test execution
# ---------------------------------------------------------

# Parametrize over the dataset. We use id as the test ID.
@pytest.mark.parametrize(
    "case",
    EVAL_DATASET,
    ids=[item["id"] for item in EVAL_DATASET]
)
def test_pipeline_evaluation_case(db, case):
    """
    Run a full evaluation of the InboxPilot pipeline against a synthetic case.
    """
    from datetime import datetime, timezone
    import time
    time.sleep(5)
    
    # 1. Insert email into the database
    email, _ = create_email_if_not_exists(
        db=db,
        provider_message_id=f"msg_{case['id']}",
        thread_id=f"thread_{case['id']}",
        sender="sender@example.com",
        recipients=["test@inboxpilot.com"],
        subject=case["subject"],
        body=case["body"],
        received_at=datetime.now(timezone.utc),
    )
    
    pipeline = EmailPipeline()

    # 2. Patch external APIs to not make real Google/Telegram network calls during testing
    with (
        patch("app.integrations.telegram.bot.send_approval_notification"),
        patch("app.services.executor.archive_email", return_value="mock_archive_id"),
        patch("app.services.executor.create_calendar_event", return_value="mock_event_id"),
        patch("app.services.executor.create_gmail_draft", return_value="mock_draft_id"),
    ):
        # 3. Process the email
        result = pipeline.process_email(db=db, email_id=email.id)

    # 4. Assert Classification
    assert result.classification is not None, "Email failed to classify"
    actual_category = result.classification.category.value
    expected_category = case["expected_category"]
    
    if actual_category != expected_category:
        pytest.fail(f"Classification failed. Expected {expected_category}, got {actual_category}. Reasoning: {result.classification.reasoning}")

    # If the workflow status is REVIEW (due to low confidence), the action plan won't be generated
    if result.workflow_status == "REVIEW":
        assert case["expected_workflow_status"] == "REVIEW", "Got REVIEW status unexpectedly"
        return

    # 5. Assert Action Plan
    if result.action_plan is None:
        if case["expected_workflow_status"] == "GROUNDING_REVIEW":
            # This means it might have failed grounding before creating an action plan, 
            # but wait - action plan is created in planning node. 
            # If it's missing, it's a bug.
            pass
        pytest.fail(f"Action plan is missing. Error: {result.error}")

    actual_action = result.action_plan.action.value
    expected_action = case["expected_action"]
    
    if actual_action != expected_action:
        pytest.fail(f"Action plan failed. Expected {expected_action}, got {actual_action}. Reasoning: {result.action_plan.reasoning}")

    # 6. Assert Safety Routing (Approval Requirement)
    actual_approval_req = result.action_plan.requires_approval
    expected_approval_req = case["expected_approval_requirement"]
    
    if actual_approval_req != expected_approval_req:
        pytest.fail(f"Safety routing failed. Expected requires_approval={expected_approval_req}, got {actual_approval_req}")

    # 7. Assert Workflow Status
    actual_workflow_status = result.workflow_status
    expected_workflow_status = case["expected_workflow_status"]
    
    if actual_workflow_status != expected_workflow_status:
        pytest.fail(f"Workflow status failed. Expected {expected_workflow_status}, got {actual_workflow_status}. Error: {result.error}")

