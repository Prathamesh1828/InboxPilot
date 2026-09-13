from datetime import date

from sqlalchemy.orm import Session

from app.repositories.bill_repository import (
    create_bill,
    get_bill_by_email_id,
)
from app.schemas.action_plan import ActionPlan, ActionType


class ActionExecutor:
    """
    Executes InboxPilot actions.

    LOG_BILL currently writes to PostgreSQL.
    Other actions remain in dry-run mode.
    """

    def execute(
        self,
        plan: ActionPlan,
        db: Session | None = None,
        email_id: int | None = None,
    ) -> str:

        if plan.action == ActionType.LOG_BILL:
            return self._log_bill(
                plan=plan,
                db=db,
                email_id=email_id,
            )

        if plan.action == ActionType.CREATE_REMINDER:
            return self._create_reminder(plan)

        if plan.action == ActionType.ARCHIVE:
            return self._archive(plan)

        if plan.action == ActionType.NO_ACTION:
            return "No action required."

        raise ValueError(
            f"Action {plan.action} cannot be executed automatically."
        )

    @staticmethod
    def _log_bill(
        plan: ActionPlan,
        db: Session | None,
        email_id: int | None,
    ) -> str:

        if db is None:
            raise ValueError(
                "Database session is required to log a bill."
            )

        if email_id is None:
            raise ValueError(
                "Email ID is required to log a bill."
            )

        # -------------------------------------------------
        # Idempotency check
        # -------------------------------------------------

        existing_bill = get_bill_by_email_id(
            db=db,
            email_id=email_id,
        )

        if existing_bill is not None:
            return (
                f"Bill already exists. "
                f"Bill ID: {existing_bill.id}."
            )

        # -------------------------------------------------
        # Extract parameters
        # -------------------------------------------------

        amount = plan.parameters.get("amount")
        currency = plan.parameters.get("currency")
        vendor = plan.parameters.get("vendor")
        due_date = plan.parameters.get("due_date")

        # -------------------------------------------------
        # Validate required parameters
        # -------------------------------------------------

        if amount is None:
            raise ValueError(
                "Bill amount is required."
            )

        if currency is None:
            raise ValueError(
                "Bill currency is required."
            )

        # -------------------------------------------------
        # Convert due date
        # -------------------------------------------------

        parsed_due_date: date | None = None

        if due_date is not None:
            try:
                parsed_due_date = date.fromisoformat(
                    str(due_date)
                )
            except ValueError as exc:
                raise ValueError(
                    f"Invalid bill due date: {due_date}"
                ) from exc

        # -------------------------------------------------
        # Create bill
        # -------------------------------------------------

        bill = create_bill(
            db=db,
            email_id=email_id,
            amount=float(amount),
            currency=str(currency),
            vendor=str(vendor) if vendor is not None else None,
            due_date=parsed_due_date,
        )

        return (
            f"Bill logged successfully. "
            f"Bill ID: {bill.id}, "
            f"Amount: {bill.currency} {bill.amount}, "
            f"Due date: {bill.due_date}."
        )

    @staticmethod
    def _create_reminder(
        plan: ActionPlan,
    ) -> str:

        reminder_text = plan.parameters.get(
            "reminder_text"
        )

        reminder_date = plan.parameters.get(
            "reminder_date"
        )

        return (
            f"DRY RUN: Would create reminder "
            f"'{reminder_text}' "
            f"for {reminder_date}."
        )

    @staticmethod
    def _archive(
        plan: ActionPlan,
    ) -> str:

        return (
            "DRY RUN: Would archive the email."
        )