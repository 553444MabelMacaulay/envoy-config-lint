"""Compare two parsed env files and report value-level differences."""
from dataclasses import dataclass, field
from typing import List, Optional
from envoy_config_lint.parser import ParseResult


@dataclass
class ValueDiff:
    key: str
    value_a: Optional[str]
    value_b: Optional[str]
    kind: str  # 'changed' | 'missing_in_b' | 'missing_in_a'

    def __str__(self) -> str:
        if self.kind == "changed":
            return f"{self.key}: {self.value_a!r} -> {self.value_b!r}"
        if self.kind == "missing_in_b":
            return f"{self.key}: present in A, missing in B"
        return f"{self.key}: missing in A, present in B"


@dataclass
class CompareResult:
    diffs: List[ValueDiff] = field(default_factory=list)

    def has_diffs(self) -> bool:
        return bool(self.diffs)

    def changed_count(self) -> int:
        return sum(1 for d in self.diffs if d.kind == "changed")

    def missing_in_b_count(self) -> int:
        return sum(1 for d in self.diffs if d.kind == "missing_in_b")

    def missing_in_a_count(self) -> int:
        return sum(1 for d in self.diffs if d.kind == "missing_in_a")


def compare_env_files(result_a: ParseResult, result_b: ParseResult) -> CompareResult:
    """Perform a value-level comparison between two parsed env files."""
    map_a = {e.key: e.value for e in result_a.entries}
    map_b = {e.key: e.value for e in result_b.entries}
    all_keys = sorted(set(map_a) | set(map_b))
    diffs: List[ValueDiff] = []

    for key in all_keys:
        in_a = key in map_a
        in_b = key in map_b
        if in_a and in_b:
            if map_a[key] != map_b[key]:
                diffs.append(ValueDiff(key, map_a[key], map_b[key], "changed"))
        elif in_a:
            diffs.append(ValueDiff(key, map_a[key], None, "missing_in_b"))
        else:
            diffs.append(ValueDiff(key, None, map_b[key], "missing_in_a"))

    return CompareResult(diffs=diffs)
