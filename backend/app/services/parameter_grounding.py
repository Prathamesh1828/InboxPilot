import re
from datetime import date

from app.schemas.action_plan import ActionPlan


def validate_action_parameters(
    plan: ActionPlan,
    subject: str | None,
    body: str,
) -> list[str]:
    """
    Check whether important action parameters
    are grounded in the original email.

    Returns a list of grounding errors.
    An empty list means the parameters passed validation.
    """

    errors: list[str] = []

    parameters = plan.parameters

    # -------------------------------------------------
    # BILL parameters
    # -------------------------------------------------

    if plan.action.value == "LOG_BILL":

        amount = parameters.get("amount")

        if amount is not None:
            amount_text = str(amount)

            if amount_text not in body:
                errors.append(
                    f"Bill amount '{amount}' was not found in email body."
                )

        due_date = parameters.get("due_date")

        if due_date is not None:
            if not _date_is_grounded(
                due_date=str(due_date),
                body=body,
            ):
                errors.append(
                    f"Due date '{due_date}' was not clearly found "
                    "in email body."
                )

        vendor = parameters.get("vendor")

        if vendor is not None:
            if str(vendor).lower() not in body.lower():
                errors.append(
                    f"Vendor '{vendor}' was not found in email body."
                )

    return errors


def _date_is_grounded(
    due_date: str,
    body: str,
) -> bool:
    """
    Check whether an ISO date appears in the email,
    either directly or in a readable date format.
    """

    if due_date in body:
        return True

    match = re.fullmatch(
        r"(\d{4})-(\d{2})-(\d{2})",
        due_date,
    )

    if not match:
        return False

    year, month, day = map(int, match.groups())

    try:
        parsed_date = date(year, month, day)
    except ValueError:
        return False

    month_name = parsed_date.strftime("%B")
    month_short = parsed_date.strftime("%b")

    readable_formats = [
        f"{month_name} {day}, {year}",
        f"{month_short} {day}, {year}",
        f"{day} {month_name} {year}",
        f"{day} {month_short} {year}",
    ]

    body_lower = body.lower()

    return any(
        readable_date.lower() in body_lower
        for readable_date in readable_formats
    )