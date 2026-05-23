"""Tests for envoy_config_lint.encoder."""
import pytest
from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.encoder import (
    check_encoding,
    _has_unescaped_newline,
    _has_control_characters,
    _has_non_ascii,
    EncodingResult,
)


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, line_number=1, raw="")


def test_no_issues_for_clean_values():
    entries = [_entry("HOST", "localhost"), _entry("PORT", "8080")]
    result = check_encoding(entries)
    assert not result.has_issues()
    assert result.issue_count() == 0


def test_detects_literal_newline():
    entries = [_entry("MSG", "hello\nworld")]
    result = check_encoding(entries)
    assert result.has_issues()
    assert any("newline" in i.message for i in result.issues)


def test_detects_carriage_return():
    entries = [_entry("MSG", "hello\rworld")]
    result = check_encoding(entries)
    assert any("newline" in i.message for i in result.issues)


def test_detects_control_character():
    entries = [_entry("CTRL", "val\x07ue")]
    result = check_encoding(entries)
    assert any("control" in i.message for i in result.issues)


def test_detects_non_ascii():
    entries = [_entry("GREETING", "héllo")]
    result = check_encoding(entries)
    assert any("non-ASCII" in i.message for i in result.issues)


def test_multiple_issues_same_entry():
    # Both non-ASCII and a control char in the same value
    entries = [_entry("BAD", "caf\xe9\x07")]
    result = check_encoding(entries)
    assert result.issue_count() >= 2


def test_has_unescaped_newline_true():
    assert _has_unescaped_newline("a\nb") is True


def test_has_unescaped_newline_false_for_escaped():
    # Escaped \n as two characters is fine
    assert _has_unescaped_newline("a\\nb") is False


def test_has_control_characters_false_for_tab():
    # Tab (0x09) is excluded from the control-char pattern
    assert _has_control_characters("a\tb") is False


def test_has_non_ascii_false_for_plain_ascii():
    assert _has_non_ascii("simple_value_123") is False


def test_encoding_result_issue_count():
    r = EncodingResult()
    assert r.issue_count() == 0
    assert not r.has_issues()
