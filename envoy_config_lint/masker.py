"""Mask sensitive values in env entries for safe display or logging."""

from dataclasses import dataclass, field
from typing import List

from envoy_config_lint.parser import EnvEntry
from envoy_config_lint.redactor import _is_sensitive

_MASK = "********"
_PARTIAL_VISIBLE = 4  # characters to reveal at start for partial masking


@dataclass
class MaskedEntry:
    key: str
    original_value: str
    masked_value: str
    was_masked: bool


@dataclass
class MaskResult:
    entries: List[MaskedEntry] = field(default_factory=list)

    def masked_count(self) -> int:
        return sum(1 for e in self.entries if e.was_masked)

    def total_count(self) -> int:
        return len(self.entries)


def _mask_value(value: str, partial: bool = False) -> str:
    """Return a masked version of the value.

    If *partial* is True and the value is long enough, reveal the first
    ``_PARTIAL_VISIBLE`` characters followed by asterisks so that reviewers
    can identify the value family without exposing the full secret.
    """
    if not value:
        return value
    if partial and len(value) > _PARTIAL_VISIBLE:
        return value[:_PARTIAL_VISIBLE] + _MASK
    return _MASK


def mask_entries(
    entries: List[EnvEntry],
    partial: bool = False,
) -> MaskResult:
    """Mask sensitive values in *entries*.

    Parameters
    ----------
    entries:
        Parsed env entries to process.
    partial:
        When *True*, reveal the first few characters of sensitive values
        instead of replacing the entire value with asterisks.

    Returns
    -------
    MaskResult
        A result object containing :class:`MaskedEntry` items for every
        input entry.
    """
    masked: List[MaskedEntry] = []
    for entry in entries:
        sensitive = _is_sensitive(entry.key)
        masked_val = _mask_value(entry.value, partial=partial) if sensitive else entry.value
        masked.append(
            MaskedEntry(
                key=entry.key,
                original_value=entry.value,
                masked_value=masked_val,
                was_masked=sensitive,
            )
        )
    return MaskResult(entries=masked)
