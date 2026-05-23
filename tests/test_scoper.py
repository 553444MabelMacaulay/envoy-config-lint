"""Tests for envoy_config_lint.scoper and envoy_config_lint.rules_scope."""

from __future__ import annotations

from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.scoper import _extract_scope_token, scope_entries
from envoy_config_lint.rules_scope import rule_mixed_env_scopes


def _entry(key: str, value: str = "value") -> EnvEntry:
    return EnvEntry(key=key, value=value, line_number=1, raw="")


# --- _extract_scope_token ---

def test_extract_scope_token_dev():
    assert _extract_scope_token("DEV_HOST") == "DEV"


def test_extract_scope_token_prod():
    assert _extract_scope_token("PROD_DATABASE_URL") == "PROD"


def test_extract_scope_token_staging():
    assert _extract_scope_token("STAGING_SECRET") == "STAGING"


def test_extract_scope_token_case_insensitive():
    assert _extract_scope_token("dev_host") == "DEV"


def test_extract_scope_token_none_for_plain_key():
    assert _extract_scope_token("DATABASE_URL") is None


def test_extract_scope_token_none_for_no_separator():
    assert _extract_scope_token("HOST") is None


# --- scope_entries ---

def test_no_issues_when_single_scope():
    entries = [_entry("DEV_HOST"), _entry("DEV_PORT"), _entry("DEV_SECRET")]
    result = scope_entries(entries)
    assert not result.has_issues
    assert result.issue_count == 0
    assert result.scopes_found == frozenset({"DEV"})


def test_no_issues_when_no_scope_tokens():
    entries = [_entry("HOST"), _entry("PORT"), _entry("DATABASE_URL")]
    result = scope_entries(entries)
    assert not result.has_issues
    assert result.scopes_found == frozenset()


def test_issues_when_mixed_scopes():
    entries = [_entry("DEV_HOST"), _entry("PROD_HOST")]
    result = scope_entries(entries)
    assert result.has_issues
    assert result.issue_count == 2
    assert "DEV" in result.scopes_found
    assert "PROD" in result.scopes_found


def test_keys_by_scope_populated():
    entries = [_entry("DEV_HOST"), _entry("DEV_PORT"), _entry("STAGING_HOST")]
    result = scope_entries(entries)
    assert result.keys_by_scope["DEV"] == ["DEV_HOST", "DEV_PORT"]
    assert result.keys_by_scope["STAGING"] == ["STAGING_HOST"]


def test_issue_references_detected_scope():
    entries = [_entry("DEV_HOST"), _entry("PROD_HOST")]
    result = scope_entries(entries)
    scopes_in_issues = {i.detected_scope for i in result.issues}
    assert scopes_in_issues == {"DEV", "PROD"}


# --- rule_mixed_env_scopes ---

def test_rule_returns_no_issues_for_single_scope():
    entries = [_entry("DEV_HOST"), _entry("DEV_PORT")]
    issues = rule_mixed_env_scopes(entries)
    assert issues == []


def test_rule_returns_warnings_for_mixed_scopes():
    entries = [_entry("DEV_HOST"), _entry("PROD_HOST")]
    issues = rule_mixed_env_scopes(entries)
    assert len(issues) == 2
    assert all(i.severity == "warning" for i in issues)
    assert all(i.rule == "mixed-env-scopes" for i in issues)


def test_rule_issue_keys_match_entries():
    entries = [_entry("CI_HOST"), _entry("STAGING_HOST")]
    issues = rule_mixed_env_scopes(entries)
    keys = {i.key for i in issues}
    assert keys == {"CI_HOST", "STAGING_HOST"}
