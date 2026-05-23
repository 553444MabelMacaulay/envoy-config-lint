"""Type checking for environment variable values against expected types."""

from dataclasses import dataclass, field
from typing import List, Optional
import re

from envoy_config_lint.parser import EnvEntry


ENV_TYPE_PATTERNS = {
    "int": re.compile(r"^-?\d+$"),
    "float": re.compile(r"^-?\d+\.\d+$"),
    "bool": re.compile(r"^(true|false|1|0|yes|no)$", re.IGNORECASE),
    "url": re.compile(r"^https?://[^\s]+$"),
    "port": re.compile(r"^([1-9]\d{0,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$"),
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
}


@dataclass
class TypeIssue:
    key: str
    value: str
    expected_type: str
    line: int

    def __str__(self) -> str:
        return (
            f"Line {self.line}: '{self.key}' expected type '{self.expected_type}', "
            f"got value '{self.value}'"
        )


@dataclass
class TypeCheckResult:
    issues: List[TypeIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def issue_count(self) -> int:
        return len(self.issues)


def check_type(value: str, expected_type: str) -> bool:
    """Return True if value matches the expected type pattern."""
    pattern = ENV_TYPE_PATTERNS.get(expected_type)
    if pattern is None:
        return True  # unknown type — skip check
    return bool(pattern.fullmatch(value))


def typecheck_entries(
    entries: List[EnvEntry],
    schema: Optional[dict] = None,
) -> TypeCheckResult:
    """Check entries against a type schema dict mapping key -> expected_type.

    If schema is None or empty, no checks are performed.
    """
    result = TypeCheckResult()
    if not schema:
        return result

    for entry in entries:
        expected = schema.get(entry.key)
        if expected is None:
            continue
        if not check_type(entry.value, expected):
            result.issues.append(
                TypeIssue(
                    key=entry.key,
                    value=entry.value,
                    expected_type=expected,
                    line=entry.line,
                )
            )
    return result
