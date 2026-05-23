"""Tests for envoy_config_lint.deprecation."""
import pytest

from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.deprecation import (
    DeprecationIssue,
    DeprecationResult,
    check_deprecations,
    build_registry,
)


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, line_number=1)


REGISTRY = {
    "OLD_API_KEY": ("Replaced by new auth system", "NEW_API_KEY"),
    "LEGACY_HOST": ("No longer supported", None),
}


def test_no_issues_when_no_deprecated_keys():
    entries = [_entry("DATABASE_URL"), _entry("PORT")]
    result = check_deprecations(entries, REGISTRY)
    assert not result.has_issues()
    assert result.issue_count() == 0


def test_detects_deprecated_key_with_replacement():
    entries = [_entry("OLD_API_KEY", "abc123")]
    result = check_deprecations(entries, REGISTRY)
    assert result.has_issues()
    assert result.issue_count() == 1
    issue = result.issues[0]
    assert issue.key == "OLD_API_KEY"
    assert issue.replacement == "NEW_API_KEY"
    assert "Replaced by new auth system" in issue.message


def test_detects_deprecated_key_without_replacement():
    entries = [_entry("LEGACY_HOST", "localhost")]
    result = check_deprecations(entries, REGISTRY)
    assert result.has_issues()
    issue = result.issues[0]
    assert issue.replacement is None


def test_detects_multiple_deprecated_keys():
    entries = [_entry("OLD_API_KEY"), _entry("LEGACY_HOST"), _entry("VALID_KEY")]
    result = check_deprecations(entries, REGISTRY)
    assert result.issue_count() == 2


def test_issue_str_with_replacement():
    issue = DeprecationIssue(key="OLD", message="outdated", replacement="NEW")
    text = str(issue)
    assert "OLD" in text
    assert "outdated" in text
    assert "NEW" in text


def test_issue_str_without_replacement():
    issue = DeprecationIssue(key="OLD", message="outdated")
    text = str(issue)
    assert "OLD" in text
    assert "Use" not in text


def test_build_registry_with_replacement():
    raw = {"OLD_KEY": {"message": "gone", "replacement": "NEW_KEY"}}
    registry = build_registry(raw)
    assert "OLD_KEY" in registry
    assert registry["OLD_KEY"] == ("gone", "NEW_KEY")


def test_build_registry_without_replacement():
    raw = {"OLD_KEY": {"message": "removed"}}
    registry = build_registry(raw)
    assert registry["OLD_KEY"] == ("removed", None)


def test_build_registry_default_message():
    raw = {"OLD_KEY": {}}
    registry = build_registry(raw)
    message, replacement = registry["OLD_KEY"]
    assert message == "deprecated"
    assert replacement is None
