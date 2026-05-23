"""Lint rule that surfaces interpolation issues as LintIssues.

Bridges the interpolator module with the standard LintIssue type used
throughout the linter pipeline.
"""

from __future__ import annotations

from typing import List

from .interpolator import check_interpolation
from .parser import EnvEntry
from .rules import LintIssue


def rule_unresolved_interpolation(entries: List[EnvEntry]) -> List[LintIssue]:
    """Emit an error for every value that references an undefined variable.

    Example triggering case::

        URL=${BASE_URL}/api   # BASE_URL never defined → error

    Returns a list of :class:`~envoy_config_lint.rules.LintIssue` objects,
    one per unresolved reference.
    """
    result = check_interpolation(entries)
    issues: List[LintIssue] = []

    for interp_issue in result.issues:
        issues.append(
            LintIssue(
                severity="error",
                rule="unresolved-interpolation",
                key=interp_issue.key,
                line=interp_issue.line,
                message=(
                    f"Value references undefined variable '${interp_issue.ref}'. "
                    "Ensure the variable is declared before use."
                ),
            )
        )

    return issues
