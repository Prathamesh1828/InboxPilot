from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text

from app.db.base import Base


class GoogleAccount(Base):
    __tablename__ = "google_accounts"

    id = Column(Integer, primary_key=True, index=True)

    # Google account information
    email = Column(String(255), unique=True, nullable=False, index=True)
    google_user_id = Column(String(255), unique=True, nullable=True)

    # OAuth credentials
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )