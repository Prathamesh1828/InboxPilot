import os
import sys

# Add the backend directory to Python path so 'app' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models.google_account import GoogleAccount
from app.services.telegram_connection_service import TelegramConnectionService
from app.db.base import Base
from dotenv import load_dotenv

# Load env variables
load_dotenv()

def main():
    print("========================================")
    print(" Telegram Connection Link Generator")
    print("========================================\n")
    
    # Initialize DB
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Get the first user (InboxPilot single-user setup)
        user = db.query(GoogleAccount).first()
        
        if not user:
            print("[X] No Google Account found in the database.")
            print("Please sign in with Google first before linking Telegram.")
            return
            
        print(f"Generating link for user: {user.email}")
        
        # Generate link
        # user.id is typed as Column[int] by some linters, so we explicitly cast or ignore
        link = TelegramConnectionService.generate_connection_link(db=db, user_id=int(user.id)) # type: ignore
        
        print("\n[OK] Link generated successfully!\n")
        print("Click the link below to open Telegram and start the bot:")
        print(f"-> {link} <-")
        print("\nNote: This link will expire in 15 minutes and can only be used once.")
        
    except Exception as e:
        print(f"[X] Error generating link: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
