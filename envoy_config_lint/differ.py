"""Diff two .env files and report missing or extra keys."""
from dataclasses import dataclass, field
from typing import List, Set

from envoy_config_lint.parser import ParseResult


@dataclass
class DiffResult:
    """Result of comparing two parsed env files."""
    base_file: str
    compare_file: str
    missing_in_compare: List[str] = field(default_factory=list)
    extra_in_compare: List[str] = field(default_factory=list)
    common_keys: List[str] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(self.missing_in_compare or self.extra_in_compare)

    @property
    def missing_count(self) -> int:
        return len(self.missing_in_compare)

    @property
    def extra_count(self) -> int:
        return len(self.extra_in_compare)


def diff_env_files(base: ParseResult, compare: ParseResult,
                   base_name: str = "base",
                   compare_name: str = "compare") -> DiffResult:
    """Compare two ParseResult objects and return a DiffResult.

    Args:
        base: The reference ParseResult (e.g. .env.example).
        compare: The ParseResult to compare against the base.
        base_name: Label for the base file.
        compare_name: Label for the compare file.

    Returns:
        A DiffResult describing the differences.
    """
    base_keys: Set[str] = {entry.key for entry in base.entries}
    compare_keys: Set[str] = {entry.key for entry in compare.entries}

    missing = sorted(base_keys - compare_keys)
    extra = sorted(compare_keys - base_keys)
    common = sorted(base_keys & compare_keys)

    return DiffResult(
        base_file=base_name,
        compare_file=compare_name,
        missing_in_compare=missing,
        extra_in_compare=extra,
        common_keys=common,
    )
