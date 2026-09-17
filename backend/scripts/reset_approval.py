import argparse
from app.db.database import SessionLocal
from app.repositories.action_approval_repository import update_action_approval_status

def main():
    parser = argparse.ArgumentParser(description="Reset an approval to PENDING state.")
    parser.add_argument("approval_id", type=int, help="The ID of the approval to reset.")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        updated = update_action_approval_status(
            db=db,
            approval_id=args.approval_id,
            status="PENDING",
        )
        if updated:
            print(f"Approval {args.approval_id} has been reset to PENDING.")
        else:
            print(f"Approval {args.approval_id} not found.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
