"""Tests for envoy_config_lint.grouper."""
import pytest
from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.grouper import group_by_prefix, _extract_prefix, GroupResult


def _entry(key: str, value: str = "val", line: int = 1) -> EnvEntry:
    return EnvEntry(key=key, value=value, line=line)


# --- _extract_prefix ---

def test_extract_prefix_returns_first_segment():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_returns_none_without_separator():
    assert _extract_prefix("PORT") is None


def test_extract_prefix_custom_separator():
    assert _extract_prefix("APP.HOST", separator=".") == "APP"


# --- group_by_prefix ---

def test_groups_entries_sharing_prefix():
    entries = [
        _entry("DB_HOST", line=1),
        _entry("DB_PORT", line=2),
        _entry("APP_NAME", line=3),
        _entry("APP_ENV", line=4),
    ]
    result = group_by_prefix(entries)
    assert set(result.group_names()) == {"DB", "APP"}
    assert result.group_count() == 2
    assert result.entry_count_for("DB") == 2
    assert result.entry_count_for("APP") == 2
    assert result.ungrouped == []


def test_singleton_prefix_goes_to_ungrouped():
    entries = [
        _entry("DB_HOST", line=1),
        _entry("PORT", line=2),  # no separator
        _entry("LONE_KEY", line=3),  # only one with LONE prefix
    ]
    result = group_by_prefix(entries, min_group_size=2)
    assert "DB" not in result.groups  # DB also singleton here
    lone_keys = [e.key for e in result.ungrouped]
    assert "LONE_KEY" in lone_keys
    assert "PORT" in lone_keys


def test_no_entries_returns_empty_result():
    result = group_by_prefix([])
    assert result.group_count() == 0
    assert result.ungrouped == []


def test_entry_count_for_missing_prefix_is_zero():
    result = GroupResult()
    assert result.entry_count_for("MISSING") == 0


def test_min_group_size_respected():
    entries = [
        _entry("X_A", line=1),
        _entry("X_B", line=2),
        _entry("X_C", line=3),
    ]
    result = group_by_prefix(entries, min_group_size=3)
    assert result.entry_count_for("X") == 3
    assert result.ungrouped == []
