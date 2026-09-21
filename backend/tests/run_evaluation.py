"""
InboxPilot Batch Evaluation Runner

Runs all evaluation cases in batches with configurable delays and
exponential-backoff retry for API rate-limit (429) errors.

Environment variables:
    EVAL_BATCH_SIZE   – cases per batch  (default 10)
    EVAL_BATCH_DELAY  – seconds between batches  (default 30)
    EVAL_MAX_RETRIES  – max retries per case on API errors  (default 3)

Usage:
    python tests/run_evaluation.py
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Ensure the backend package is importable
# ---------------------------------------------------------------------------
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.google_account import GoogleAccount
from app.repositories.email_repository import create_email_if_not_exists
from app.services.email_pipeline import EmailPipeline

# ---------------------------------------------------------------------------
# Configuration (from env or defaults)
# ---------------------------------------------------------------------------
BATCH_SIZE: int = int(os.environ.get("EVAL_BATCH_SIZE", "5"))
BATCH_DELAY: int = int(os.environ.get("EVAL_BATCH_DELAY", "60"))
MAX_RETRIES: int = int(os.environ.get("EVAL_MAX_RETRIES", "5"))

DATASET_PATH = Path(__file__).parent / "eval_dataset.json"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("eval_runner")

# Silence noisy HTTP loggers during evaluation
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("groq").setLevel(logging.WARNING)
logging.getLogger("app.services.email_pipeline").setLevel(logging.WARNING)
logging.getLogger("app.services.classification_service").setLevel(logging.WARNING)
logging.getLogger("app.services.workflow_service").setLevel(logging.WARNING)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------
@dataclass
class CaseResult:
    case_id: str
    passed: bool
    api_error: bool = False
    failure_reason: str = ""
    expected_category: str = ""
    actual_category: str = ""
    expected_action: str = ""
    actual_action: str = ""
    expected_approval: bool = False
    actual_approval: bool = False
    expected_workflow: str = ""
    actual_workflow: str = ""
    classification_ok: bool = False
    action_ok: bool = False
    grounding_ok: bool = False
    safety_ok: bool = False


@dataclass
class EvalReport:
    total: int = 0
    passed: int = 0
    failed: int = 0
    api_errors: int = 0
    classification_correct: int = 0
    action_correct: int = 0
    grounding_correct: int = 0
    safety_correct: int = 0
    results: list[CaseResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Database helpers (isolated in-memory DB)
# ---------------------------------------------------------------------------
def create_test_session():
    """Create an isolated SQLite in-memory database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed a mock GoogleAccount
    account = GoogleAccount(
        email="test@inboxpilot.com",
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
    )
    session.add(account)
    session.commit()
    return session, engine


# ---------------------------------------------------------------------------
# Rate-limit detection
# ---------------------------------------------------------------------------
_RATE_LIMIT_MARKERS = [
    "429",
    "rate_limit",
    "rate limit",
    "too many requests",
    "resource_exhausted",
    "quota",
]


def _is_rate_limit_error(exc: BaseException | None) -> bool:
    """Return True if the exception looks like an API rate-limit error."""
    while exc is not None:
        msg = str(exc).lower()
        if any(marker in msg for marker in _RATE_LIMIT_MARKERS):
            return True
        exc = exc.__cause__ or exc.__context__
    return False


# ---------------------------------------------------------------------------
# Single-case evaluation with retry
# ---------------------------------------------------------------------------
def evaluate_case(case: dict) -> CaseResult:
    """
    Run a single evaluation case.

    If it hits a rate-limit error, retry with exponential backoff
    up to MAX_RETRIES times.  Ordinary assertion/logic failures are
    NOT retried.
    """
    case_id = case["id"]

    for attempt in range(1, MAX_RETRIES + 1):
        # Fresh DB per attempt so state is clean
        db, engine = create_test_session()

        try:
            email, _ = create_email_if_not_exists(
                db=db,
                provider_message_id=f"msg_{case_id}_attempt{attempt}",
                thread_id=f"thread_{case_id}_attempt{attempt}",
                sender="sender@example.com",
                recipients=["test@inboxpilot.com"],
                subject=case["subject"],
                body=case["body"],
                received_at=datetime.now(timezone.utc),
            )

            pipeline = EmailPipeline()

            with (
                patch("app.integrations.telegram.bot.send_approval_notification"),
                patch("app.services.executor.archive_email", return_value="mock_archive_id"),
                patch("app.services.executor.create_calendar_event", return_value="mock_event_id"),
                patch("app.services.executor.create_gmail_draft", return_value="mock_draft_id"),
            ):
                result = pipeline.process_email(db=db, email_id=email.id)

            # ---------- assertions ----------
            res = CaseResult(
                case_id=case_id,
                passed=True,
                expected_category=case["expected_category"],
                expected_action=case["expected_action"],
                expected_approval=case["expected_approval_requirement"],
                expected_workflow=case["expected_workflow_status"],
            )

            # Classification
            if result.classification is None:
                res.passed = False
                res.failure_reason = "Classification returned None"
                return res

            res.actual_category = result.classification.category.value
            res.classification_ok = (res.actual_category == res.expected_category)
            if not res.classification_ok:
                res.passed = False
                res.failure_reason = (
                    f"Classification: expected {res.expected_category}, "
                    f"got {res.actual_category}. "
                    f"Reasoning: {result.classification.reasoning}"
                )
                return res

            # REVIEW short-circuit
            if result.workflow_status == "REVIEW":
                if case["expected_workflow_status"] == "REVIEW":
                    res.action_ok = True
                    res.grounding_ok = True
                    res.safety_ok = True
                    return res
                else:
                    res.passed = False
                    res.failure_reason = "Got REVIEW status unexpectedly"
                    return res

            # Action plan
            if result.action_plan is None:
                res.passed = False
                res.failure_reason = f"Action plan is missing. Error: {result.error}"
                return res

            res.actual_action = result.action_plan.action.value
            res.action_ok = (res.actual_action == res.expected_action)
            if not res.action_ok:
                res.passed = False
                res.failure_reason = (
                    f"Action: expected {res.expected_action}, "
                    f"got {res.actual_action}. "
                    f"Reasoning: {result.action_plan.reasoning}"
                )
                return res

            # Safety / approval routing
            res.actual_approval = result.action_plan.requires_approval
            res.safety_ok = (res.actual_approval == res.expected_approval)
            if not res.safety_ok:
                res.passed = False
                res.failure_reason = (
                    f"Safety: expected requires_approval={res.expected_approval}, "
                    f"got {res.actual_approval}"
                )
                return res

            # Workflow status (grounding)
            res.actual_workflow = result.workflow_status
            res.grounding_ok = (res.actual_workflow == res.expected_workflow)
            if not res.grounding_ok:
                res.passed = False
                res.failure_reason = (
                    f"Workflow: expected {res.expected_workflow}, "
                    f"got {res.actual_workflow}. Error: {result.error}"
                )
                return res

            # All passed
            res.grounding_ok = True
            return res

        except Exception as exc:
            if _is_rate_limit_error(exc) and attempt < MAX_RETRIES:
                wait = 2 ** attempt * 10  # 20s, 40s, 80s
                logger.warning(
                    "  [%s] API rate-limit on attempt %d/%d - waiting %ds",
                    case_id, attempt, MAX_RETRIES, wait,
                )
                time.sleep(wait)
                continue
            elif _is_rate_limit_error(exc):
                logger.error(
                    "  [%s] API rate-limit - all %d retries exhausted",
                    case_id, MAX_RETRIES,
                )
                return CaseResult(
                    case_id=case_id,
                    passed=False,
                    api_error=True,
                    failure_reason=f"API rate-limit after {MAX_RETRIES} retries: {exc}",
                    expected_category=case["expected_category"],
                    expected_action=case["expected_action"],
                )
            else:
                # Non-rate-limit runtime error - do NOT retry
                return CaseResult(
                    case_id=case_id,
                    passed=False,
                    api_error=True,
                    failure_reason=f"Runtime error: {exc}",
                    expected_category=case["expected_category"],
                    expected_action=case["expected_action"],
                )
        finally:
            db.close()
            Base.metadata.drop_all(bind=engine)

    # Should not reach here, but safety net
    return CaseResult(
        case_id=case_id,
        passed=False,
        api_error=True,
        failure_reason="Exhausted all retries",
        expected_category=case["expected_category"],
        expected_action=case["expected_action"],
    )


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------
def run_evaluation(cases: list[dict] | None = None) -> EvalReport:
    """Run the full evaluation in batches."""

    if cases is None:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            cases = json.load(f)

    total = len(cases)
    report = EvalReport(total=total)

    # Split into batches
    batches = [cases[i : i + BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]
    num_batches = len(batches)

    logger.info("=" * 60)
    logger.info("InboxPilot Evaluation Runner")
    logger.info("  Total cases  : %d", total)
    logger.info("  Batch size   : %d", BATCH_SIZE)
    logger.info("  Batches      : %d", num_batches)
    logger.info("  Batch delay  : %ds", BATCH_DELAY)
    logger.info("  Max retries  : %d (per case, rate-limit only)", MAX_RETRIES)
    logger.info("=" * 60)

    for batch_idx, batch in enumerate(batches, 1):
        batch_passed = 0
        batch_total = len(batch)

        logger.info("")
        logger.info("--- Batch %d/%d (%d cases) ---", batch_idx, num_batches, batch_total)

        for i, case in enumerate(batch, 1):
            logger.info("  [%d/%d] Running %s ...", i, batch_total, case["id"])
            result = evaluate_case(case)
            report.results.append(result)

            if result.passed:
                batch_passed += 1
                report.passed += 1
                logger.info("    -> PASSED")
            elif result.api_error:
                report.api_errors += 1
                report.failed += 1
                logger.error("    -> API_ERROR: %s", result.failure_reason[:120])
            else:
                report.failed += 1
                logger.warning("    -> FAILED: %s", result.failure_reason[:120])

            # Track component accuracy
            if result.classification_ok:
                report.classification_correct += 1
            if result.action_ok:
                report.action_correct += 1
            if result.grounding_ok:
                report.grounding_correct += 1
            if result.safety_ok:
                report.safety_correct += 1

        logger.info("  Batch %d result: %d/%d passed", batch_idx, batch_passed, batch_total)

        # Delay between batches (but not after the last one)
        if batch_idx < num_batches:
            logger.info("  Waiting %ds before next batch...", BATCH_DELAY)
            time.sleep(BATCH_DELAY)

    # Final report
    _print_report(report)
    return report


# ---------------------------------------------------------------------------
# Report printer
# ---------------------------------------------------------------------------
def _print_report(report: EvalReport) -> None:
    t = report.total
    logger.info("")
    logger.info("=" * 60)
    logger.info("EVALUATION REPORT")
    logger.info("=" * 60)
    logger.info("  Total cases            : %d", t)
    logger.info("  Passed                 : %d", report.passed)
    logger.info("  Failed                 : %d", report.failed)
    logger.info("  API/rate-limit errors  : %d", report.api_errors)
    logger.info("")

    evaluated = t - report.api_errors
    if evaluated > 0:
        logger.info("  Classification accuracy : %d/%d (%.1f%%)",
                     report.classification_correct, evaluated,
                     report.classification_correct / evaluated * 100)
        logger.info("  Action-plan accuracy    : %d/%d (%.1f%%)",
                     report.action_correct, evaluated,
                     report.action_correct / evaluated * 100)
        logger.info("  Grounding accuracy      : %d/%d (%.1f%%)",
                     report.grounding_correct, evaluated,
                     report.grounding_correct / evaluated * 100)
        logger.info("  Safety/approval accuracy: %d/%d (%.1f%%)",
                     report.safety_correct, evaluated,
                     report.safety_correct / evaluated * 100)
        logger.info("  Overall strict match    : %d/%d (%.1f%%)",
                     report.passed, evaluated,
                     report.passed / evaluated * 100)

    # Failed cases detail
    failures = [r for r in report.results if not r.passed]
    if failures:
        logger.info("")
        logger.info("-" * 60)
        logger.info("FAILED CASES")
        logger.info("-" * 60)
        for r in failures:
            tag = "API_ERROR" if r.api_error else "FAILED"
            logger.info("")
            logger.info("  %s  [%s]", r.case_id, tag)
            logger.info("    Expected category : %s", r.expected_category)
            logger.info("    Actual category   : %s", r.actual_category or "N/A")
            logger.info("    Expected action   : %s", r.expected_action)
            logger.info("    Actual action     : %s", r.actual_action or "N/A")
            logger.info("    Reason            : %s", r.failure_reason)

    logger.info("")
    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    run_evaluation()
