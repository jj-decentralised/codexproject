"""API call budget tracker with SQLite logging."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path


class BudgetExhaustedError(Exception):
    """Raised when the API call budget has been exhausted."""


class BudgetTracker:
    """Tracks cumulative API calls with SQLite persistence.

    Hard-stops at 95% of budget to reserve capacity for debugging.
    """

    def __init__(self, limit: int = 100_000, db_path: str = "data/raw/budget.db"):
        self.limit = limit
        self.hard_stop = int(limit * 0.95)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS api_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    module TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    variables_hash TEXT,
                    cached BOOLEAN DEFAULT FALSE
                )"""
            )
            conn.execute(
                """CREATE INDEX IF NOT EXISTS idx_module
                   ON api_calls(module)"""
            )

    def record_call(self, module: str, query_type: str, variables_hash: str = "", cached: bool = False) -> int:
        """Record an API call. Returns total count. Raises BudgetExhaustedError if over limit."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO api_calls (timestamp, module, query_type, variables_hash, cached) VALUES (?, ?, ?, ?, ?)",
                (time.time(), module, query_type, variables_hash, cached),
            )
            (count,) = conn.execute(
                "SELECT COUNT(*) FROM api_calls WHERE cached = FALSE"
            ).fetchone()

        if count >= self.hard_stop:
            raise BudgetExhaustedError(
                f"Budget exhausted: {count}/{self.limit} calls used "
                f"(hard stop at {self.hard_stop})"
            )
        return count

    @property
    def total_calls(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            (count,) = conn.execute(
                "SELECT COUNT(*) FROM api_calls WHERE cached = FALSE"
            ).fetchone()
        return count

    @property
    def remaining(self) -> int:
        return max(0, self.hard_stop - self.total_calls)

    def summary_by_module(self) -> dict[str, int]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT module, COUNT(*) FROM api_calls WHERE cached = FALSE GROUP BY module"
            ).fetchall()
        return dict(rows)

    def summary_by_query_type(self) -> dict[str, int]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT query_type, COUNT(*) FROM api_calls WHERE cached = FALSE GROUP BY query_type"
            ).fetchall()
        return dict(rows)
