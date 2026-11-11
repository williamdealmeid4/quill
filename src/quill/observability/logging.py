"""Structured logging with redaction before the rotating handler writes."""

import json
import logging
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from quill.observability.redaction import JsonValue, redact


class RedactedJsonFormatter(logging.Formatter):
    """Never include raw traceback messages or arbitrary record extras."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, JsonValue] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "event": str(getattr(record, "event", record.name)),
            "task_id": str(getattr(record, "task_id", "")),
            "execution_id": str(getattr(record, "execution_id", "")),
            "code": str(getattr(record, "code", "")),
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            payload["exception_type"] = record.exc_info[0].__name__
        return json.dumps(redact(payload), ensure_ascii=False, allow_nan=False)


def setup_logging(log_dir: Path, *, max_bytes: int = 10 * 1024 * 1024) -> None:
    """Configure the Quill logger idempotently; leave other loggers untouched."""
    if max_bytes < 1:
        raise ValueError("max_bytes deve ser positivo")
    log_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    logger = logging.getLogger("quill")
    handler = RotatingFileHandler(
        log_dir / "quill.jsonl", maxBytes=max_bytes, backupCount=5, encoding="utf-8"
    )
    handler.setFormatter(RedactedJsonFormatter())
    for previous in logger.handlers[:]:
        logger.removeHandler(previous)
        previous.close()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
