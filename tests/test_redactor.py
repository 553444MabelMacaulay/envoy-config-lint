"""Tests for envoy_config_lint.redactor module."""

import pytest

from envoy_config_lint.parser import EnvEntry, ParseResult
from envoy_config_lint.redactor import (
    REDACTED_PLACEHOLDER,
    RedactResult,
    redact_parse_result,
    render_redacted,
    _is_sensitive,
    DEFAULT_SENSITIVE_PATTERNS,
)


def _make_result(*pairs) -> ParseResult:
    entries = [
        EnvEntry(key=k, value=v, line_number=i + 1)
        for i, (k, v) in enumerate(pairs)
    ]
    return ParseResult(entries=entries)


# --- _is_sensitive ---

def test_is_sensitive_with_secret_key():
    assert _is_sensitive("DB_SECRET", DEFAULT_SENSITIVE_PATTERNS) is True


def test_is_sensitive_with_token_key():
    assert _is_sensitive("GITHUB_TOKEN", DEFAULT_SENSITIVE_PATTERNS) is True


def test_is_sensitive_case_insensitive():
    assert _is_sensitive("github_token", DEFAULT_SENSITIVE_PATTERNS) is True


def test_is_not_sensitive_for_plain_key():
    assert _is_sensitive("APP_NAME", DEFAULT_SENSITIVE_PATTERNS) is False


# --- redact_parse_result ---

def test_sensitive_value_is_redacted():
    result = _make_result(("API_KEY", "abc123"))
    redacted = redact_parse_result(result)
    assert redacted.entries[0].value == REDACTED_PLACEHOLDER
    assert redacted.entries[0].redacted is True


def test_non_sensitive_value_is_preserved():
    result = _make_result(("APP_NAME", "myapp"))
    redacted = redact_parse_result(result)
    assert redacted.entries[0].value == "myapp"
    assert redacted.entries[0].redacted is False


def test_mixed_entries_redaction():
    result = _make_result(
        ("APP_NAME", "myapp"),
        ("DB_PASSWORD", "s3cr3t"),
        ("PORT", "8080"),
        ("AUTH_TOKEN", "tok-xyz"),
    )
    redacted = redact_parse_result(result)
    assert redacted.redacted_count == 2
    assert redacted.total_count == 4


def test_extra_patterns_are_applied():
    result = _make_result(("STRIPE_WEBHOOK", "whsec_abc"))
    redacted = redact_parse_result(result, extra_patterns={"WEBHOOK"})
    assert redacted.entries[0].redacted is True


def test_extra_patterns_case_insensitive():
    result = _make_result(("stripe_webhook", "whsec_abc"))
    redacted = redact_parse_result(result, extra_patterns={"webhook"})
    assert redacted.entries[0].redacted is True


def test_redacted_count_zero_when_no_sensitive():
    result = _make_result(("HOST", "localhost"), ("PORT", "5432"))
    redacted = redact_parse_result(result)
    assert redacted.redacted_count == 0


# --- render_redacted ---

def test_render_redacted_output():
    result = _make_result(("APP_NAME", "myapp"), ("API_KEY", "secret"))
    redacted = redact_parse_result(result)
    output = render_redacted(redacted)
    assert "APP_NAME=myapp" in output
    assert f"API_KEY={REDACTED_PLACEHOLDER}" in output


def test_render_empty_result():
    redacted = RedactResult(entries=[])
    assert render_redacted(redacted) == ""
