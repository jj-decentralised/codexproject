"""Study period definition and time window generation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.utils.timestamps import to_unix

# Study period: 6 months ending today (Feb 19, 2026)
STUDY_END = datetime(2026, 2, 19, tzinfo=timezone.utc)
STUDY_START = datetime(2025, 8, 19, tzinfo=timezone.utc)
STUDY_DAYS = (STUDY_END - STUDY_START).days  # 184 days

STUDY_START_UNIX = to_unix(STUDY_START)
STUDY_END_UNIX = to_unix(STUDY_END)


def daily_windows() -> list[tuple[int, int]]:
    """Generate (start_unix, end_unix) for each day in the study period."""
    windows = []
    current = STUDY_START
    while current < STUDY_END:
        day_start = to_unix(current)
        day_end = to_unix(current + timedelta(days=1))
        windows.append((day_start, day_end))
        current += timedelta(days=1)
    return windows


def weekly_windows() -> list[tuple[int, int]]:
    """Generate (start_unix, end_unix) for each week in the study period."""
    windows = []
    current = STUDY_START
    while current < STUDY_END:
        week_start = to_unix(current)
        week_end = to_unix(min(current + timedelta(weeks=1), STUDY_END))
        windows.append((week_start, week_end))
        current += timedelta(weeks=1)
    return windows


def monthly_windows() -> list[tuple[int, int]]:
    """Generate (start_unix, end_unix) for each month in the study period."""
    windows = []
    current = STUDY_START
    while current < STUDY_END:
        month_start = to_unix(current)
        # Advance to next month
        if current.month == 12:
            next_month = current.replace(year=current.year + 1, month=1)
        else:
            next_month = current.replace(month=current.month + 1)
        next_month = min(next_month, STUDY_END)
        month_end = to_unix(next_month)
        windows.append((month_start, month_end))
        current = next_month
    return windows
