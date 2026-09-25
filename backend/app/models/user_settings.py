from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    
    # Notifications
    notify_email_approvals: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_email_completions: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_email_failures: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_email_alerts: Mapped[bool] = mapped_column(Boolean, default=True)
    
    notify_telegram_approvals: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_telegram_completions: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_telegram_failures: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Automation
    automation_mode: Mapped[str] = mapped_column(String, default="ASSISTED")
    confidence_threshold: Mapped[int] = mapped_column(Integer, default=90)
    pause_all_automations: Mapped[bool] = mapped_column(Boolean, default=False)
    
    approval_required_sending: Mapped[bool] = mapped_column(Boolean, default=True)
    approval_required_forwarding: Mapped[bool] = mapped_column(Boolean, default=True)
    approval_required_deleting: Mapped[bool] = mapped_column(Boolean, default=True)
    approval_required_calendar: Mapped[bool] = mapped_column(Boolean, default=True)
    approval_required_other: Mapped[bool] = mapped_column(Boolean, default=True)

    # Appearance
    theme: Mapped[str] = mapped_column(String, default="SYSTEM")
    density: Mapped[str] = mapped_column(String, default="COMFORTABLE")

    # Relationship back to user
    user = relationship("User", back_populates="settings")
