from app.db.base import Base
from app.db.database import engine
from app.models.email import Email
from app.models.google_account import GoogleAccount
from app.models.bill import Bill
from app.models.action_approval import ActionApproval
from app.models.telegram_connection import TelegramConnection


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")