"""High-level linter interface combining parsing and rule evaluation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envoy_config_lint.parser import ParseResult, parse_env_file
from envoy_config_lint.rules import LintIssue, run_rules


@dataclass
class LintReport:
    """Aggregated report for a single file."""

    file_path: str
    parse_result: ParseResult
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'error')

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'warning')

    @property
    def has_errors(self) -> bool:
        return self.error_count > 0

    def summary(self) -> str:
        """Return a human-readable one-line summary of the report."""
        return (
            f"{self.file_path}: "
            f"{self.error_count} error(s), {self.warning_count} warning(s)"
        )


def _extract_line_number(error_message: str) -> int:
    """Extract a line number from a parse error message, defaulting to 0."""
    try:
        return int(error_message.split('Line ')[1].split(':')[0])
    except (IndexError, ValueError):
        return 0


def lint_content(content: str, file_path: str = '<stdin>') -> LintReport:
    """Lint raw .env content and return a report."""
    parse_result = parse_env_file(content)
    issues = run_rules(parse_result)

    # Surface parse errors as lint issues
    for err in parse_result.errors:
        issues.append(LintIssue(
            line_number=_extract_line_number(err) if 'Line ' in err else 0,
            rule_id='E000',
            severity='error',
            message=err,
        ))

    issues.sort(key=lambda i: i.line_number)
    return LintReport(file_path=file_path, parse_result=parse_result, issues=issues)


def lint_file(path: Path) -> LintReport:
    """Read a file from disk and lint it."""
    try:
        content = path.read_text(encoding='utf-8')
    except OSError as exc:
        parse_result = parse_env_file('')
        report = LintReport(file_path=str(path), parse_result=parse_result)
        report.issues.append(LintIssue(
            line_number=0,
            rule_id='E999',
            severity='error',
            message=f"Could not read file: {exc}",
        ))
        return report
    return lint_content(content, file_path=str(path))
