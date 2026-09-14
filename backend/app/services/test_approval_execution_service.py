from app.db.database import SessionLocal
from app.services.approval_execution_service import (
    ApprovalExecutionService,
)


def main() -> None:
    print("Testing Approval Execution Service")
    print("=" * 60)

    db = SessionLocal()

    try:
        service = ApprovalExecutionService()

        # Approval 2 was previously REJECTED.
        # It must never be executed.
        try:
            service.execute_approved(
                db=db,
                approval_id=2,
            )
        except ValueError as exc:
            print()
            print("REJECTED ACTION TEST")
            print("-" * 60)
            print(exc)

    finally:
        db.close()


if __name__ == "__main__":
    main()