"""Tests for envoy_config_lint.formatter_profile."""
import json
import pytest
from envoy_config_lint.profiler import ProfileResult
from envoy_config_lint.formatter import OutputFormat
from envoy_config_lint.formatter_profile import format_profile


def _make_result(**kwargs) -> ProfileResult:
    defaults = dict(
        total_keys=5,
        empty_value_count=1,
        quoted_value_count=2,
        long_value_count=0,
        prefixes_found=["APP", "DB"],
        avg_value_length=12.4,
        key_length_distribution={"short": 1, "medium": 3, "long": 1},
    )
    defaults.update(kwargs)
    return ProfileResult(**defaults)


# --- TEXT ---

def test_text_contains_total_keys():
    out = format_profile(_make_result(), OutputFormat.TEXT)
    assert "Total keys" in out
    assert "5" in out


def test_text_contains_prefixes():
    out = format_profile(_make_result(), OutputFormat.TEXT)
    assert "APP" in out
    assert "DB" in out


def test_text_no_prefixes_shows_none():
    out = format_profile(_make_result(prefixes_found=[]), OutputFormat.TEXT)
    assert "none" in out


def test_text_contains_distribution():
    out = format_profile(_make_result(), OutputFormat.TEXT)
    assert "short" in out
    assert "medium" in out
    assert "long" in out


# --- JSON ---

def test_json_is_valid():
    out = format_profile(_make_result(), OutputFormat.JSON)
    data = json.loads(out)
    assert data["total_keys"] == 5


def test_json_contains_prefixes():
    out = format_profile(_make_result(), OutputFormat.JSON)
    data = json.loads(out)
    assert "APP" in data["prefixes_found"]


def test_json_contains_distribution():
    out = format_profile(_make_result(), OutputFormat.JSON)
    data = json.loads(out)
    assert "short" in data["key_length_distribution"]


# --- GITHUB ---

def test_github_contains_notice():
    out = format_profile(_make_result(), OutputFormat.GITHUB)
    assert "::notice ::" in out


def test_github_shows_key_count():
    out = format_profile(_make_result(), OutputFormat.GITHUB)
    assert "5 keys" in out


def test_github_shows_prefixes_line():
    out = format_profile(_make_result(), OutputFormat.GITHUB)
    assert "Prefixes detected" in out


def test_github_no_prefixes_line_when_empty():
    out = format_profile(_make_result(prefixes_found=[]), OutputFormat.GITHUB)
    assert "Prefixes detected" not in out
