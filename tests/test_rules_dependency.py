"""Tests for envoy_config_lint.rules_dependency."""
from __future__ import annotations

from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.rules_dependency import (
    rule_missing_dependencies,
    rule_unused_variables,
)


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}", line_number=1)


# --- rule_missing_dependencies ---

def test_no_errors_when_all_refs_defined():
    entries = [_entry("HOST", "localhost"), _entry("URL", "${HOST}/path")]
    issues = rule_missing_dependencies(entries)
    assert issues == []


def test_error_for_undefined_reference():
    entries = [_entry("URL", "${UNDEFINED}/path")]
    issues = rule_missing_dependencies(entries)
    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert issues[0].key == "URL"
    assert "UNDEFINED" in issues[0].message


def test_multiple_errors_for_multiple_missing_refs():
    entries = [_entry("COMBO", "${A}-${B}-${C}")]
    issues = rule_missing_dependencies(entries)
    assert len(issues) == 3
    keys_mentioned = {i.message for i in issues}
    assert all(any(k in m for m in keys_mentioned) for k in ("A", "B", "C"))


def test_no_errors_when_no_interpolation():
    entries = [_entry("PLAIN", "just_a_value")]
    issues = rule_missing_dependencies(entries)
    assert issues == []


# --- rule_unused_variables ---

def test_no_warnings_when_all_keys_referenced():
    entries = [
        _entry("BASE", "http://localhost"),
        _entry("FULL", "${BASE}/api"),
    ]
    # BASE is referenced, FULL is not — only FULL should be warned
    issues = rule_unused_variables(entries)
    unused_keys = {i.key for i in issues}
    assert "BASE" not in unused_keys
    assert "FULL" in unused_keys


def test_warning_for_unreferenced_key():
    entries = [_entry("ORPHAN", "value")]
    issues = rule_unused_variables(entries)
    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert issues[0].key == "ORPHAN"


def test_no_warnings_for_empty_entries():
    issues = rule_unused_variables([])
    assert issues == []
