"""Tests for envoy_config_lint.comparator."""
import pytest
from envoy_config_lint.parser import ParseResult, EnvEntry
from envoy_config_lint.comparator import compare_env_files, CompareResult


def _make_result(*pairs) -> ParseResult:
    entries = [EnvEntry(key=k, value=v, line_number=i + 1, raw=f"{k}={v}") for i, (k, v) in enumerate(pairs)]
    return ParseResult(entries=entries, errors=[])


def test_no_diffs_when_identical():
    a = _make_result(("FOO", "bar"), ("BAZ", "qux"))
    b = _make_result(("FOO", "bar"), ("BAZ", "qux"))
    result = compare_env_files(a, b)
    assert not result.has_diffs()
    assert result.changed_count() == 0


def test_detects_changed_value():
    a = _make_result(("FOO", "old"))
    b = _make_result(("FOO", "new"))
    result = compare_env_files(a, b)
    assert result.has_diffs()
    assert result.changed_count() == 1
    assert result.diffs[0].key == "FOO"
    assert result.diffs[0].kind == "changed"
    assert result.diffs[0].value_a == "old"
    assert result.diffs[0].value_b == "new"


def test_detects_key_missing_in_b():
    a = _make_result(("ONLY_A", "1"), ("SHARED", "x"))
    b = _make_result(("SHARED", "x"))
    result = compare_env_files(a, b)
    assert result.missing_in_b_count() == 1
    assert result.diffs[0].key == "ONLY_A"
    assert result.diffs[0].kind == "missing_in_b"


def test_detects_key_missing_in_a():
    a = _make_result(("SHARED", "x"))
    b = _make_result(("SHARED", "x"), ("ONLY_B", "2"))
    result = compare_env_files(a, b)
    assert result.missing_in_a_count() == 1
    assert result.diffs[0].key == "ONLY_B"
    assert result.diffs[0].kind == "missing_in_a"


def test_mixed_diffs():
    a = _make_result(("A", "1"), ("B", "old"), ("C", "3"))
    b = _make_result(("B", "new"), ("C", "3"), ("D", "4"))
    result = compare_env_files(a, b)
    assert result.changed_count() == 1
    assert result.missing_in_b_count() == 1
    assert result.missing_in_a_count() == 1


def test_empty_files_have_no_diffs():
    a = _make_result()
    b = _make_result()
    result = compare_env_files(a, b)
    assert not result.has_diffs()


def test_value_diff_str_changed():
    a = _make_result(("KEY", "v1"))
    b = _make_result(("KEY", "v2"))
    diff = compare_env_files(a, b).diffs[0]
    assert "KEY" in str(diff)
    assert "v1" in str(diff)
    assert "v2" in str(diff)
