"""Redaction utilities for masking sensitive values in env files."""

from dataclasses import dataclass, field
from typing import List, Set

from envoy_config_lint.parser import EnvEntry, ParseResult

# Common patterns that indicate a value should be treated as sensitive
DEFAULT_SENSITIVE_PATTERNS: Set[str] = {
    "SECRET",
    "PASSWORD",
    "PASSWD",
    "TOKEN",
    "API_KEY",
    "APIKEY",
    "PRIVATE_KEY",
    "PRIVATE",
    "CREDENTIAL",
    "AUTH",
    "ACCESS_KEY",
    "SIGNING_KEY",
}

REDACTED_PLACEHOLDER = "***REDACTED***"


@dataclass
class RedactedEntry:
    key: str
    value: str
    redacted: bool
    line_number: int


@dataclass
class RedactResult:
    entries: List[RedactedEntry] = field(default_factory=list)

    @property
    def redacted_count(self) -> int:
        return sum(1 for e in self.entries if e.redacted)

    @property
    def total_count(self) -> int:
        return len(self.entries)


def _is_sensitive(key: str, patterns: Set[str]) -> bool:
    """Return True if the key contains any of the known sensitive patterns."""
    upper_key = key.upper()
    return any(pattern in upper_key for pattern in patterns)


def redact_parse_result(
    result: ParseResult,
    extra_patterns: Set[str] | None = None,
) -> RedactResult:
    """Produce a RedactResult from a ParseResult, masking sensitive values."""
    patterns = DEFAULT_SENSITIVE_PATTERNS.copy()
    if extra_patterns:
        patterns.update(p.upper() for p in extra_patterns)

    redacted_entries: List[RedactedEntry] = []
    for entry in result.entries:
        sensitive = _is_sensitive(entry.key, patterns)
        redacted_entries.append(
            RedactedEntry(
                key=entry.key,
                value=REDACTED_PLACEHOLDER if sensitive else entry.value,
                redacted=sensitive,
                line_number=entry.line_number,
            )
        )
    return RedactResult(entries=redacted_entries)


def render_redacted(result: RedactResult) -> str:
    """Render a redacted env file as a string suitable for safe display."""
    lines = []
    for entry in result.entries:
        lines.append(f"{entry.key}={entry.value}")
    return "\n".join(lines)
