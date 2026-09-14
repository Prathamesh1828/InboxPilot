from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.integrations.google_calendar.client import create_calendar_event
from app.models.google_account import GoogleAccount
from app.repositories.bill_repository import (
    create_bill,
    get_bill_by_email_id,
)
from app.repositories.reminder_repository import (
    create_reminder,
    get_reminder_by_email_id,
)
from app.schemas.action_plan import (
    ActionPlan,
    ActionType,
    BillActionPlan,
    CalendarActionPlan,
    ReminderActionPlan,
)
from app.services.datetime_parser import parse_calendar_datetime


_DATE_FORMATS = (
    "%Y-%m-%d",
    "%B %d, %Y",
    "%b %d, %Y",
    "%d %B %Y",
    "%d %b %Y",
)


def _parse_date(value: str) -> date:
    """Parse a date string using several common formats."""
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    raise ValueError(
        f"Unrecognised date format: {value}"
    )


class ActionExecutor:
    """
    Executes InboxPilot actions.

    LOG_BILL and CREATE_REMINDER write to PostgreSQL.
    CREATE_CALENDAR_EVENT creates a real Google Calendar event.
    Other actions remain in dry-run mode.
    """

    def execute(
        self,
        plan: ActionPlan,
        db: Session | None = None,
        email_id: int | None = None,
    ) -> str:

        if isinstance(plan, BillActionPlan):
            return self._log_bill(
                plan=plan,
                db=db,
                email_id=email_id,
            )

        if isinstance(plan, ReminderActionPlan):
            return self._create_reminder(
                plan=plan,
                db=db,
                email_id=email_id,
            )

        if isinstance(plan, CalendarActionPlan):
            return self._create_calendar_event(
                plan=plan,
                db=db,
            )

        if plan.action == ActionType.ARCHIVE:
            return self._archive()

        if plan.action == ActionType.NO_ACTION:
            return "No action required."

        raise ValueError(
            f"Action {plan.action} cannot be executed automatically."
        )

    @staticmethod
    def _log_bill(
        plan: BillActionPlan,
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

        existing_bill = get_bill_by_email_id(
            db=db,
            email_id=email_id,
        )

        if existing_bill is not None:
            return (
                f"Bill already exists. "
                f"Bill ID: {existing_bill.id}."
            )

        parameters = plan.parameters

        amount = parameters.amount
        currency = parameters.currency
        vendor = parameters.vendor
        due_date = parameters.due_date

        parsed_due_date: date | None = None

        if due_date is not None:
            try:
                parsed_due_date = _parse_date(due_date)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid bill due date: {due_date}"
                ) from exc

        bill = create_bill(
            db=db,
            email_id=email_id,
            amount=amount,
            currency=currency,
            vendor=vendor,
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
        plan: ReminderActionPlan,
        db: Session | None,
        email_id: int | None,
    ) -> str:

        if db is None:
            raise ValueError(
                "Database session is required to create a reminder."
            )

        if email_id is None:
            raise ValueError(
                "Email ID is required to create a reminder."
            )

        parameters = plan.parameters

        reminder_text = parameters.reminder_text
        reminder_date = parameters.reminder_date

        if not reminder_text:
            raise ValueError(
                "Reminder text is required."
            )

        if reminder_date is None:
            raise ValueError(
                "Reminder date is required."
            )

        try:
            parsed_reminder_date = _parse_date(
                reminder_date
            )
        except ValueError as exc:
            raise ValueError(
                f"Invalid reminder date: {reminder_date}"
            ) from exc

        existing_reminder = get_reminder_by_email_id(
            db=db,
            email_id=email_id,
        )

        if existing_reminder is not None:
            return (
                f"Reminder already exists. "
                f"Reminder ID: {existing_reminder.id}."
            )

        reminder = create_reminder(
            db=db,
            email_id=email_id,
            reminder_text=reminder_text,
            reminder_date=parsed_reminder_date,
        )

        return (
            f"Reminder created successfully. "
            f"Reminder ID: {reminder.id}, "
            f"Text: '{reminder.reminder_text}', "
            f"Date: {reminder.reminder_date}."
        )

    @staticmethod
    def _create_calendar_event(
        plan: CalendarActionPlan,
        db: Session | None,
    ) -> str:

        if db is None:
            raise ValueError(
                "Database session is required to create a calendar event."
            )

        parameters = plan.parameters

        if not parameters.start_time:
            raise ValueError(
                "Calendar event start time is required."
            )

        if not parameters.end_time:
            raise ValueError(
                "Calendar event end time is required."
            )

        reference_time = datetime.now(timezone.utc)

        try:
            start_time = parse_calendar_datetime(
                value=parameters.start_time,
                reference_time=reference_time,
            )
        except ValueError as exc:
            raise ValueError(
                f"Invalid calendar event start time: "
                f"{parameters.start_time}"
            ) from exc

        try:
            end_time = parse_calendar_datetime(
                value=parameters.end_time,
                reference_time=reference_time,
            )
        except ValueError as exc:
            raise ValueError(
                f"Invalid calendar event end time: "
                f"{parameters.end_time}"
            ) from exc

        if end_time <= start_time:
            raise ValueError(
                "Calendar event end time must be after start time."
            )

        account = (
            db.query(GoogleAccount)
            .first()
        )

        if account is None:
            raise ValueError(
                "No connected Google account found."
            )

        event_id = create_calendar_event(
            db=db,
            account=account,
            title=parameters.title,
            start_time=start_time,
            end_time=end_time,
            description=parameters.description,
        )

        return (
            f"Calendar event created successfully. "
            f"Google Event ID: {event_id}."
        )

    @staticmethod
    def _archive() -> str:
        return "DRY RUN: Would archive the email."