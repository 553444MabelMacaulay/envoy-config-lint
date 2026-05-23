"""Parser module for reading and tokenizing .env files."""

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EnvEntry:
    """Represents a single entry in a .env file."""

    line_number: int
    key: Optional[str]
    value: Optional[str]
    raw_line: str
    is_comment: bool = False
    is_blank: bool = False
    has_export: bool = False


@dataclass
class ParseResult:
    """Result of parsing a .env file."""

    entries: List[EnvEntry] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


KEY_PATTERN = re.compile(r'^(?P<export>export\s+)?(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$')


def _strip_inline_comment(value: str) -> str:
    """Strip an inline comment from an unquoted value.

    Only strips comments from values that are not wrapped in quotes,
    since a '#' inside a quoted string is not a comment delimiter.
    """
    if '#' in value and not value.startswith(('"', "'")):
        value = value.split('#', 1)[0].strip()
    return value


def parse_env_file(content: str) -> ParseResult:
    """Parse the content of a .env file into structured entries."""
    result = ParseResult()

    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        stripped = raw_line.strip()

        if not stripped:
            result.entries.append(EnvEntry(
                line_number=line_number,
                key=None,
                value=None,
                raw_line=raw_line,
                is_blank=True,
            ))
            continue

        if stripped.startswith('#'):
            result.entries.append(EnvEntry(
                line_number=line_number,
                key=None,
                value=None,
                raw_line=raw_line,
                is_comment=True,
            ))
            continue

        match = KEY_PATTERN.match(stripped)
        if match:
            key = match.group('key')
            value = _strip_inline_comment(match.group('value').strip())
            has_export = bool(match.group('export'))
            result.entries.append(EnvEntry(
                line_number=line_number,
                key=key,
                value=value,
                raw_line=raw_line,
                has_export=has_export,
            ))
        else:
            result.errors.append(f"Line {line_number}: Unable to parse line: {raw_line!r}")

    return result
