"""Detect declared-but-unused and used-but-undeclared variable dependencies."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set

from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.interpolator import _extract_refs  # reuse ref extraction


@dataclass
class DependencyIssue:
    key: str
    referenced_key: str
    kind: str  # "missing_dependency" | "unused_key"
    severity: str = "warning"

    def __str__(self) -> str:
        if self.kind == "missing_dependency":
            return (
                f"{self.severity.upper()}: '{self.key}' references "
                f"'${self.referenced_key}' which is not defined"
            )
        return (
            f"{self.severity.upper()}: '{self.key}' is defined but never "
            f"referenced by any other variable"
        )


@dataclass
class DependencyResult:
    issues: List[DependencyIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def issue_count(self) -> int:
        return len(self.issues)


def _all_defined_keys(entries: List[EnvEntry]) -> Set[str]:
    return {e.key for e in entries}


def _all_referenced_keys(entries: List[EnvEntry]) -> Set[str]:
    """Collect every key that is referenced via interpolation in any value."""
    refs: Set[str] = set()
    for entry in entries:
        refs.update(_extract_refs(entry.value))
    return refs


def check_dependencies(
    entries: List[EnvEntry],
    report_unused: bool = False,
) -> DependencyResult:
    """Return a DependencyResult describing missing and (optionally) unused keys."""
    result = DependencyResult()
    defined = _all_defined_keys(entries)
    referenced_globally = _all_referenced_keys(entries)

    for entry in entries:
        for ref in _extract_refs(entry.value):
            if ref not in defined:
                result.issues.append(
                    DependencyIssue(
                        key=entry.key,
                        referenced_key=ref,
                        kind="missing_dependency",
                        severity="error",
                    )
                )

    if report_unused:
        for entry in entries:
            if entry.key not in referenced_globally:
                result.issues.append(
                    DependencyIssue(
                        key=entry.key,
                        referenced_key=entry.key,
                        kind="unused_key",
                        severity="warning",
                    )
                )

    return result
