"""Formatter module for rendering lint reports in various output formats."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from envoy_config_lint.linter import LintReport


class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"
    GITHUB = "github"


def format_report(report: "LintReport", fmt: OutputFormat = OutputFormat.TEXT) -> str:
    """Render a LintReport as a string in the requested format."""
    if fmt == OutputFormat.JSON:
        return _format_json(report)
    if fmt == OutputFormat.GITHUB:
        return _format_github(report)
    return _format_text(report)


def _format_text(report: "LintReport") -> str:
    if not report.issues:
        return "No issues found."

    lines: list[str] = []
    for issue in report.issues:
        location = f"line {issue.line}" if issue.line is not None else "file"
        lines.append(
            f"[{issue.severity.upper()}] {location}: {issue.message}"
        )

    summary = (
        f"\n{len(report.issues)} issue(s) found "
        f"({report.error_count} error(s), {report.warning_count} warning(s))."
    )
    lines.append(summary)
    return "\n".join(lines)


def _format_json(report: "LintReport") -> str:
    import json

    payload = {
        "summary": {
            "total": len(report.issues),
            "errors": report.error_count,
            "warnings": report.warning_count,
        },
        "issues": [
            {
                "severity": issue.severity,
                "line": issue.line,
                "key": issue.key,
                "message": issue.message,
            }
            for issue in report.issues
        ],
    }
    return json.dumps(payload, indent=2)


def _format_github(report: "LintReport") -> str:
    """Emit GitHub Actions workflow command annotations."""
    if not report.issues:
        return ""

    lines: list[str] = []
    for issue in report.issues:
        level = "error" if issue.severity == "error" else "warning"
        line_part = f",line={issue.line}" if issue.line is not None else ""
        title = f"envoy-config-lint: {issue.key or 'unknown key'}"
        lines.append(
            f"::{level} title={title}{line_part}::{issue.message}"
        )
    return "\n".join(lines)
