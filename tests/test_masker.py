"""Tests for envoy_config_lint.masker."""

import pytest

from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.masker import (
    MaskedEntry,
    MaskResult,
    _mask_value,
    mask_entries,
)


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, line_number=1)


# ---------------------------------------------------------------------------
# _mask_value unit tests
# ---------------------------------------------------------------------------

def test_mask_value_returns_asterisks():
    assert _mask_value("supersecret") == "********"


def test_mask_value_empty_string_unchanged():
    assert _mask_value("") == ""


def test_mask_value_partial_reveals_prefix():
    result = _mask_value("abcdefgh", partial=True)
    assert result.startswith("abcd")
    assert "********" in result


def test_mask_value_partial_short_value_fully_masked():
    # Value shorter than _PARTIAL_VISIBLE → full mask
    result = _mask_value("ab", partial=True)
    assert result == "********"


# ---------------------------------------------------------------------------
# mask_entries integration tests
# ---------------------------------------------------------------------------

def test_non_sensitive_key_not_masked():
    entries = [_entry("APP_NAME", "myapp")]
    result = mask_entries(entries)
    assert result.entries[0].was_masked is False
    assert result.entries[0].masked_value == "myapp"


def test_sensitive_key_is_masked():
    entries = [_entry("DB_PASSWORD", "s3cr3t")]
    result = mask_entries(entries)
    assert result.entries[0].was_masked is True
    assert result.entries[0].masked_value == "********"
    assert result.entries[0].original_value == "s3cr3t"


def test_token_key_is_masked():
    entries = [_entry("GITHUB_TOKEN", "ghp_abc123")]
    result = mask_entries(entries)
    assert result.entries[0].was_masked is True


def test_secret_key_is_masked():
    entries = [_entry("API_SECRET", "topsecret")]
    result = mask_entries(entries)
    assert result.entries[0].was_masked is True


def test_masked_count_reflects_only_sensitive():
    entries = [
        _entry("APP_NAME", "myapp"),
        _entry("DB_PASSWORD", "pass"),
        _entry("REDIS_SECRET", "abc"),
    ]
    result = mask_entries(entries)
    assert result.masked_count() == 2
    assert result.total_count() == 3


def test_partial_masking_mode():
    entries = [_entry("DB_PASSWORD", "supersecretvalue")]
    result = mask_entries(entries, partial=True)
    entry = result.entries[0]
    assert entry.was_masked is True
    assert entry.masked_value.startswith("supe")
    assert entry.masked_value != entry.original_value


def test_empty_entries_returns_empty_result():
    result = mask_entries([])
    assert result.total_count() == 0
    assert result.masked_count() == 0
