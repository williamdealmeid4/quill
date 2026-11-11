"""Sensitive data must be removed before reaching a logging handler."""

import json
import logging
from pathlib import Path

import pytest

from quill.observability.logging import setup_logging
from quill.observability.redaction import redact

pytestmark = pytest.mark.security


def test_authorization_token_redacted() -> None:
    assert "fixture-secret" not in str(redact("Authorization: Bearer fixture-secret"))
    assert "fixture-cookie" not in str(redact("Cookie: session=fixture-cookie"))


def test_nested_cookie_and_url_secret() -> None:
    result = redact(
        {
            "nested": [{"api_key": "fixture-secret"}],
            "url": "https://example.test/?token=fixture-token&visible=yes",
        }
    )
    assert "fixture-secret" not in str(result)
    assert "fixture-token" not in str(result)
    assert "visible=yes" in str(result)


def test_no_raw_secret_in_file(tmp_path: Path) -> None:
    setup_logging(tmp_path)
    logger = logging.getLogger("quill.test")
    try:
        raise ValueError("Authorization: Bearer fixture-exception-secret")
    except ValueError:
        logger.exception("Authorization: Bearer fixture-message-secret")
    content = (tmp_path / "quill.jsonl").read_text()
    assert "fixture-message-secret" not in content
    assert "fixture-exception-secret" not in content
    assert json.loads(content)["level"] == "ERROR"


def test_handler_not_duplicated(tmp_path: Path) -> None:
    setup_logging(tmp_path)
    setup_logging(tmp_path)
    logging.getLogger("quill").warning("one event")
    assert len((tmp_path / "quill.jsonl").read_text().splitlines()) == 1


def test_rotation_retains_five_backups(tmp_path: Path) -> None:
    setup_logging(tmp_path, max_bytes=200)
    for index in range(30):
        logging.getLogger("quill").warning("event %s", index)
    files = list(tmp_path.glob("quill.jsonl*"))
    assert len(files) == 6
    for path in files:
        for line in path.read_text().splitlines():
            assert isinstance(json.loads(line), dict)
