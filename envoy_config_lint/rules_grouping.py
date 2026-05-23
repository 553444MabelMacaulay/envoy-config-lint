"""Lint rules that operate on prefix groups."""
from typing import List
from .parser import EnvEntry
from .rules import LintIssue
from .grouper import group_by_prefix


def rule_inconsistent_prefix_casing(entries: List[EnvEntry]) -> List[LintIssue]:
    """Warn when keys within the same prefix group mix upper and lower case."""
    issues: List[LintIssue] = []
    result = group_by_prefix(entries)
    for prefix, group in result.groups.items():
        has_upper = any(e.key == e.key.upper() for e in group)
        has_lower = any(e.key != e.key.upper() for e in group)
        if has_upper and has_lower:
            keys = ", ".join(e.key for e in group)
            issues.append(
                LintIssue(
                    severity="warning",
                    code="W006",
                    message=(
                        f"Prefix group '{prefix}' contains mixed-case keys: {keys}"
                    ),
                    line=group[0].line,
                )
            )
    return issues


def rule_singleton_prefix(entries: List[EnvEntry]) -> List[LintIssue]:
    """Info-level notice when a prefixed key has no siblings in its group."""
    issues: List[LintIssue] = []
    result = group_by_prefix(entries, min_group_size=2)
    # Entries in `ungrouped` that still have a separator are true singletons
    for entry in result.ungrouped:
        if "_" in entry.key:
            prefix = entry.key.split("_", 1)[0]
            issues.append(
                LintIssue(
                    severity="info",
                    code="I001",
                    message=(
                        f"Key '{entry.key}' uses prefix '{prefix}' "
                        "but no other keys share that prefix."
                    ),
                    line=entry.line,
                )
            )
    return issues
