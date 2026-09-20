from unittest.mock import patch, MagicMock
from app.integrations.telegram.bot import send_approval_notification
from app.core.settings import settings

def test_send_approval_notification_includes_gmail_url():
    # Setup mock configuration so the function actually executes
    original_token = settings.telegram_bot_token
    original_username = settings.telegram_bot_username
    settings.telegram_bot_token = "fake_token"
    settings.telegram_bot_username = "fake_username"

    with patch("app.integrations.telegram.bot.httpx.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Call with an identifier
        send_approval_notification(
            chat_id="12345",
            approval_id=99,
            action="CREATE_CALENDAR_EVENT",
            email_subject="Test Subject",
            risk_level="MEDIUM",
            gmail_thread_id="thread123"
        )

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        payload = kwargs["json"]
        
        keyboard = payload["reply_markup"]["inline_keyboard"]
        
        # Should have two rows now: URL row, then Action row
        assert len(keyboard) == 2
        
        # Check URL button
        url_button = keyboard[0][0]
        assert url_button["text"] == "📧 Open Email"
        assert url_button["url"] == "https://mail.google.com/mail/u/0/#all/thread123"
        
        # Check action buttons
        action_row = keyboard[1]
        assert action_row[0]["text"] == "✅ Approve"
        assert action_row[1]["text"] == "❌ Reject"

    # Restore config
    settings.telegram_bot_token = original_token
    settings.telegram_bot_username = original_username
