"""Variable interpolation checker for .env files.

Detects references like ${VAR} or $VAR within values and verifies
that the referenced variable is defined within the same file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Set

from .parser import EnvEntry

# Matches ${VAR_NAME} and $VAR_NAME (bare) forms
_REF_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolationIssue:
    key: str          # key whose value contains the bad reference
    ref: str          # the variable name that is unresolved
    line: int

    def __str__(self) -> str:
        return f"Line {self.line}: '{self.key}' references undefined variable '${self.ref}'"


@dataclass
class InterpolationResult:
    issues: List[InterpolationIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def issue_count(self) -> int:
        return len(self.issues)


def _extract_refs(value: str) -> Set[str]:
    """Return all variable names referenced inside *value*."""
    refs: Set[str] = set()
    for m in _REF_PATTERN.finditer(value):
        name = m.group(1) or m.group(2)
        if name:
            refs.add(name)
    return refs


def check_interpolation(entries: List[EnvEntry]) -> InterpolationResult:
    """Check that every variable reference in a value resolves to a known key."""
    defined: Set[str] = {e.key for e in entries}
    result = InterpolationResult()

    for entry in entries:
        if not entry.value:
            continue
        for ref in sorted(_extract_refs(entry.value)):
            if ref not in defined:
                result.issues.append(
                    InterpolationIssue(key=entry.key, ref=ref, line=entry.line)
                )

    return result
