"""Built-in lint rules for .env file validation."""

from dataclasses import dataclass
from typing import List

from envoy_config_lint.parser import EnvEntry, ParseResult


@dataclass
class LintIssue:
    """Represents a single lint finding."""

    line_number: int
    rule_id: str
    severity: str  # 'error' | 'warning' | 'info'
    message: str


def rule_duplicate_keys(entries: List[EnvEntry]) -> List[LintIssue]:
    """Detect duplicate key definitions."""
    issues = []
    seen = {}
    for entry in entries:
        if entry.key is None:
            continue
        if entry.key in seen:
            issues.append(LintIssue(
                line_number=entry.line_number,
                rule_id='E001',
                severity='error',
                message=f"Duplicate key '{entry.key}' (first defined on line {seen[entry.key]})",
            ))
        else:
            seen[entry.key] = entry.line_number
    return issues


def rule_empty_value(entries: List[EnvEntry]) -> List[LintIssue]:
    """Warn on keys with empty values."""
    issues = []
    for entry in entries:
        if entry.key and entry.value == '':
            issues.append(LintIssue(
                line_number=entry.line_number,
                rule_id='W001',
                severity='warning',
                message=f"Key '{entry.key}' has an empty value",
            ))
    return issues


def rule_uppercase_keys(entries: List[EnvEntry]) -> List[LintIssue]:
    """Warn on keys that are not fully uppercase."""
    issues = []
    for entry in entries:
        if entry.key and entry.key != entry.key.upper():
            issues.append(LintIssue(
                line_number=entry.line_number,
                rule_id='W002',
                severity='warning',
                message=f"Key '{entry.key}' should be uppercase (convention)",
            ))
    return issues


def rule_unquoted_spaces(entries: List[EnvEntry]) -> List[LintIssue]:
    """Detect values containing spaces that are not quoted."""
    issues = []
    for entry in entries:
        if entry.key and entry.value:
            val = entry.value
            if ' ' in val and not (val.startswith('"') or val.startswith("'")):
                issues.append(LintIssue(
                    line_number=entry.line_number,
                    rule_id='W003',
                    severity='warning',
                    message=f"Value for '{entry.key}' contains spaces but is not quoted",
                ))
    return issues


DEFAULT_RULES = [
    rule_duplicate_keys,
    rule_empty_value,
    rule_uppercase_keys,
    rule_unquoted_spaces,
]


def run_rules(parse_result: ParseResult) -> List[LintIssue]:
    """Run all default rules against a parse result."""
    issues = []
    for rule_fn in DEFAULT_RULES:
        issues.extend(rule_fn(parse_result.entries))
    issues.sort(key=lambda i: i.line_number)
    return issues
