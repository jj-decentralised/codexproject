"""Tests for the Codex.io API client."""

from __future__ import annotations

import json
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.api.budget_tracker import BudgetTracker, BudgetExhaustedError
from src.api.rate_limiter import TokenBucketRateLimiter

TEST_DB_PATH = "/tmp/test_budget.db"


class TestBudgetTracker:
    def setup_method(self):
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        self.tracker = BudgetTracker(limit=100, db_path=TEST_DB_PATH)

    def teardown_method(self):
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    def test_record_call(self):
        count = self.tracker.record_call("test", "filterTokens", "hash1")
        assert count == 1

    def test_budget_limit(self):
        # Fill up to hard stop (95% of 100 = 95)
        for i in range(94):
            self.tracker.record_call("test", "query", f"hash_{i}")

        with pytest.raises(BudgetExhaustedError):
            self.tracker.record_call("test", "query", "hash_final")

    def test_cached_calls_not_counted(self):
        self.tracker.record_call("test", "query", "h1", cached=True)
        self.tracker.record_call("test", "query", "h2", cached=False)
        assert self.tracker.total_calls == 1  # Only non-cached

    def test_summary_by_module(self):
        self.tracker.record_call("census", "filterTokens", "h1")
        self.tracker.record_call("census", "filterTokens", "h2")
        self.tracker.record_call("ohlcv", "getBars", "h3")

        summary = self.tracker.summary_by_module()
        assert summary["census"] == 2
        assert summary["ohlcv"] == 1

    def test_remaining(self):
        self.tracker.record_call("test", "query", "h1")
        assert self.tracker.remaining == 94  # 95 - 1


class TestTokenBucketRateLimiter:
    @pytest.mark.asyncio
    async def test_acquire(self):
        limiter = TokenBucketRateLimiter(rate=100, burst=10)
        # Should not block for first burst
        for _ in range(10):
            await limiter.acquire()
