import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.abspath('backend'), '.env'))

sys.path.append(os.path.abspath('backend'))
from app.db.database import SessionLocal
from app.models.email import Email
from sqlalchemy import func

db = SessionLocal()
statuses = db.query(Email.status, func.count(Email.id)).group_by(Email.status).all()
print("Email statuses:", statuses)
