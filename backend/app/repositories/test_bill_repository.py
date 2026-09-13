from datetime import date

import app.models

from app.db.database import SessionLocal
from app.repositories.bill_repository import create_bill

def main() -> None:
    print("Testing Bill Repository")
    print("=" * 60)

    db = SessionLocal()

    try:
        bill = create_bill(
            db=db,
            email_id=1,
            amount=2450,
            currency="INR",
            vendor="Electricity",
            due_date=date(2026, 9, 20),
        )

        print()
        print("BILL CREATED")
        print("-" * 60)
        print(f"ID:         {bill.id}")
        print(f"Email ID:   {bill.email_id}")
        print(f"Amount:     {bill.amount}")
        print(f"Currency:   {bill.currency}")
        print(f"Vendor:     {bill.vendor}")
        print(f"Due Date:   {bill.due_date}")

    finally:
        db.close()


if __name__ == "__main__":
    main()