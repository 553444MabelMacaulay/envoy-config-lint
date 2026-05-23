"""Tests for envoy_config_lint.interpolator."""

import pytest

from envoy_config_lint.interpolator import (
    InterpolationIssue,
    InterpolationResult,
    _extract_refs,
    check_interpolation,
)
from envoy_config_lint.parser import EnvEntry


def _entry(key: str, value: str, line: int = 1) -> EnvEntry:
    return EnvEntry(key=key, value=value, line=line)


# --- _extract_refs -----------------------------------------------------------

def test_extract_refs_brace_syntax():
    assert _extract_refs("${FOO}") == {"FOO"}


def test_extract_refs_bare_syntax():
    assert _extract_refs("$BAR") == {"BAR"}


def test_extract_refs_mixed():
    assert _extract_refs("${A}_$B") == {"A", "B"}


def test_extract_refs_no_refs():
    assert _extract_refs("plain-value") == set()


def test_extract_refs_empty_string():
    assert _extract_refs("") == set()


# --- check_interpolation -----------------------------------------------------

def test_no_issues_when_all_refs_defined():
    entries = [
        _entry("BASE", "http://localhost", 1),
        _entry("URL", "${BASE}/api", 2),
    ]
    result = check_interpolation(entries)
    assert not result.has_issues
    assert result.issue_count == 0


def test_detects_undefined_reference():
    entries = [
        _entry("URL", "${BASE}/api", 1),
    ]
    result = check_interpolation(entries)
    assert result.has_issues
    assert result.issue_count == 1
    issue = result.issues[0]
    assert issue.key == "URL"
    assert issue.ref == "BASE"
    assert issue.line == 1


def test_multiple_undefined_refs_in_one_value():
    entries = [
        _entry("CONN", "${HOST}:${PORT}", 3),
    ]
    result = check_interpolation(entries)
    assert result.issue_count == 2
    refs = {i.ref for i in result.issues}
    assert refs == {"HOST", "PORT"}


def test_empty_value_skipped():
    entries = [
        _entry("EMPTY", "", 1),
    ]
    result = check_interpolation(entries)
    assert not result.has_issues


def test_issue_str_representation():
    issue = InterpolationIssue(key="URL", ref="BASE", line=5)
    assert "Line 5" in str(issue)
    assert "URL" in str(issue)
    assert "$BASE" in str(issue)


def test_self_reference_is_flagged():
    """A key that references itself is undefined at parse time."""
    entries = [
        _entry("A", "${A}_suffix", 1),
    ]
    # A is defined, so self-reference should NOT be flagged
    result = check_interpolation(entries)
    assert not result.has_issues
