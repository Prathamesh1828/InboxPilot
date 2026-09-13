from app.schemas.action_plan import ActionPlan, ActionType


class ActionExecutor:
    """
    Executes InboxPilot actions.

    Currently operates in dry-run mode.
    No external systems are modified.
    """

    def execute(
        self,
        plan: ActionPlan,
    ) -> str:

        if plan.action == ActionType.LOG_BILL:
            return self._log_bill(plan)

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
    ) -> str:

        amount = plan.parameters.get("amount")
        currency = plan.parameters.get("currency")
        due_date = plan.parameters.get("due_date")

        return (
            f"DRY RUN: Would log bill of "
            f"{currency} {amount} "
            f"due on {due_date}."
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

