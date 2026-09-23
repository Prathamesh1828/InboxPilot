from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class TelegramConnection(Base):
    __tablename__ = "telegram_connections"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    telegram_user_id = Column(String(255), nullable=True)
    telegram_chat_id = Column(String(255), unique=True, nullable=True, index=True)

    connection_token = Column(String(255), unique=True, nullable=False, index=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=False)

    connected_at = Column(DateTime(timezone=True), nullable=True)

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
