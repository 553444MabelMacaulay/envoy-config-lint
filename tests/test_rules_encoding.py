"""Tests for envoy_config_lint.rules_encoding."""
from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.rules_encoding import rule_encoding_issues


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, line_number=1, raw="")


def test_no_issues_for_clean_entries():
    entries = [_entry("DB_HOST", "localhost"), _entry("PORT", "5432")]
    issues = rule_encoding_issues(entries)
    assert issues == []


def test_literal_newline_is_error():
    entries = [_entry("MSG", "line1\nline2")]
    issues = rule_encoding_issues(entries)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert issues[0].key == "MSG"


def test_control_character_is_error():
    entries = [_entry("CTRL", "val\x01ue")]
    issues = rule_encoding_issues(entries)
    error_issues = [i for i in issues if i.severity == "error"]
    assert len(error_issues) >= 1


def test_non_ascii_is_warning():
    entries = [_entry("LABEL", "caf\xe9")]
    issues = rule_encoding_issues(entries)
    warning_issues = [i for i in issues if i.severity == "warning"]
    assert len(warning_issues) >= 1


def test_multiple_entries_each_checked():
    entries = [
        _entry("A", "ok"),
        _entry("B", "bad\nvalue"),
        _entry("C", "also\x00bad"),
    ]
    issues = rule_encoding_issues(entries)
    keys_with_issues = {i.key for i in issues}
    assert "B" in keys_with_issues
    assert "C" in keys_with_issues
    assert "A" not in keys_with_issues


def test_returns_lint_issue_objects():
    from envoy_config_lint.rules import LintIssue
    entries = [_entry("X", "\x0b")]
    issues = rule_encoding_issues(entries)
    assert all(isinstance(i, LintIssue) for i in issues)
