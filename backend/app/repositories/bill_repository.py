from datetime import date

from sqlalchemy.orm import Session

from app.models.bill import Bill


def get_bill_by_email_id(
    db: Session,
    email_id: int,
) -> Bill | None:
    return (
        db.query(Bill)
        .filter(Bill.email_id == email_id)
        .first()
    )


def create_bill(
    db: Session,
    email_id: int,
    amount: float,
    currency: str,
    vendor: str | None,
    due_date: date | None,
) -> Bill:
    bill = Bill(
        email_id=email_id,
        amount=amount,
        currency=currency,
        vendor=vendor,
        due_date=due_date,
    )

    db.add(bill)
    db.commit()
    db.refresh(bill)

    return bill