from sqlalchemy.orm import Session

from app.models.telegram_connection import TelegramConnection


def get_telegram_connection_by_user_id(
    db: Session,
    user_id: str,
) -> TelegramConnection | None:
    return (
        db.query(TelegramConnection)
        .filter(TelegramConnection.user_id == user_id)
        .first()
    )


def get_telegram_connection_by_token(
    db: Session,
    token: str,
) -> TelegramConnection | None:
    return (
        db.query(TelegramConnection)
        .filter(TelegramConnection.connection_token == token)
        .first()
    )


def get_telegram_connection_by_chat_id(
    db: Session,
    chat_id: str,
) -> TelegramConnection | None:
    return (
        db.query(TelegramConnection)
        .filter(TelegramConnection.telegram_chat_id == chat_id)
        .first()
    )


def create_telegram_connection(
    db: Session,
    user_id: str,
    connection_token: str,
    token_expires_at,
) -> TelegramConnection:
    connection = TelegramConnection(
        user_id=user_id,
        connection_token=connection_token,
        token_expires_at=token_expires_at,
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


def update_telegram_connection(
    db: Session,
    connection: TelegramConnection,
) -> TelegramConnection:
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


def delete_telegram_connection(
    db: Session,
    connection: TelegramConnection,
) -> None:
    db.delete(connection)
    db.commit()

def delete_telegram_connection_by_user(
    db: Session,
    user_id: str,
) -> bool:
    connection = get_telegram_connection_by_user_id(db, user_id)
    if not connection:
        return False
    db.delete(connection)
    db.commit()
    return True
