"""Encoder module: detect and report value encoding issues in env entries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import re

from envoy_config_lint.parser import EnvEntry


@dataclass
class EncodingIssue:
    key: str
    value: str
    message: str

    def __str__(self) -> str:
        return f"[encoding] {self.key}: {self.message}"


@dataclass
class EncodingResult:
    issues: List[EncodingIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def issue_count(self) -> int:
        return len(self.issues)


_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_NON_ASCII_RE = re.compile(r"[^\x00-\x7f]")
_ESCAPED_NEWLINE_RE = re.compile(r"\\n|\\r")


def _has_unescaped_newline(value: str) -> bool:
    """Return True if the raw value contains a literal newline character."""
    return "\n" in value or "\r" in value


def _has_control_characters(value: str) -> bool:
    return bool(_CONTROL_CHAR_RE.search(value))


def _has_non_ascii(value: str) -> bool:
    return bool(_NON_ASCII_RE.search(value))


def check_encoding(entries: List[EnvEntry]) -> EncodingResult:
    """Inspect each entry's value for encoding problems."""
    result = EncodingResult()
    for entry in entries:
        v = entry.value
        if _has_unescaped_newline(v):
            result.issues.append(
                EncodingIssue(entry.key, v, "contains a literal newline character")
            )
        if _has_control_characters(v):
            result.issues.append(
                EncodingIssue(entry.key, v, "contains non-printable control characters")
            )
        if _has_non_ascii(v):
            result.issues.append(
                EncodingIssue(entry.key, v, "contains non-ASCII characters; consider escaping or using ASCII")
            )
    return result
