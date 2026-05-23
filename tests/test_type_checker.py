"""Tests for envoy_config_lint.type_checker."""

import pytest
from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.type_checker import (
    TypeIssue,
    TypeCheckResult,
    check_type,
    typecheck_entries,
)


def _entry(key: str, value: str, line: int = 1) -> EnvEntry:
    return EnvEntry(key=key, value=value, line=line)


# --- check_type unit tests ---

@pytest.mark.parametrize("value", ["42", "-1", "0"])
def test_check_type_int_valid(value):
    assert check_type(value, "int") is True


@pytest.mark.parametrize("value", ["3.14", "abc", ""])
def test_check_type_int_invalid(value):
    assert check_type(value, "int") is False


@pytest.mark.parametrize("value", ["true", "false", "1", "0", "yes", "no", "True", "FALSE"])
def test_check_type_bool_valid(value):
    assert check_type(value, "bool") is True


def test_check_type_bool_invalid():
    assert check_type("maybe", "bool") is False


@pytest.mark.parametrize("value", ["http://example.com", "https://api.example.com/v1"])
def test_check_type_url_valid(value):
    assert check_type(value, "url") is True


def test_check_type_url_invalid():
    assert check_type("not-a-url", "url") is False


@pytest.mark.parametrize("value", ["80", "443", "8080", "65535"])
def test_check_type_port_valid(value):
    assert check_type(value, "port") is True


@pytest.mark.parametrize("value", ["0", "65536", "99999", "abc"])
def test_check_type_port_invalid(value):
    assert check_type(value, "port") is False


def test_check_type_unknown_type_always_passes():
    assert check_type("anything", "uuid") is True


# --- typecheck_entries integration tests ---

def test_no_issues_when_schema_is_none():
    entries = [_entry("PORT", "not-a-number")]
    result = typecheck_entries(entries, schema=None)
    assert not result.has_issues


def test_no_issues_when_schema_is_empty():
    entries = [_entry("PORT", "abc")]
    result = typecheck_entries(entries, schema={})
    assert not result.has_issues


def test_valid_entry_produces_no_issue():
    entries = [_entry("PORT", "8080", line=3)]
    result = typecheck_entries(entries, schema={"PORT": "port"})
    assert not result.has_issues


def test_invalid_entry_produces_issue():
    entries = [_entry("PORT", "not-a-port", line=5)]
    result = typecheck_entries(entries, schema={"PORT": "port"})
    assert result.has_issues
    assert result.issue_count == 1
    issue = result.issues[0]
    assert issue.key == "PORT"
    assert issue.expected_type == "port"
    assert issue.line == 5


def test_only_schema_keys_are_checked():
    entries = [
        _entry("PORT", "bad", line=1),
        _entry("DEBUG", "yes", line=2),
    ]
    result = typecheck_entries(entries, schema={"DEBUG": "bool"})
    assert not result.has_issues


def test_type_issue_str_representation():
    issue = TypeIssue(key="TIMEOUT", value="abc", expected_type="int", line=7)
    text = str(issue)
    assert "TIMEOUT" in text
    assert "int" in text
    assert "abc" in text
    assert "7" in text
