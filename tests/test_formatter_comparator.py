"""Tests for envoy_config_lint.formatter_comparator."""
import json
import pytest
from envoy_config_lint.parser import ParseResult, EnvEntry
from envoy_config_lint.comparator import compare_env_files
from envoy_config_lint.formatter import OutputFormat
from envoy_config_lint.formatter_comparator import format_compare


def _make_result(*pairs) -> ParseResult:
    entries = [EnvEntry(key=k, value=v, line_number=i + 1, raw=f"{k}={v}") for i, (k, v) in enumerate(pairs)]
    return ParseResult(entries=entries, errors=[])


def test_text_no_diffs_message():
    a = _make_result(("X", "1"))
    b = _make_result(("X", "1"))
    out = format_compare(compare_env_files(a, b), OutputFormat.TEXT)
    assert "No value differences" in out


def test_text_shows_changed_key():
    a = _make_result(("FOO", "old"))
    b = _make_result(("FOO", "new"))
    out = format_compare(compare_env_files(a, b), OutputFormat.TEXT)
    assert "CHANGED" in out
    assert "FOO" in out


def test_text_shows_only_in_a():
    a = _make_result(("GONE", "1"))
    b = _make_result()
    out = format_compare(compare_env_files(a, b), OutputFormat.TEXT)
    assert "ONLY_IN_A" in out
    assert "GONE" in out


def test_text_shows_only_in_b():
    a = _make_result()
    b = _make_result(("NEW", "2"))
    out = format_compare(compare_env_files(a, b), OutputFormat.TEXT)
    assert "ONLY_IN_B" in out
    assert "NEW" in out


def test_text_summary_line():
    a = _make_result(("A", "1"), ("B", "x"))
    b = _make_result(("A", "2"), ("C", "y"))
    out = format_compare(compare_env_files(a, b), OutputFormat.TEXT)
    assert "Summary:" in out


def test_json_structure():
    a = _make_result(("K", "old"))
    b = _make_result(("K", "new"))
    out = format_compare(compare_env_files(a, b), OutputFormat.JSON)
    data = json.loads(out)
    assert "has_diffs" in data
    assert "diffs" in data
    assert data["changed"] == 1


def test_json_no_diffs():
    a = _make_result(("K", "v"))
    b = _make_result(("K", "v"))
    out = format_compare(compare_env_files(a, b), OutputFormat.JSON)
    data = json.loads(out)
    assert data["has_diffs"] is False
    assert data["diffs"] == []


def test_github_warning_for_changed():
    a = _make_result(("TOKEN", "a"))
    b = _make_result(("TOKEN", "b"))
    out = format_compare(compare_env_files(a, b), OutputFormat.GITHUB)
    assert "::warning" in out
    assert "TOKEN" in out


def test_github_notice_when_clean():
    a = _make_result(("K", "v"))
    b = _make_result(("K", "v"))
    out = format_compare(compare_env_files(a, b), OutputFormat.GITHUB)
    assert "::notice::" in out
