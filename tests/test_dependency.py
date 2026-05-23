"""Tests for envoy_config_lint.dependency."""
from __future__ import annotations

import pytest
from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.dependency import check_dependencies, DependencyResult


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}", line_number=1)


def test_no_issues_when_no_interpolation():
    entries = [_entry("FOO", "bar"), _entry("BAZ", "qux")]
    result = check_dependencies(entries)
    assert not result.has_issues()
    assert result.issue_count() == 0


def test_no_issues_when_reference_is_defined():
    entries = [_entry("BASE", "http://localhost"), _entry("URL", "${BASE}/api")]
    result = check_dependencies(entries)
    assert not result.has_issues()


def test_detects_missing_dependency():
    entries = [_entry("URL", "${BASE}/api")]
    result = check_dependencies(entries)
    assert result.has_issues()
    assert result.issue_count() == 1
    issue = result.issues[0]
    assert issue.kind == "missing_dependency"
    assert issue.key == "URL"
    assert issue.referenced_key == "BASE"
    assert issue.severity == "error"


def test_detects_multiple_missing_dependencies():
    entries = [_entry("COMBINED", "${HOST}:${PORT}")]
    result = check_dependencies(entries)
    assert result.issue_count() == 2
    kinds = {i.kind for i in result.issues}
    assert kinds == {"missing_dependency"}


def test_unused_key_not_reported_by_default():
    entries = [_entry("SOLO", "standalone"), _entry("URL", "${SOLO}/path")]
    result = check_dependencies(entries, report_unused=False)
    assert not result.has_issues()


def test_unused_key_reported_when_flag_set():
    entries = [
        _entry("BASE", "http://localhost"),
        _entry("URL", "${BASE}/api"),
    ]
    result = check_dependencies(entries, report_unused=True)
    # URL is not referenced by anything; BASE is referenced by URL
    unused = [i for i in result.issues if i.kind == "unused_key"]
    assert any(i.key == "URL" for i in unused)


def test_dependency_issue_str_missing():
    entries = [_entry("X", "${MISSING}")]
    result = check_dependencies(entries)
    issue_str = str(result.issues[0])
    assert "MISSING" in issue_str
    assert "not defined" in issue_str


def test_dependency_issue_str_unused():
    entries = [_entry("ORPHAN", "value")]
    result = check_dependencies(entries, report_unused=True)
    issue_str = str(result.issues[0])
    assert "ORPHAN" in issue_str
    assert "never referenced" in issue_str


def test_self_reference_is_missing():
    """A key referencing itself is still considered missing (circular)."""
    entries = [_entry("A", "${A}_suffix")]
    result = check_dependencies(entries)
    # A references A; A is defined — should NOT be flagged as missing
    assert not result.has_issues()
