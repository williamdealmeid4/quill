"""Best-effort redaction complements collecting the minimum necessary data."""

import re

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]

_SENSITIVE_KEY = re.compile(
    r"authorization|cookie|password|passwd|secret|token|api[_-]?key", re.IGNORECASE
)
_HEADERS = re.compile(r"\b(?:authorization|cookie|set-cookie)\s*:\s*[^\r\n]+", re.IGNORECASE)
_ASSIGNMENTS = re.compile(
    r"\b(?:password|passwd|secret|token|api[_-]?key|access_token|refresh_token)"
    r"\s*[=:]\s*[^\s&;]+",
    re.IGNORECASE,
)
_TOKENS = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b")
_BEARER = re.compile(r"\bBearer\s+[^\s,;]+", re.IGNORECASE)


def redact(value: JsonValue) -> JsonValue:
    """Return a redacted copy without mutating the caller's payload."""
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if _SENSITIVE_KEY.search(key) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        text = _HEADERS.sub("[REDACTED HEADER]", value)
        text = _ASSIGNMENTS.sub("[REDACTED]", text)
        text = _TOKENS.sub("[REDACTED]", text)
        return _BEARER.sub("Bearer [REDACTED]", text)
    return value
