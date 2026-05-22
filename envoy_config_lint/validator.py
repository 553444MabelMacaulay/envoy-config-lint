"""Validator module for checking .env files against a reference schema.

Allows users to define required and optional keys, and validates that
a given .env file satisfies the schema constraints.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set

from envoy_config_lint.parser import ParseResult
from envoy_config_lint.rules import LintIssue


@dataclass
class EnvSchema:
    """Defines expected keys for an environment configuration."""

    required_keys: Set[str] = field(default_factory=set)
    optional_keys: Set[str] = field(default_factory=set)

    def all_known_keys(self) -> Set[str]:
        return self.required_keys | self.optional_keys


@dataclass
class ValidationResult:
    """Result of validating a ParseResult against an EnvSchema."""

    issues: List[LintIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return all(issue.severity != "error" for issue in self.issues)


def validate_against_schema(
    parse_result: ParseResult,
    schema: EnvSchema,
    source: Optional[str] = None,
) -> ValidationResult:
    """Validate parsed env entries against the provided schema.

    Emits errors for missing required keys and warnings for unknown keys
    that are present in the file but not declared in the schema.

    Args:
        parse_result: The parsed environment file entries.
        schema: The schema defining required and optional keys.
        source: Optional filename used in issue messages.

    Returns:
        A ValidationResult containing any detected issues.
    """
    issues: List[LintIssue] = []
    file_label = source or "<input>"

    present_keys: Set[str] = {entry.key for entry in parse_result.entries}

    for key in sorted(schema.required_keys):
        if key not in present_keys:
            issues.append(
                LintIssue(
                    severity="error",
                    rule="missing_required_key",
                    message=f"Required key '{key}' is missing from {file_label}.",
                    line=None,
                )
            )

    if schema.all_known_keys():
        for key in sorted(present_keys - schema.all_known_keys()):
            matching_line = next(
                (e.line for e in parse_result.entries if e.key == key), None
            )
            issues.append(
                LintIssue(
                    severity="warning",
                    rule="unknown_key",
                    message=f"Key '{key}' is not declared in the schema.",
                    line=matching_line,
                )
            )

    return ValidationResult(issues=issues)
