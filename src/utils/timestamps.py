"""Unix timestamp utilities."""

from __future__ import annotations

from datetime import datetime, timezone


def to_unix(dt: datetime) -> int:
    """Convert datetime to Unix timestamp (seconds)."""
    return int(dt.replace(tzinfo=timezone.utc).timestamp())


def from_unix(ts: int) -> datetime:
    """Convert Unix timestamp to UTC datetime."""
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def date_to_unix(year: int, month: int, day: int) -> int:
    """Convert date components to Unix timestamp."""
    return to_unix(datetime(year, month, day, tzinfo=timezone.utc))


def unix_day_range(year: int, month: int, day: int) -> tuple[int, int]:
    """Return (start, end) Unix timestamps for a single UTC day."""
    start = date_to_unix(year, month, day)
    end = start + 86400
    return start, end
