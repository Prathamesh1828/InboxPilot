from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class UserSettingsBase(BaseModel):
    notify_email_approvals: bool = True
    notify_email_completions: bool = False
    notify_email_failures: bool = True
    notify_email_alerts: bool = True
    
    notify_telegram_approvals: bool = True
    notify_telegram_completions: bool = False
    notify_telegram_failures: bool = True
    
    automation_mode: str = "ASSISTED"
    confidence_threshold: int = Field(default=90, ge=0, le=100)
    pause_all_automations: bool = False
    
    approval_required_sending: bool = True
    approval_required_forwarding: bool = True
    approval_required_deleting: bool = True
    approval_required_calendar: bool = True
    approval_required_other: bool = True
    
    theme: str = "SYSTEM"
    density: str = "COMFORTABLE"

class UserSettingsUpdate(BaseModel):
    # Notifications
    notify_email_approvals: Optional[bool] = None
    notify_email_completions: Optional[bool] = None
    notify_email_failures: Optional[bool] = None
    notify_email_alerts: Optional[bool] = None
    
    notify_telegram_approvals: Optional[bool] = None
    notify_telegram_completions: Optional[bool] = None
    notify_telegram_failures: Optional[bool] = None
    
    # Automation
    automation_mode: Optional[str] = None
    confidence_threshold: Optional[int] = Field(None, ge=0, le=100)
    pause_all_automations: Optional[bool] = None
    
    approval_required_sending: Optional[bool] = None
    approval_required_forwarding: Optional[bool] = None
    approval_required_deleting: Optional[bool] = None
    approval_required_calendar: Optional[bool] = None
    approval_required_other: Optional[bool] = None
    
    # Appearance
    theme: Optional[str] = None
    density: Optional[str] = None

class UserSettingsResponse(UserSettingsBase):
    user_id: str

    model_config = ConfigDict(from_attributes=True)

class ProfileUpdate(BaseModel):
    name: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str
