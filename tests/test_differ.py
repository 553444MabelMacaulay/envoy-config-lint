"""Tests for the differ module."""
import pytest

from envoy_config_lint.differ import diff_env_files, DiffResult
from envoy_config_lint.parser import ParseResult, EnvEntry


def _make_result(*keys: str) -> ParseResult:
    entries = [EnvEntry(key=k, value="value", line_number=i + 1) for i, k in enumerate(keys)]
    return ParseResult(entries=entries, errors=[])


def test_no_differences_when_keys_match():
    base = _make_result("FOO", "BAR")
    compare = _make_result("FOO", "BAR")
    result = diff_env_files(base, compare)
    assert not result.has_differences
    assert result.missing_in_compare == []
    assert result.extra_in_compare == []
    assert sorted(result.common_keys) == ["BAR", "FOO"]


def test_missing_keys_detected():
    base = _make_result("FOO", "BAR", "BAZ")
    compare = _make_result("FOO")
    result = diff_env_files(base, compare)
    assert result.has_differences
    assert "BAR" in result.missing_in_compare
    assert "BAZ" in result.missing_in_compare
    assert result.missing_count == 2


def test_extra_keys_detected():
    base = _make_result("FOO")
    compare = _make_result("FOO", "EXTRA_KEY")
    result = diff_env_files(base, compare)
    assert result.has_differences
    assert "EXTRA_KEY" in result.extra_in_compare
    assert result.extra_count == 1


def test_missing_and_extra_simultaneously():
    base = _make_result("FOO", "BAR")
    compare = _make_result("FOO", "NEW_KEY")
    result = diff_env_files(base, compare, "base.env", "compare.env")
    assert "BAR" in result.missing_in_compare
    assert "NEW_KEY" in result.extra_in_compare
    assert result.common_keys == ["FOO"]
    assert result.base_file == "base.env"
    assert result.compare_file == "compare.env"


def test_empty_files_have_no_differences():
    base = _make_result()
    compare = _make_result()
    result = diff_env_files(base, compare)
    assert not result.has_differences


def test_missing_count_and_extra_count_properties():
    base = _make_result("A", "B", "C")
    compare = _make_result("A", "D", "E")
    result = diff_env_files(base, compare)
    assert result.missing_count == 2  # B, C
    assert result.extra_count == 2    # D, E
