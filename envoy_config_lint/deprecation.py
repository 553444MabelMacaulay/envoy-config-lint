"""Deprecation checker for environment variable keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envoy_config_lint.parser import EnvEntry


@dataclass
class DeprecationIssue:
    key: str
    message: str
    replacement: str | None = None

    def __str__(self) -> str:
        base = f"Key '{self.key}' is deprecated: {self.message}"
        if self.replacement:
            base += f" Use '{self.replacement}' instead."
        return base


@dataclass
class DeprecationResult:
    issues: List[DeprecationIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def issue_count(self) -> int:
        return len(self.issues)


# Maps deprecated key -> (message, optional replacement)
DeprecationRegistry = Dict[str, tuple[str, str | None]]


def check_deprecations(
    entries: List[EnvEntry],
    registry: DeprecationRegistry,
) -> DeprecationResult:
    """Check entries against a registry of deprecated keys.

    Args:
        entries: Parsed environment entries.
        registry: Mapping of deprecated key names to (reason, replacement).

    Returns:
        DeprecationResult containing any detected deprecation issues.
    """
    issues: List[DeprecationIssue] = []
    for entry in entries:
        if entry.key in registry:
            reason, replacement = registry[entry.key]
            issues.append(
                DeprecationIssue(
                    key=entry.key,
                    message=reason,
                    replacement=replacement,
                )
            )
    return DeprecationResult(issues=issues)


def build_registry(mapping: Dict[str, dict]) -> DeprecationRegistry:
    """Build a DeprecationRegistry from a plain dict configuration.

    Expected format::

        {
            "OLD_KEY": {"message": "reason", "replacement": "NEW_KEY"},
            "ANOTHER_OLD": {"message": "no longer used"},
        }
    """
    registry: DeprecationRegistry = {}
    for key, info in mapping.items():
        registry[key] = (info.get("message", "deprecated"), info.get("replacement"))
    return registry
