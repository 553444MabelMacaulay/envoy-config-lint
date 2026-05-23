"""Profile env files by detecting patterns like key density, value lengths, and structure."""
from dataclasses import dataclass, field
from typing import List, Dict
from envoy_config_lint.parser import EnvEntry


@dataclass
class ProfileResult:
    total_keys: int = 0
    empty_value_count: int = 0
    quoted_value_count: int = 0
    long_value_count: int = 0  # values > 64 chars
    prefixes_found: List[str] = field(default_factory=list)
    avg_value_length: float = 0.0
    key_length_distribution: Dict[str, int] = field(default_factory=dict)  # short/medium/long


def _classify_key_length(key: str) -> str:
    length = len(key)
    if length <= 8:
        return "short"
    elif length <= 20:
        return "medium"
    return "long"


def _extract_prefix(key: str, separator: str = "_") -> str | None:
    parts = key.split(separator, 1)
    return parts[0] if len(parts) > 1 else None


def profile_entries(entries: List[EnvEntry]) -> ProfileResult:
    """Analyse a list of EnvEntry objects and return a ProfileResult."""
    if not entries:
        return ProfileResult()

    result = ProfileResult(total_keys=len(entries))
    total_value_length = 0
    prefixes: set = set()
    key_dist: Dict[str, int] = {"short": 0, "medium": 0, "long": 0}

    for entry in entries:
        value = entry.value or ""

        if value == "":
            result.empty_value_count += 1

        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            result.quoted_value_count += 1

        if len(value) > 64:
            result.long_value_count += 1

        total_value_length += len(value)

        prefix = _extract_prefix(entry.key)
        if prefix:
            prefixes.add(prefix)

        bucket = _classify_key_length(entry.key)
        key_dist[bucket] = key_dist.get(bucket, 0) + 1

    result.avg_value_length = round(total_value_length / len(entries), 2)
    result.prefixes_found = sorted(prefixes)
    result.key_length_distribution = key_dist
    return result
