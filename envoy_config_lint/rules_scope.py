"""Lint rule wrapping scope analysis for use in the main linting pipeline."""

from __future__ import annotations

from typing import List

from envoy_config_lint.linter import LintIssue
from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.scoper import scope_entries


def rule_mixed_env_scopes(entries: List[EnvEntry]) -> List[LintIssue]:
    """Warn when keys from multiple environment scopes are mixed in one file.

    For example, having both DEV_HOST and PROD_HOST in the same .env file is
    usually a mistake — each environment should have its own file.
    """
    result = scope_entries(entries)
    if not result.has_issues:
        return []

    lint_issues: List[LintIssue] = []
    for issue in result.issues:
        lint_issues.append(
            LintIssue(
                key=issue.key,
                message=issue.message,
                severity="warning",
                rule="mixed-env-scopes",
            )
        )
    return lint_issues
