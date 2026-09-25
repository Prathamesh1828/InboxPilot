import sys
import os

sys.path.append(os.path.abspath('backend'))
from app.db.database import SessionLocal
from app.models.email import Email

db = SessionLocal()
emails = db.query(Email).limit(5).all()

for e in emails:
    print(f"ID: {e.id}, msg_id: {e.provider_message_id}, thread: {e.thread_id}")
