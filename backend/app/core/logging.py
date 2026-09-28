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

    # Redact sensitive tokens from uvicorn access logs
    class SensitiveQueryFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if isinstance(record.args, tuple) and len(record.args) > 2:
                path_query = record.args[2]
                if isinstance(path_query, str) and "token=" in path_query:
                    import re
                    # Replace token value with ***
                    redacted = re.sub(r'token=[^&]+', 'token=***', path_query)
                    args_list = list(record.args)
                    args_list[2] = redacted
                    record.args = tuple(args_list)
            return True

    logging.getLogger("uvicorn.access").addFilter(SensitiveQueryFilter())
