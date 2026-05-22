"""Tests for the envoy_config_lint.validator module."""

import pytest

from envoy_config_lint.parser import EnvEntry, ParseResult
from envoy_config_lint.validator import EnvSchema, validate_against_schema


def _make_parse_result(*key_value_pairs):
    """Helper to build a ParseResult from (key, value, line) tuples."""
    entries = [
        EnvEntry(key=k, value=v, line=ln) for k, v, ln in key_value_pairs
    ]
    return ParseResult(entries=entries, errors=[])


def test_missing_required_key_is_error():
    schema = EnvSchema(required_keys={"DATABASE_URL", "SECRET_KEY"})
    result = _make_parse_result(("DATABASE_URL", "postgres://localhost/db", 1))
    validation = validate_against_schema(result, schema, source=".env")

    errors = [i for i in validation.issues if i.severity == "error"]
    assert len(errors) == 1
    assert "SECRET_KEY" in errors[0].message
    assert validation.is_valid is False


def test_all_required_keys_present_no_errors():
    schema = EnvSchema(required_keys={"HOST", "PORT"})
    result = _make_parse_result(("HOST", "localhost", 1), ("PORT", "8080", 2))
    validation = validate_against_schema(result, schema)

    errors = [i for i in validation.issues if i.severity == "error"]
    assert errors == []
    assert validation.is_valid is True


def test_unknown_key_emits_warning():
    schema = EnvSchema(required_keys={"APP_ENV"}, optional_keys={"LOG_LEVEL"})
    result = _make_parse_result(
        ("APP_ENV", "production", 1),
        ("LOG_LEVEL", "info", 2),
        ("MYSTERY_VAR", "42", 3),
    )
    validation = validate_against_schema(result, schema, source=".env.prod")

    warnings = [i for i in validation.issues if i.severity == "warning"]
    assert len(warnings) == 1
    assert "MYSTERY_VAR" in warnings[0].message
    assert warnings[0].line == 3


def test_no_warnings_when_schema_is_empty():
    """When no schema keys are defined, unknown keys should not be flagged."""
    schema = EnvSchema()
    result = _make_parse_result(("ANYTHING", "value", 1))
    validation = validate_against_schema(result, schema)

    assert validation.issues == []


def test_multiple_missing_required_keys():
    schema = EnvSchema(required_keys={"A", "B", "C"})
    result = _make_parse_result()
    validation = validate_against_schema(result, schema)

    error_rules = [i.rule for i in validation.issues]
    assert error_rules.count("missing_required_key") == 3


def test_validation_result_is_valid_with_only_warnings():
    schema = EnvSchema(required_keys=set(), optional_keys={"KNOWN"})
    result = _make_parse_result(("UNKNOWN_KEY", "val", 5))
    validation = validate_against_schema(result, schema)

    warnings = [i for i in validation.issues if i.severity == "warning"]
    assert len(warnings) == 1
    assert validation.is_valid is True
