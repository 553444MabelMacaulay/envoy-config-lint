"""Renamer module: suggests or applies key rename operations across env entries."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envoy_config_lint.parser import EnvEntry


@dataclass
class RenameIssue:
    old_key: str
    new_key: str
    line_number: int
    reason: str

    def __str__(self) -> str:
        return (
            f"Line {self.line_number}: rename '{self.old_key}' -> '{self.new_key}' "
            f"({self.reason})"
        )


@dataclass
class RenameResult:
    issues: List[RenameIssue] = field(default_factory=list)
    renamed: Dict[str, str] = field(default_factory=dict)  # old_key -> new_key

    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def issue_count(self) -> int:
        return len(self.issues)


def _suggest_canonical(key: str) -> Optional[str]:
    """Return a canonical (uppercase, no leading/trailing underscores) form if different."""
    canonical = key.upper().strip("_")
    if canonical != key:
        return canonical
    return None


def suggest_renames(
    entries: List[EnvEntry],
    rename_map: Optional[Dict[str, str]] = None,
) -> RenameResult:
    """Suggest renames based on a provided rename_map and canonical form checks.

    Args:
        entries: Parsed env entries.
        rename_map: Explicit mapping of old_key -> new_key (e.g. deprecated renames).

    Returns:
        RenameResult with all suggested rename issues.
    """
    result = RenameResult()
    explicit = rename_map or {}

    for entry in entries:
        key = entry.key

        # Explicit rename map takes priority
        if key in explicit:
            new_key = explicit[key]
            issue = RenameIssue(
                old_key=key,
                new_key=new_key,
                line_number=entry.line_number,
                reason="explicit rename map",
            )
            result.issues.append(issue)
            result.renamed[key] = new_key
            continue

        # Suggest canonical form
        canonical = _suggest_canonical(key)
        if canonical is not None:
            issue = RenameIssue(
                old_key=key,
                new_key=canonical,
                line_number=entry.line_number,
                reason="non-canonical key form",
            )
            result.issues.append(issue)
            result.renamed[key] = canonical

    return result
