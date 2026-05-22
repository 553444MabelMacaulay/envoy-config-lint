"""Formatting helpers for DiffResult output."""
import json
from typing import Callable, Dict

from envoy_config_lint.differ import DiffResult
from envoy_config_lint.formatter import OutputFormat


def format_diff(result: DiffResult, fmt: OutputFormat = OutputFormat.TEXT) -> str:
    """Format a DiffResult according to the requested output format."""
    formatters: Dict[OutputFormat, Callable[[DiffResult], str]] = {
        OutputFormat.TEXT: _format_diff_text,
        OutputFormat.JSON: _format_diff_json,
        OutputFormat.GITHUB: _format_diff_github,
    }
    formatter = formatters.get(fmt, _format_diff_text)
    return formatter(result)


def _format_diff_text(result: DiffResult) -> str:
    lines = [f"Diff: {result.base_file} vs {result.compare_file}"]
    if not result.has_differences:
        lines.append("  No differences found.")
        return "\n".join(lines)
    if result.missing_in_compare:
        lines.append(f"  Missing in {result.compare_file} ({result.missing_count}):")
        for key in result.missing_in_compare:
            lines.append(f"    - {key}")
    if result.extra_in_compare:
        lines.append(f"  Extra in {result.compare_file} ({result.extra_count}):")
        for key in result.extra_in_compare:
            lines.append(f"    + {key}")
    lines.append(
        f"  Summary: {result.missing_count} missing, "
        f"{result.extra_count} extra, {len(result.common_keys)} common"
    )
    return "\n".join(lines)


def _format_diff_json(result: DiffResult) -> str:
    data = {
        "base_file": result.base_file,
        "compare_file": result.compare_file,
        "missing_in_compare": result.missing_in_compare,
        "extra_in_compare": result.extra_in_compare,
        "common_keys": result.common_keys,
        "has_differences": result.has_differences,
    }
    return json.dumps(data, indent=2)


def _format_diff_github(result: DiffResult) -> str:
    lines = []
    for key in result.missing_in_compare:
        lines.append(
            f"::warning title=Missing key::'{key}' is in {result.base_file} "
            f"but missing from {result.compare_file}"
        )
    for key in result.extra_in_compare:
        lines.append(
            f"::notice title=Extra key::'{key}' is in {result.compare_file} "
            f"but not in {result.base_file}"
        )
    if not lines:
        lines.append(f"::notice::No differences between {result.base_file} and {result.compare_file}")
    return "\n".join(lines)
