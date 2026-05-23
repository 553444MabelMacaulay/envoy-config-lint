"""Lint rule that surfaces encoding issues as LintIssues."""
from __future__ import annotations

from typing import List

from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.rules import LintIssue
from envoy_config_lint.encoder import check_encoding


def rule_encoding_issues(entries: List[EnvEntry]) -> List[LintIssue]:
    """Return a LintIssue for every detected encoding problem.

    Unescaped newlines and control characters are reported as errors;
    non-ASCII characters are reported as warnings.
    """
    result = check_encoding(entries)
    issues: List[LintIssue] = []
    for enc_issue in result.issues:
        is_error = (
            "newline" in enc_issue.message
            or "control" in enc_issue.message
        )
        issues.append(
            LintIssue(
                key=enc_issue.key,
                message=enc_issue.message,
                severity="error" if is_error else "warning",
            )
        )
    return issues
