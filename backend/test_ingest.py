import os
import sys

# Ensure backend directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.workers.tasks import ingest_all_gmail

if __name__ == "__main__":
    print("Triggering email ingestion...")
    result = ingest_all_gmail.apply()
    print("Ingestion result:", result.result)
