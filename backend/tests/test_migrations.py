import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from alembic.migration import MigrationContext

from app.db.base import Base

def test_alembic_migrations():
    """Test that alembic can upgrade an empty database to head."""
    # Create an in-memory SQLite database
    db_url = "sqlite:///:memory:"
    engine = create_engine(db_url)
    
    # Configure Alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    
    # Run the upgrade
    # Note: alembic commands require the connection to be passed if we are using memory db
    # otherwise it opens a new connection to memory which is empty.
    with engine.begin() as connection:
        alembic_cfg.attributes['connection'] = connection
        command.upgrade(alembic_cfg, "head")
        
        # Verify tables exist
        context = MigrationContext.configure(connection)
        
        # Get table names directly from sqlite_master to avoid deprecated get_table_names
        result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        
        assert "emails" in tables
        assert "google_accounts" in tables
        assert "action_approvals" in tables
        assert "bills" in tables
        assert "reminders" in tables
        assert "telegram_connections" in tables
        assert "audit_events" in tables

def test_unique_pending_approval_constraint():
    """Test that the partial index prevents multiple PENDING approvals for the same email."""
    db_url = "sqlite:///:memory:"
    engine = create_engine(db_url)
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    
    with engine.begin() as connection:
        alembic_cfg.attributes['connection'] = connection
        command.upgrade(alembic_cfg, "head")
        
    Session = sessionmaker(bind=engine)
    db = Session()
    
    from app.models.email import Email
    from app.models.action_approval import ActionApproval
    from datetime import datetime, timezone
    import sqlalchemy.exc
    
    # 1. Create an email
    email = Email(
        provider_message_id="test-msg-123",
        sender="sender@test.com",
        recipients=[],
        body="test",
        received_at=datetime.now(timezone.utc),
        status="PENDING",
    )
    db.add(email)
    db.commit()
    
    # 2. Add first pending approval
    approval1 = ActionApproval(
        email_id=email.id,
        action="TEST",
        action_plan={},
        status="PENDING"
    )
    db.add(approval1)
    db.commit()
    
    # 3. Add second pending approval for same email - SHOULD FAIL
    approval2 = ActionApproval(
        email_id=email.id,
        action="TEST2",
        action_plan={},
        status="PENDING"
    )
    db.add(approval2)
    
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.commit()
        
    db.rollback()
    
    # 4. Change status of first approval
    approval1.status = "APPROVED"
    db.commit()
    
    # 5. Add second pending approval - SHOULD SUCCEED NOW
    approval3 = ActionApproval(
        email_id=email.id,
        action="TEST3",
        action_plan={},
        status="PENDING"
    )
    db.add(approval3)
    db.commit()
