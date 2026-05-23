"""Format a CompareResult for text, JSON, and GitHub Actions output."""
import json
from envoy_config_lint.comparator import CompareResult
from envoy_config_lint.formatter import OutputFormat


def format_compare(result: CompareResult, fmt: OutputFormat = OutputFormat.TEXT) -> str:
    if fmt == OutputFormat.JSON:
        return _format_compare_json(result)
    if fmt == OutputFormat.GITHUB:
        return _format_compare_github(result)
    return _format_compare_text(result)


def _format_compare_text(result: CompareResult) -> str:
    lines = []
    if not result.has_diffs():
        lines.append("No value differences found.")
    else:
        for diff in result.diffs:
            if diff.kind == "changed":
                lines.append(f"  CHANGED   {diff.key}: {diff.value_a!r} -> {diff.value_b!r}")
            elif diff.kind == "missing_in_b":
                lines.append(f"  ONLY_IN_A {diff.key}")
            else:
                lines.append(f"  ONLY_IN_B {diff.key}")
    lines.append(
        f"Summary: {result.changed_count()} changed, "
        f"{result.missing_in_b_count()} only in A, "
        f"{result.missing_in_a_count()} only in B."
    )
    return "\n".join(lines)


def _format_compare_json(result: CompareResult) -> str:
    payload = {
        "has_diffs": result.has_diffs(),
        "changed": result.changed_count(),
        "missing_in_b": result.missing_in_b_count(),
        "missing_in_a": result.missing_in_a_count(),
        "diffs": [
            {"key": d.key, "kind": d.kind, "value_a": d.value_a, "value_b": d.value_b}
            for d in result.diffs
        ],
    }
    return json.dumps(payload, indent=2)


def _format_compare_github(result: CompareResult) -> str:
    lines = []
    for diff in result.diffs:
        if diff.kind == "changed":
            lines.append(f"::warning title=ValueChanged::{diff.key} value differs between files")
        elif diff.kind == "missing_in_b":
            lines.append(f"::warning title=MissingInB::{diff.key} is only present in file A")
        else:
            lines.append(f"::warning title=MissingInA::{diff.key} is only present in file B")
    if not lines:
        lines.append("::notice::No value differences found.")
    return "\n".join(lines)
