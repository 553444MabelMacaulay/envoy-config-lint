"""Lint rule adapter that surfaces deprecation issues as LintIssues."""
from __future__ import annotations

from typing import Dict, List

from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.rules import LintIssue
from envoy_config_lint.deprecation import DeprecationRegistry, check_deprecations


def rule_deprecated_keys(
    entries: List[EnvEntry],
    registry: DeprecationRegistry | None = None,
) -> List[LintIssue]:
    """Emit a warning for every entry whose key appears in the deprecation registry.

    Args:
        entries: Parsed environment entries to inspect.
        registry: Optional deprecation registry.  When *None* or empty the rule
                  is effectively a no-op, so callers can safely omit it.

    Returns:
        A list of :class:`~envoy_config_lint.rules.LintIssue` warnings.
    """
    if not registry:
        return []

    result = check_deprecations(entries, registry)
    issues: List[LintIssue] = []
    for dep in result.issues:
        detail = f"Key '{dep.key}' is deprecated: {dep.message}"
        if dep.replacement:
            detail += f" Consider using '{dep.replacement}'."
        issues.append(
            LintIssue(
                key=dep.key,
                severity="warning",
                message=detail,
            )
        )
    return issues
