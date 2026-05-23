"""Tests for envoy_config_lint.sorter."""

import pytest
from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.sorter import (
    SortResult,
    is_sorted_count,
    total_count,
    sort_entries,
)


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, line_number=1, raw=f"{key}={value}")


def test_already_sorted_returns_is_sorted_true():
    entries = [_entry("ALPHA"), _entry("BETA"), _entry("GAMMA")]
    result = sort_entries(entries)
    assert result.is_sorted is True
    assert result.out_of_order == []


def test_unsorted_entries_detected():
    entries = [_entry("GAMMA"), _entry("ALPHA"), _entry("BETA")]
    result = sort_entries(entries)
    assert result.is_sorted is False
    assert len(result.out_of_order) > 0


def test_sorted_entries_are_in_alphabetical_order():
    entries = [_entry("ZEBRA"), _entry("APPLE"), _entry("MANGO")]
    result = sort_entries(entries)
    keys = [e.key for e in result.sorted_entries]
    assert keys == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_is_case_insensitive_by_default():
    entries = [_entry("zebra"), _entry("APPLE"), _entry("Mango")]
    result = sort_entries(entries)
    keys = [e.key for e in result.sorted_entries]
    assert keys == ["APPLE", "Mango", "zebra"]


def test_sort_case_sensitive_option():
    entries = [_entry("b"), _entry("A"), _entry("C")]
    result = sort_entries(entries, case_sensitive=True)
    keys = [e.key for e in result.sorted_entries]
    # uppercase letters come before lowercase in ASCII
    assert keys == ["A", "C", "b"]


def test_group_by_prefix_keeps_groups_together():
    entries = [
        _entry("DB_HOST"),
        _entry("APP_NAME"),
        _entry("DB_PORT"),
        _entry("APP_ENV"),
    ]
    result = sort_entries(entries, group_by_prefix=True)
    keys = [e.key for e in result.sorted_entries]
    # APP group first, then DB group
    assert keys.index("APP_ENV") < keys.index("APP_NAME") or keys.index("APP_NAME") < keys.index("DB_HOST")
    app_keys = [k for k in keys if k.startswith("APP_")]
    db_keys = [k for k in keys if k.startswith("DB_")]
    assert app_keys == sorted(app_keys)
    assert db_keys == sorted(db_keys)
    assert keys.index(app_keys[-1]) < keys.index(db_keys[0])


def test_is_sorted_count_returns_number_of_out_of_order_keys():
    entries = [_entry("GAMMA"), _entry("ALPHA"), _entry("BETA")]
    result = sort_entries(entries)
    assert is_sorted_count(result) == len(result.out_of_order)


def test_total_count_returns_all_entries():
    entries = [_entry("A"), _entry("B"), _entry("C")]
    result = sort_entries(entries)
    assert total_count(result) == 3


def test_empty_entries_returns_sorted_true():
    result = sort_entries([])
    assert result.is_sorted is True
    assert result.sorted_entries == []
    assert result.out_of_order == []


def test_single_entry_is_always_sorted():
    entries = [_entry("ONLY_KEY")]
    result = sort_entries(entries)
    assert result.is_sorted is True
