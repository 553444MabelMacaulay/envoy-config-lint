"""Formatters for ProfileResult output."""
import json
from envoy_config_lint.profiler import ProfileResult
from envoy_config_lint.formatter import OutputFormat


def format_profile(result: ProfileResult, fmt: OutputFormat = OutputFormat.TEXT) -> str:
    if fmt == OutputFormat.JSON:
        return _format_profile_json(result)
    if fmt == OutputFormat.GITHUB:
        return _format_profile_github(result)
    return _format_profile_text(result)


def _format_profile_text(result: ProfileResult) -> str:
    lines = [
        "=== Env File Profile ===",
        f"Total keys          : {result.total_keys}",
        f"Empty values        : {result.empty_value_count}",
        f"Quoted values       : {result.quoted_value_count}",
        f"Long values (>64)   : {result.long_value_count}",
        f"Avg value length    : {result.avg_value_length}",
        f"Prefixes found      : {', '.join(result.prefixes_found) if result.prefixes_found else 'none'}",
        "Key length distribution:",
        f"  short  (<= 8)  : {result.key_length_distribution.get('short', 0)}",
        f"  medium (<= 20) : {result.key_length_distribution.get('medium', 0)}",
        f"  long   (> 20)  : {result.key_length_distribution.get('long', 0)}",
    ]
    return "\n".join(lines)


def _format_profile_json(result: ProfileResult) -> str:
    data = {
        "total_keys": result.total_keys,
        "empty_value_count": result.empty_value_count,
        "quoted_value_count": result.quoted_value_count,
        "long_value_count": result.long_value_count,
        "avg_value_length": result.avg_value_length,
        "prefixes_found": result.prefixes_found,
        "key_length_distribution": result.key_length_distribution,
    }
    return json.dumps(data, indent=2)


def _format_profile_github(result: ProfileResult) -> str:
    lines = [
        f"::notice ::Env profile — {result.total_keys} keys, "
        f"{result.empty_value_count} empty, "
        f"{result.long_value_count} long values, "
        f"avg length {result.avg_value_length}"
    ]
    if result.prefixes_found:
        lines.append(f"::notice ::Prefixes detected: {', '.join(result.prefixes_found)}")
    return "\n".join(lines)
