"""Scope analysis: detect keys that appear to belong to multiple environments
(e.g. DEV_*, PROD_*, STAGING_*) mixed together in a single env file."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional

from envoy_config_lint.parser import EnvEntry

_KNOWN_ENV_TOKENS = frozenset(
    ["DEV", "DEVELOPMENT", "PROD", "PRODUCTION", "STAGING", "TEST", "QA", "LOCAL", "CI"]
)


@dataclass(frozen=True)
class ScopeIssue:
    key: str
    detected_scope: str
    message: str

    def __str__(self) -> str:  # pragma: no cover
        return f"[scope] {self.key}: {self.message}"


@dataclass
class ScopeResult:
    issues: List[ScopeIssue] = field(default_factory=list)
    scopes_found: FrozenSet[str] = field(default_factory=frozenset)
    keys_by_scope: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def issue_count(self) -> int:
        return len(self.issues)


def _extract_scope_token(key: str) -> Optional[str]:
    """Return the leading environment scope token if present, else None."""
    parts = key.upper().split("_", 1)
    if len(parts) >= 1 and parts[0] in _KNOWN_ENV_TOKENS:
        return parts[0]
    return None


def scope_entries(entries: List[EnvEntry]) -> ScopeResult:
    """Analyse entries for mixed environment scopes."""
    keys_by_scope: Dict[str, List[str]] = {}

    for entry in entries:
        token = _extract_scope_token(entry.key)
        if token:
            keys_by_scope.setdefault(token, []).append(entry.key)

    scopes_found = frozenset(keys_by_scope.keys())
    issues: List[ScopeIssue] = []

    if len(scopes_found) > 1:
        for scope, keys in sorted(keys_by_scope.items()):
            for key in keys:
                issues.append(
                    ScopeIssue(
                        key=key,
                        detected_scope=scope,
                        message=(
                            f"Key belongs to scope '{scope}' but file contains "
                            f"multiple scopes: {sorted(scopes_found)}"
                        ),
                    )
                )

    return ScopeResult(
        issues=issues,
        scopes_found=scopes_found,
        keys_by_scope=keys_by_scope,
    )
