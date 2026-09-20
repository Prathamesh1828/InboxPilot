import logging
import sys


def setup_logging() -> None:
    """
    Configure structured logging for InboxPilot.

    Call once at application startup.
    """

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )

    # Quiet noisy third-party libraries.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("googleapiclient").setLevel(logging.WARNING)
