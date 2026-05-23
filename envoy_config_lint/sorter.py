"""Sorting and ordering utilities for env file entries."""

from dataclasses import dataclass, field
from typing import List, Optional
from envoy_config_lint.parser import EnvEntry


@dataclass
class SortResult:
    original: List[EnvEntry]
    sorted_entries: List[EnvEntry]
    is_sorted: bool
    out_of_order: List[str] = field(default_factory=list)


def is_sorted_count(result: SortResult) -> int:
    """Return number of keys that are out of order."""
    return len(result.out_of_order)


def total_count(result: SortResult) -> int:
    """Return total number of entries."""
    return len(result.original)


def _key_name(entry: EnvEntry) -> str:
    return entry.key.upper()


def sort_entries(
    entries: List[EnvEntry],
    case_sensitive: bool = False,
    group_by_prefix: bool = False,
    separator: str = "_",
) -> SortResult:
    """Sort env entries alphabetically and detect ordering issues.

    Args:
        entries: List of parsed env entries.
        case_sensitive: If True, sort is case-sensitive.
        group_by_prefix: If True, entries are grouped by prefix before sorting.
        separator: Separator character used to identify prefixes.

    Returns:
        SortResult with sorted entries and ordering metadata.
    """
    key_fn = (lambda e: e.key) if case_sensitive else (lambda e: e.key.upper())

    if group_by_prefix:
        groups: dict = {}
        no_prefix: List[EnvEntry] = []
        for entry in entries:
            if separator in entry.key:
                prefix = entry.key.split(separator, 1)[0]
                prefix_key = prefix if case_sensitive else prefix.upper()
                groups.setdefault(prefix_key, []).append(entry)
            else:
                no_prefix.append(entry)

        sorted_entries: List[EnvEntry] = []
        for prefix_key in sorted(groups.keys()):
            sorted_entries.extend(sorted(groups[prefix_key], key=key_fn))
        sorted_entries.extend(sorted(no_prefix, key=key_fn))
    else:
        sorted_entries = sorted(entries, key=key_fn)

    # Detect which keys are out of order compared to sorted result
    out_of_order: List[str] = []
    for original_entry, sorted_entry in zip(entries, sorted_entries):
        if original_entry.key != sorted_entry.key:
            if original_entry.key not in out_of_order:
                out_of_order.append(original_entry.key)

    is_sorted = len(out_of_order) == 0

    return SortResult(
        original=entries,
        sorted_entries=sorted_entries,
        is_sorted=is_sorted,
        out_of_order=out_of_order,
    )
