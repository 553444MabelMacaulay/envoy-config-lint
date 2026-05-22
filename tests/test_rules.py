"""Tests for built-in lint rules."""

import pytest

from envoy_config_lint.parser import parse_env_file
from envoy_config_lint.rules import (
    rule_duplicate_keys,
    rule_empty_value,
    rule_uppercase_keys,
    rule_unquoted_spaces,
    run_rules,
)


def _entries(content: str):
    return parse_env_file(content).entries


def test_duplicate_keys_detected():
    entries = _entries('FOO=1\nFOO=2')
    issues = rule_duplicate_keys(entries)
    assert len(issues) == 1
    assert issues[0].rule_id == 'E001'
    assert issues[0].line_number == 2


def test_no_duplicate_keys():
    entries = _entries('FOO=1\nBAR=2')
    assert rule_duplicate_keys(entries) == []


def test_empty_value_warning():
    entries = _entries('EMPTY=')
    issues = rule_empty_value(entries)
    assert len(issues) == 1
    assert issues[0].rule_id == 'W001'


def test_no_empty_value_warning_for_non_empty():
    entries = _entries('FOO=bar')
    assert rule_empty_value(entries) == []


def test_lowercase_key_warning():
    entries = _entries('my_var=value')
    issues = rule_uppercase_keys(entries)
    assert len(issues) == 1
    assert issues[0].rule_id == 'W002'


def test_uppercase_key_no_warning():
    entries = _entries('MY_VAR=value')
    assert rule_uppercase_keys(entries) == []


def test_unquoted_spaces_warning():
    entries = _entries('GREETING=hello world')
    issues = rule_unquoted_spaces(entries)
    assert len(issues) == 1
    assert issues[0].rule_id == 'W003'


def test_quoted_spaces_no_warning():
    entries = _entries('GREETING="hello world"')
    assert rule_unquoted_spaces(entries) == []


def test_run_rules_aggregates_all():
    content = 'foo=\nfoo=bar'
    result = parse_env_file(content)
    issues = run_rules(result)
    rule_ids = {i.rule_id for i in issues}
    assert 'E001' in rule_ids  # duplicate
    assert 'W002' in rule_ids  # lowercase
