"""Tests for envoy_config_lint.profiler."""
import pytest
from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.profiler import ProfileResult, profile_entries, _classify_key_length, _extract_prefix


def _entry(key: str, value: str, line: int = 1) -> EnvEntry:
    return EnvEntry(key=key, value=value, line=line)


# --- _classify_key_length ---

def test_short_key():
    assert _classify_key_length("FOO") == "short"


def test_medium_key():
    assert _classify_key_length("DATABASE_URL") == "medium"


def test_long_key():
    assert _classify_key_length("VERY_LONG_CONFIGURATION_KEY_NAME") == "long"


# --- _extract_prefix ---

def test_extract_prefix_returns_first_segment():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_returns_none_without_separator():
    assert _extract_prefix("NOPREFIX") is None


# --- profile_entries ---

def test_empty_entries_returns_default_profile():
    result = profile_entries([])
    assert result.total_keys == 0
    assert result.avg_value_length == 0.0


def test_total_keys_counted():
    entries = [_entry("A", "1"), _entry("B", "2"), _entry("C", "3")]
    result = profile_entries(entries)
    assert result.total_keys == 3


def test_empty_value_count():
    entries = [_entry("A", ""), _entry("B", ""), _entry("C", "value")]
    result = profile_entries(entries)
    assert result.empty_value_count == 2


def test_quoted_value_count():
    entries = [_entry("A", '"hello"'), _entry("B", "'world'"), _entry("C", "plain")]
    result = profile_entries(entries)
    assert result.quoted_value_count == 2


def test_long_value_count():
    long_val = "x" * 65
    entries = [_entry("A", long_val), _entry("B", "short")]
    result = profile_entries(entries)
    assert result.long_value_count == 1


def test_avg_value_length():
    entries = [_entry("A", "ab"), _entry("B", "abcd")]  # lengths 2 + 4 = 6 / 2 = 3.0
    result = profile_entries(entries)
    assert result.avg_value_length == 3.0


def test_prefixes_found_sorted():
    entries = [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("APP_NAME", "myapp"),
    ]
    result = profile_entries(entries)
    assert result.prefixes_found == ["APP", "DB"]


def test_key_length_distribution():
    entries = [
        _entry("FOO", "v"),          # short
        _entry("DATABASE_URL", "v"),  # medium
        _entry("VERY_LONG_CONFIGURATION_KEY_NAME", "v"),  # long
    ]
    result = profile_entries(entries)
    assert result.key_length_distribution["short"] == 1
    assert result.key_length_distribution["medium"] == 1
    assert result.key_length_distribution["long"] == 1
