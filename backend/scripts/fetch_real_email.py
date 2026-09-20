import sys
import os
from datetime import datetime, timezone

# Add the backend directory to sys.path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.models.google_account import GoogleAccount
from app.integrations.gmail.client import get_gmail_service
from app.services.email_service import ingest_email
from app.workers.tasks import process_email_pipeline

def main():
    db = SessionLocal()
    account = db.query(GoogleAccount).first()
    
    if not account:
        print("No Google account found. Please connect your Gmail.")
        return

    print("Fetching the latest real email from your Gmail inbox...")
    service = get_gmail_service(db, account)
    
    # Fetch latest 1 message
    results = service.users().messages().list(userId="me", maxResults=1).execute()
    messages = results.get("messages", [])
    
    if not messages:
        print("No messages found in your inbox.")
        return

    message_id = messages[0]["id"]
    msg = service.users().messages().get(userId="me", id=message_id).execute()
    
    thread_id = msg.get("threadId")
    headers = msg.get("payload", {}).get("headers", [])
    
    subject = "No Subject"
    sender = "unknown@example.com"
    
    for header in headers:
        if header["name"].lower() == "subject":
            subject = header["value"]
        elif header["name"].lower() == "from":
            sender = header["value"]
            
    snippet = msg.get("snippet", "")
    
    print(f"\nFound real email!")
    print(f"Subject: {subject}")
    print(f"From: {sender}")
    print(f"Thread ID: {thread_id}")
    
    # Ingest into InboxPilot
    email = ingest_email(
        db=db,
        provider_message_id=message_id,
        thread_id=thread_id,
        sender=sender,
        recipients=["me@example.com"],
        subject=subject,
        body=snippet, # Using snippet for testing
        received_at=datetime.now(timezone.utc),
    )
    
    print(f"\nIngested into InboxPilot as Email ID: {email.id}")
    
    # Queue for processing
    process_email_pipeline.delay(email.id)
    print(f"Queued Email {email.id} for processing!")
    print("Check your Telegram for the approval notification.")

if __name__ == "__main__":
    main()
