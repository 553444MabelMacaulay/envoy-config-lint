"""Tests for the diff formatter."""
import json
import pytest

from envoy_config_lint.differ import DiffResult
from envoy_config_lint.formatter import OutputFormat
from envoy_config_lint.formatter_diff import format_diff


def _make_diff(missing=None, extra=None, common=None) -> DiffResult:
    return DiffResult(
        base_file=".env.example",
        compare_file=".env",
        missing_in_compare=missing or [],
        extra_in_compare=extra or [],
        common_keys=common or [],
    )


def test_text_no_differences():
    result = _make_diff(common=["FOO"])
    output = format_diff(result, OutputFormat.TEXT)
    assert "No differences found" in output
    assert ".env.example" in output


def test_text_shows_missing_keys():
    result = _make_diff(missing=["SECRET", "TOKEN"])
    output = format_diff(result, OutputFormat.TEXT)
    assert "- SECRET" in output
    assert "- TOKEN" in output


def test_text_shows_extra_keys():
    result = _make_diff(extra=["DEBUG"])
    output = format_diff(result, OutputFormat.TEXT)
    assert "+ DEBUG" in output


def test_text_summary_line():
    result = _make_diff(missing=["A"], extra=["B", "C"], common=["D"])
    output = format_diff(result, OutputFormat.TEXT)
    assert "1 missing" in output
    assert "2 extra" in output
    assert "1 common" in output


def test_json_format_structure():
    result = _make_diff(missing=["FOO"], extra=["BAR"])
    output = format_diff(result, OutputFormat.JSON)
    data = json.loads(output)
    assert data["base_file"] == ".env.example"
    assert "FOO" in data["missing_in_compare"]
    assert "BAR" in data["extra_in_compare"]
    assert data["has_differences"] is True


def test_json_no_differences():
    result = _make_diff(common=["X"])
    output = format_diff(result, OutputFormat.JSON)
    data = json.loads(output)
    assert data["has_differences"] is False


def test_github_format_missing_warning():
    result = _make_diff(missing=["SECRET"])
    output = format_diff(result, OutputFormat.GITHUB)
    assert "::warning" in output
    assert "SECRET" in output


def test_github_format_extra_notice():
    result = _make_diff(extra=["EXTRA"])
    output = format_diff(result, OutputFormat.GITHUB)
    assert "::notice" in output
    assert "EXTRA" in output


def test_github_format_no_differences():
    result = _make_diff(common=["FOO"])
    output = format_diff(result, OutputFormat.GITHUB)
    assert "::notice" in output
    assert "No differences" in output
