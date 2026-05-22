"""Tests for the formatter module."""

from __future__ import annotations

import json

import pytest

from envoy_config_lint.formatter import OutputFormat, format_report
from envoy_config_lint.linter import LintReport
from envoy_config_lint.rules import LintIssue


def _make_report(*issues: LintIssue) -> LintReport:
    issues_list = list(issues)
    errors = sum(1 for i in issues_list if i.severity == "error")
    warnings = sum(1 for i in issues_list if i.severity == "warning")
    return LintReport(
        issues=issues_list,
        error_count=errors,
        warning_count=warnings,
        has_errors=errors > 0,
    )


_ERROR = LintIssue(severity="error", line=3, key="SECRET", message="Duplicate key")
_WARNING = LintIssue(severity="warning", line=7, key="EMPTY_VAR", message="Empty value")


class TestTextFormat:
    def test_no_issues(self):
        report = _make_report()
        assert format_report(report, OutputFormat.TEXT) == "No issues found."

    def test_single_error(self):
        report = _make_report(_ERROR)
        output = format_report(report, OutputFormat.TEXT)
        assert "[ERROR]" in output
        assert "line 3" in output
        assert "Duplicate key" in output

    def test_summary_line(self):
        report = _make_report(_ERROR, _WARNING)
        output = format_report(report, OutputFormat.TEXT)
        assert "2 issue(s)" in output
        assert "1 error(s)" in output
        assert "1 warning(s)" in output


class TestJsonFormat:
    def test_valid_json(self):
        report = _make_report(_ERROR, _WARNING)
        output = format_report(report, OutputFormat.JSON)
        data = json.loads(output)
        assert data["summary"]["total"] == 2
        assert data["summary"]["errors"] == 1
        assert data["summary"]["warnings"] == 1
        assert len(data["issues"]) == 2

    def test_empty_report(self):
        report = _make_report()
        data = json.loads(format_report(report, OutputFormat.JSON))
        assert data["issues"] == []


class TestGithubFormat:
    def test_error_annotation(self):
        report = _make_report(_ERROR)
        output = format_report(report, OutputFormat.GITHUB)
        assert "::error " in output
        assert "line=3" in output
        assert "Duplicate key" in output

    def test_warning_annotation(self):
        report = _make_report(_WARNING)
        output = format_report(report, OutputFormat.GITHUB)
        assert "::warning " in output

    def test_no_issues_empty_string(self):
        report = _make_report()
        assert format_report(report, OutputFormat.GITHUB) == ""
