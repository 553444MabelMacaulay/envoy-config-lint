"""Lint rules that wrap dependency analysis."""
from __future__ import annotations

from typing import List

from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.rules import LintIssue
from envoy_config_lint.dependency import check_dependencies


def rule_missing_dependencies(entries: List[EnvEntry]) -> List[LintIssue]:
    """Error when a value references a key that is not defined in the same file."""
    result = check_dependencies(entries, report_unused=False)
    issues: List[LintIssue] = []
    for dep_issue in result.issues:
        if dep_issue.kind == "missing_dependency":
            issues.append(
                LintIssue(
                    key=dep_issue.key,
                    message=(
                        f"references '${dep_issue.referenced_key}' "
                        f"which is not defined in this file"
                    ),
                    severity="error",
                )
            )
    return issues


def rule_unused_variables(entries: List[EnvEntry]) -> List[LintIssue]:
    """Warn when a key is never referenced by any other variable in the file."""
    result = check_dependencies(entries, report_unused=True)
    issues: List[LintIssue] = []
    for dep_issue in result.issues:
        if dep_issue.kind == "unused_key":
            issues.append(
                LintIssue(
                    key=dep_issue.key,
                    message="is defined but never referenced by another variable",
                    severity="warning",
                )
            )
    return issues
