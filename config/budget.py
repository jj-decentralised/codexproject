"""API call budget allocation per module."""

from __future__ import annotations

TOTAL_BUDGET = 100_000
HARD_STOP = 95_000  # 95% of total

# Per-module allocations
BUDGET_ALLOCATION = {
    "census": 15_000,
    "ohlcv": 25_000,
    "events": 15_000,
    "wallet_pnl": 5_000,
    "pair_stats": 10_000,
    "metadata": 2_000,
    "reserve": 28_000,
}

assert sum(BUDGET_ALLOCATION.values()) == TOTAL_BUDGET
