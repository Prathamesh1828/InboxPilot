import logging
from typing import Any
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.integrations.telegram.bot import (
    answer_callback_query,
    edit_message_text,
    is_telegram_configured,
)
from app.repositories.telegram_connection_repository import get_telegram_connection_by_chat_id
from app.services.approval_execution_service import ApprovalExecutionService
from app.services.approval_service import ApprovalService
from app.services.telegram_connection_service import TelegramConnectionService
from app.integrations.telegram.bot import httpx
from app.core.settings import settings
from app.core.limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/telegram",
    tags=["Telegram"],
)


def _send_text_message(chat_id: str, text: str):
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    try:
        httpx.post(url, json=payload, timeout=5.0)
    except Exception as e:
        logger.error("Failed to send text message: %s", e)


@router.post("/webhook")
@limiter.limit("100/minute")
async def telegram_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Handle incoming Telegram webhooks:
    - /start <token> messages to link accounts
    - callback queries for approve/reject inline buttons
    """
    if not is_telegram_configured():
        logger.warning("Received Telegram webhook but Telegram is not configured.")
        return {"status": "ignored"}

    # Verify Telegram Secret Token if configured
    if settings.telegram_webhook_secret:
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret_token != settings.telegram_webhook_secret:
            logger.warning("Invalid Telegram webhook secret token.")
            return {"status": "unauthorized"}

    data = await request.json()

    # 1. Handle standard messages (/start <token>)
    if "message" in data:
        message = data["message"]
        text = message.get("text", "")
        chat_id = str(message.get("chat", {}).get("id"))
        user_id = str(message.get("from", {}).get("id"))

        if text.startswith("/start "):
            token = text.split(" ", 1)[1].strip()
            try:
                TelegramConnectionService.connect_account(
                    db=db,
                    token=token,
                    telegram_user_id=user_id,
                    telegram_chat_id=chat_id,
                )
                _send_text_message(chat_id, "✅ *Successfully connected to InboxPilot!*\nYou will now receive approval notifications here.")
            except ValueError as e:
                _send_text_message(chat_id, f"❌ *Connection failed:*\n{e}")
            except Exception as e:
                logger.error("Error connecting Telegram account: %s", e)
                _send_text_message(chat_id, "❌ *An unexpected error occurred.*")
        
        return {"status": "ok"}

    # 2. Handle callback queries (Approve/Reject)
    if "callback_query" not in data:
        return {"status": "ok"}

    callback_query = data["callback_query"]
    query_id = callback_query.get("id")
    callback_data = callback_query.get("data", "")
    message = callback_query.get("message", {})
    message_id = message.get("message_id")
    chat_id = str(message.get("chat", {}).get("id"))
    original_text = message.get("text", "")

    if not callback_data.startswith(("approve_", "reject_")):
        if query_id:
            answer_callback_query(query_id, "Unknown action.")
        return {"status": "ok"}

    action, approval_id_str = callback_data.split("_", 1)

    # Security check: Ensure the user clicking the button is the one who owns the chat connection
    user_id = str(callback_query.get("from", {}).get("id"))
    connection = get_telegram_connection_by_chat_id(db, chat_id=chat_id)
    
    if not connection or connection.telegram_user_id != user_id:
        logger.warning(
            "Unauthorized approval attempt. Expected user %s, got %s in chat %s",
            connection.telegram_user_id if connection else "None",
            user_id,
            chat_id
        )
        if query_id:
            answer_callback_query(query_id, "You are not authorized to approve this.", show_alert=True)
        return {"status": "ok"}

    try:
        approval_id = int(approval_id_str)
    except ValueError:
        if query_id:
            answer_callback_query(query_id, "Invalid approval ID.")
        return {"status": "ok"}

    try:
        if action == "approve":
            ApprovalService.approve(db=db, approval_id=approval_id)
            from app.workers.tasks import execute_approved_action
            execute_approved_action.delay(approval_id=approval_id)
            
            status_text = "✅ Approved. Executing..."
            alert_text = f"Action {approval_id} approved. Execution started."
            
        elif action == "reject":
            ApprovalService.reject(db=db, approval_id=approval_id)
            
            status_text = "❌ Rejected"
            alert_text = f"Action {approval_id} rejected."
        
        else:
            return {"status": "ok"}

        if query_id:
            answer_callback_query(query_id, alert_text)

        if message_id and chat_id:
            # Strip out the question and append the result status
            new_text = original_text.replace("Do you approve this action?", "")
            new_text += f"\n*Status:* {status_text}"
            edit_message_text(chat_id, message_id, new_text)

    except ValueError as exc:
        # This catches already-approved or not-found cases
        logger.warning("Telegram webhook error for approval %d: %s", approval_id, exc)
        if query_id:
            answer_callback_query(query_id, str(exc), show_alert=True)
            
        if message_id and chat_id:
            new_text = original_text.replace("Do you approve this action?", "")
            new_text += f"\n*Status:* ⚠️ Error: {str(exc)}"
            edit_message_text(chat_id, message_id, new_text)

    except Exception as exc:
        logger.error("Unexpected error in Telegram webhook for approval %d: %s", approval_id, exc)
        if query_id:
            answer_callback_query(query_id, "An unexpected error occurred.", show_alert=True)

    return {"status": "ok"}
