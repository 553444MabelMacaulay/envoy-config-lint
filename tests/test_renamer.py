"""Tests for envoy_config_lint.renamer."""

import pytest
from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.renamer import (
    RenameResult,
    RenameIssue,
    _suggest_canonical,
    suggest_renames,
)


def _entry(key: str, value: str = "val", line: int = 1) -> EnvEntry:
    return EnvEntry(key=key, value=value, line_number=line, raw=f"{key}={value}")


# --- _suggest_canonical ---

def test_suggest_canonical_already_upper_returns_none():
    assert _suggest_canonical("MY_KEY") is None


def test_suggest_canonical_lowercase_returns_upper():
    assert _suggest_canonical("my_key") == "MY_KEY"


def test_suggest_canonical_strips_leading_underscores():
    assert _suggest_canonical("_PRIVATE") == "PRIVATE"


def test_suggest_canonical_strips_trailing_underscores():
    assert _suggest_canonical("KEY_") == "KEY"


def test_suggest_canonical_mixed_case_and_underscores():
    result = _suggest_canonical("_myKey_")
    assert result == "MYKEY"


# --- suggest_renames: canonical suggestions ---

def test_no_issues_for_already_canonical_keys():
    entries = [_entry("DB_HOST"), _entry("APP_PORT")]
    result = suggest_renames(entries)
    assert not result.has_issues()
    assert result.issue_count() == 0


def test_detects_lowercase_key():
    entries = [_entry("db_host", line=3)]
    result = suggest_renames(entries)
    assert result.has_issues()
    assert result.issue_count() == 1
    issue = result.issues[0]
    assert issue.old_key == "db_host"
    assert issue.new_key == "DB_HOST"
    assert issue.line_number == 3
    assert "non-canonical" in issue.reason


def test_renamed_dict_populated_for_canonical():
    entries = [_entry("app_name")]
    result = suggest_renames(entries)
    assert result.renamed["app_name"] == "APP_NAME"


# --- suggest_renames: explicit rename map ---

def test_explicit_rename_map_overrides_canonical():
    entries = [_entry("OLD_KEY", line=5)]
    result = suggest_renames(entries, rename_map={"OLD_KEY": "NEW_KEY"})
    assert result.has_issues()
    issue = result.issues[0]
    assert issue.old_key == "OLD_KEY"
    assert issue.new_key == "NEW_KEY"
    assert issue.line_number == 5
    assert "explicit" in issue.reason


def test_explicit_rename_map_populates_renamed():
    entries = [_entry("LEGACY_DB")]
    result = suggest_renames(entries, rename_map={"LEGACY_DB": "DATABASE_URL"})
    assert result.renamed["LEGACY_DB"] == "DATABASE_URL"


def test_keys_not_in_rename_map_still_checked_canonically():
    entries = [_entry("GOOD_KEY"), _entry("bad_key")]
    result = suggest_renames(entries, rename_map={"UNRELATED": "OTHER"})
    assert result.issue_count() == 1
    assert result.issues[0].old_key == "bad_key"


def test_str_representation_of_issue():
    issue = RenameIssue(old_key="old", new_key="NEW", line_number=7, reason="test")
    s = str(issue)
    assert "old" in s
    assert "NEW" in s
    assert "7" in s
    assert "test" in s
