import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.settings import settings
from app.repositories.telegram_connection_repository import (
    create_telegram_connection,
    get_telegram_connection_by_chat_id,
    get_telegram_connection_by_token,
    get_telegram_connection_by_user_id,
    update_telegram_connection,
)


class TelegramConnectionService:
    @staticmethod
    def generate_connection_link(
        db: Session,
        user_id: str,
    ) -> str:
        """
        Generate a secure, single-use, expiring connection token for a user.
        Returns the Telegram deep link to start the bot.
        """
        if not settings.telegram_bot_username:
            raise ValueError("TELEGRAM_BOT_USERNAME is not configured.")

        # Check if they already have an active connection or pending token
        connection = get_telegram_connection_by_user_id(db, user_id=user_id)
        
        # If they are already connected, we don't strictly need to generate a new token
        # but sometimes users want to re-connect or change chats.
        # For this implementation, we will update the existing connection's token.
        
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        if connection:
            connection.connection_token = token  # type: ignore
            connection.token_expires_at = expires_at  # type: ignore
            connection.connected_at = None  # type: ignore
            update_telegram_connection(db, connection)
        else:
            create_telegram_connection(
                db=db,
                user_id=user_id,
                connection_token=token,
                token_expires_at=expires_at,
            )

        return f"https://t.me/{settings.telegram_bot_username}?start={token}"

    @staticmethod
    def connect_account(
        db: Session,
        token: str,
        telegram_user_id: str,
        telegram_chat_id: str,
    ) -> None:
        """
        Process a /start <token> command to link a Telegram chat to a user account.
        """
        connection = get_telegram_connection_by_token(db, token=token)

        if not connection:
            raise ValueError("Invalid or unrecognized token.")

        if connection.connected_at is not None:
            raise ValueError("This token has already been used.")

        if datetime.now(timezone.utc) > connection.token_expires_at:
            raise ValueError("This token has expired.")

        # Prevent one Telegram account from being silently linked to multiple users
        existing_chat_connection = get_telegram_connection_by_chat_id(
            db=db, chat_id=telegram_chat_id
        )

        if existing_chat_connection and existing_chat_connection.id != connection.id:
            raise ValueError("This Telegram account is already linked to another user.")

        connection.telegram_user_id = telegram_user_id  # type: ignore
        connection.telegram_chat_id = telegram_chat_id  # type: ignore
        connection.connected_at = datetime.now(timezone.utc)  # type: ignore

        update_telegram_connection(db, connection)
