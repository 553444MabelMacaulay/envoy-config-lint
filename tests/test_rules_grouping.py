"""Tests for envoy_config_lint.rules_grouping."""
from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.rules_grouping import (
    rule_inconsistent_prefix_casing,
    rule_singleton_prefix,
)


def _entry(key: str, value: str = "v", line: int = 1) -> EnvEntry:
    return EnvEntry(key=key, value=value, line=line)


# --- rule_inconsistent_prefix_casing ---

def test_no_issues_when_all_uppercase_in_group():
    entries = [_entry("DB_HOST"), _entry("DB_PORT")]
    assert rule_inconsistent_prefix_casing(entries) == []


def test_no_issues_for_single_key():
    entries = [_entry("PORT")]
    assert rule_inconsistent_prefix_casing(entries) == []


def test_detects_mixed_casing_within_group():
    entries = [
        _entry("DB_HOST", line=1),   # uppercase
        _entry("DB_port", line=2),   # lowercase suffix makes key != upper
    ]
    issues = rule_inconsistent_prefix_casing(entries)
    assert len(issues) == 1
    assert issues[0].code == "W006"
    assert "DB" in issues[0].message
    assert issues[0].severity == "warning"


def test_no_cross_group_interference():
    entries = [
        _entry("DB_HOST"),
        _entry("DB_PORT"),
        _entry("app_name"),
        _entry("app_env"),
    ]
    # Both groups are internally consistent — no issues
    issues = rule_inconsistent_prefix_casing(entries)
    assert issues == []


# --- rule_singleton_prefix ---

def test_no_issues_when_no_singleton_prefixes():
    entries = [_entry("DB_HOST"), _entry("DB_PORT")]
    assert rule_singleton_prefix(entries) == []


def test_detects_singleton_prefix():
    entries = [
        _entry("DB_HOST", line=1),
        _entry("DB_PORT", line=2),
        _entry("LONE_KEY", line=5),
    ]
    issues = rule_singleton_prefix(entries)
    assert len(issues) == 1
    assert issues[0].code == "I001"
    assert "LONE_KEY" in issues[0].message
    assert issues[0].severity == "info"


def test_no_issue_for_key_without_separator():
    entries = [_entry("PORT", line=1)]
    issues = rule_singleton_prefix(entries)
    assert issues == []
