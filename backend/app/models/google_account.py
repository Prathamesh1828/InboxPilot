from datetime import datetime, timezone

from sqlalchemy import BigInteger, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GoogleAccount(Base):
    __tablename__ = "google_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True, # temporarily nullable for existing data
        index=True,
    )

    # Google account information
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    google_user_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    # OAuth credentials
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Gmail sync checkpoint — stores the Gmail historyId so that
    # each polling cycle only fetches messages that arrived after
    # the previous successful sync.
    last_history_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )