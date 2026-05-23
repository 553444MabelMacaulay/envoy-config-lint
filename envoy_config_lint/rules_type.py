"""Lint rule that wraps type-checking as a standard LintIssue list."""

from typing import Dict, List

from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.rules import LintIssue
from envoy_config_lint.type_checker import typecheck_entries


def rule_type_mismatch(
    entries: List[EnvEntry],
    type_schema: Dict[str, str],
) -> List[LintIssue]:
    """Return LintIssues for entries whose values do not match their declared type.

    Args:
        entries:     Parsed env entries to validate.
        type_schema: Mapping of key name -> expected type string
                     (e.g. {"PORT": "port", "DEBUG": "bool"}).

    Returns:
        A list of LintIssue with severity 'error' for each mismatch.
    """
    issues: List[LintIssue] = []

    if not type_schema:
        return issues

    result = typecheck_entries(entries, schema=type_schema)
    for type_issue in result.issues:
        issues.append(
            LintIssue(
                key=type_issue.key,
                line=type_issue.line,
                message=(
                    f"Value '{type_issue.value}' does not match "
                    f"expected type '{type_issue.expected_type}'."
                ),
                severity="error",
            )
        )
    return issues
