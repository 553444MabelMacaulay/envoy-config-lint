"""Tests for the .env file parser."""

import pytest

from envoy_config_lint.parser import parse_env_file


def test_simple_key_value():
    result = parse_env_file('FOO=bar')
    assert len(result.entries) == 1
    entry = result.entries[0]
    assert entry.key == 'FOO'
    assert entry.value == 'bar'
    assert not entry.is_comment
    assert not entry.is_blank


def test_blank_lines():
    result = parse_env_file('FOO=bar\n\nBAZ=qux')
    assert len(result.entries) == 3
    assert result.entries[1].is_blank


def test_comment_lines():
    result = parse_env_file('# This is a comment\nFOO=bar')
    assert result.entries[0].is_comment
    assert result.entries[1].key == 'FOO'


def test_export_prefix():
    result = parse_env_file('export MY_VAR=hello')
    entry = result.entries[0]
    assert entry.key == 'MY_VAR'
    assert entry.value == 'hello'
    assert entry.has_export


def test_inline_comment_stripped():
    result = parse_env_file('FOO=bar # inline comment')
    assert result.entries[0].value == 'bar'


def test_empty_value():
    result = parse_env_file('EMPTY=')
    assert result.entries[0].key == 'EMPTY'
    assert result.entries[0].value == ''


def test_invalid_line_produces_error():
    result = parse_env_file('not valid at all!!!')
    assert len(result.errors) == 1
    assert 'Line 1' in result.errors[0]


def test_multiple_entries():
    content = 'A=1\nB=2\nC=3'
    result = parse_env_file(content)
    keys = [e.key for e in result.entries if e.key]
    assert keys == ['A', 'B', 'C']
