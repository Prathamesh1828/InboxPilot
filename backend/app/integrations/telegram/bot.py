import logging
import httpx

from app.core.settings import settings

logger = logging.getLogger(__name__)


def is_telegram_configured() -> bool:
    return bool(settings.telegram_bot_token and settings.telegram_bot_username)


def send_approval_notification(
    chat_id: str,
    approval_id: int,
    action: str,
    email_subject: str | None,
    risk_level: str,
    gmail_thread_id: str | None = None,
    gmail_message_id: str | None = None,
) -> int | None:
    """
    Send an approval notification to Telegram with inline
    Approve and Reject buttons, and a link to the original email.
    """
    if not is_telegram_configured():
        logger.info("Telegram not configured, skipping notification for approval %d", approval_id)
        return None

    import html
    
    subject = email_subject or "(No subject)"
    escaped_subject = html.escape(subject)
    
    text = (
        f"🚨 <b>Action Approval Required</b>\n\n"
        f"<b>Action:</b> {action}\n"
        f"<b>Risk:</b> {risk_level}\n"
        f"<b>Email:</b> {escaped_subject}\n\n"
        f"Do you approve this action?"
    )

    # Use thread_id if available, otherwise fallback to message_id
    identifier = gmail_thread_id or gmail_message_id
    
    inline_keyboard = []
    
    if identifier:
        gmail_url = f"https://mail.google.com/mail/u/0/#all/{identifier}"
        inline_keyboard.append([{"text": "📧 Open Email", "url": gmail_url}])
        
    inline_keyboard.append([
        {"text": "✅ Approve", "callback_data": f"approve_{approval_id}"},
        {"text": "❌ Reject", "callback_data": f"reject_{approval_id}"}
    ])

    keyboard = {
        "inline_keyboard": inline_keyboard
    }

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": keyboard
    }

    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        logger.info("Sent Telegram notification for approval %d", approval_id)
        data = response.json()
        return data.get("result", {}).get("message_id")
    except Exception as e:
        logger.error("Failed to send Telegram notification: %s", e)
        return None


def answer_callback_query(
    callback_query_id: str,
    text: str,
    show_alert: bool = False
) -> None:
    """
    Answer the callback query so the loading state on the button stops.
    """
    if not is_telegram_configured():
        return

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/answerCallbackQuery"
    payload = {
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": show_alert
    }

    try:
        httpx.post(url, json=payload, timeout=5.0)
    except Exception as e:
        logger.error("Failed to answer callback query: %s", e)


def edit_message_text(
    chat_id: str,
    message_id: int,
    text: str,
) -> None:
    """
    Edit the original message to remove the buttons once an action is taken.
    """
    if not is_telegram_configured():
        return

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        httpx.post(url, json=payload, timeout=5.0)
    except Exception as e:
        logger.error("Failed to edit message text: %s", e)
