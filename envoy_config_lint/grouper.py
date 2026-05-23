"""Group env entries by prefix for structural analysis."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .parser import EnvEntry


@dataclass
class GroupResult:
    groups: Dict[str, List[EnvEntry]] = field(default_factory=dict)
    ungrouped: List[EnvEntry] = field(default_factory=list)

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def group_count(self) -> int:
        return len(self.groups)

    def entry_count_for(self, prefix: str) -> int:
        return len(self.groups.get(prefix, []))


def _extract_prefix(key: str, separator: str = "_") -> Optional[str]:
    """Return the first segment of a key split by separator, or None if no separator."""
    if separator in key:
        return key.split(separator, 1)[0]
    return None


def group_by_prefix(
    entries: List[EnvEntry],
    separator: str = "_",
    min_group_size: int = 2,
) -> GroupResult:
    """Group entries by their key prefix.

    Only prefixes shared by at least `min_group_size` entries are treated as
    real groups; remaining entries go into `ungrouped`.
    """
    buckets: Dict[str, List[EnvEntry]] = {}
    for entry in entries:
        prefix = _extract_prefix(entry.key, separator)
        if prefix is not None:
            buckets.setdefault(prefix, []).append(entry)
        # entries without a separator are always ungrouped

    result = GroupResult()
    for entry in entries:
        prefix = _extract_prefix(entry.key, separator)
        if prefix and len(buckets.get(prefix, [])) >= min_group_size:
            result.groups.setdefault(prefix, []).append(entry)
        else:
            result.ungrouped.append(entry)

    return result
