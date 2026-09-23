import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.repositories.google_account_repository import get_google_account_by_user, delete_google_account
from app.repositories.email_repository import delete_emails_by_user
from app.repositories.telegram_connection_repository import get_telegram_connection_by_user_id, delete_telegram_connection_by_user
from app.integrations.telegram.bot import is_telegram_configured

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
    dependencies=[Depends(get_current_user)]
)

@router.get("")
def get_integrations_status(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the status of all integrations for the current user.
    """
    # Google (Gmail / Calendar)
    google_account = get_google_account_by_user(db, user.id)
    google_status = {
        "status": "CONNECTED" if google_account else "NOT_CONNECTED",
        "email": google_account.email if google_account else None,
    }

    # Telegram
    telegram_conn = get_telegram_connection_by_user_id(db, user.id)
    
    # We can fetch the username using Telegram API if we stored it, 
    # but currently we don't store the username, only chat_id/user_id.
    telegram_status = {
        "status": "CONNECTED" if telegram_conn and telegram_conn.connected_at else "NOT_CONNECTED",
        "account": f"Chat ID: {telegram_conn.telegram_chat_id}" if telegram_conn and telegram_conn.telegram_chat_id else None,
    }

    # If they generated a token but haven't sent the /start command yet:
    if telegram_conn and not telegram_conn.connected_at:
        telegram_status["status"] = "CONNECTING"

    return {
        "gmail": google_status,
        "calendar": google_status,  # Inherits Google account status
        "telegram": telegram_status,
        "telegram_configured": is_telegram_configured(),
    }


@router.post("/gmail/disconnect")
def disconnect_gmail(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect Google account (Gmail & Calendar) for the current user.
    """
    success = delete_google_account(db, user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Google account not connected.")
    
    # Clear emails associated with the disconnected account
    deleted_count = delete_emails_by_user(db, user.id)
    
    logger.info(f"User {user.id} disconnected Google account. Deleted {deleted_count} emails.")
    return {"status": "success", "message": "Google account disconnected and emails cleared."}


@router.post("/telegram/disconnect")
def disconnect_telegram(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect Telegram notifications for the current user.
    """
    success = delete_telegram_connection_by_user(db, user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Telegram account not connected.")
    
    logger.info(f"User {user.id} disconnected Telegram.")
    return {"status": "success", "message": "Telegram disconnected."}

@router.get("/telegram/connect")
def connect_telegram(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.services.telegram_connection_service import TelegramConnectionService
    try:
        link = TelegramConnectionService.generate_connection_link(db, user.id)
        return {"link": link}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
