"""Async token bucket rate limiter."""

from __future__ import annotations

import asyncio
import time


class TokenBucketRateLimiter:
    """Token bucket rate limiter for controlling API request rate.

    Enterprise tier: 1000 requests/second.
    """

    def __init__(self, rate: float = 1000.0, burst: int = 1000):
        self.rate = rate
        self.burst = burst
        self._tokens = float(burst)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a token is available."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            self._tokens = min(self.burst, self._tokens + elapsed * self.rate)
            self._last_refill = now

            if self._tokens < 1.0:
                wait_time = (1.0 - self._tokens) / self.rate
                await asyncio.sleep(wait_time)
                self._tokens = 0.0
                self._last_refill = time.monotonic()
            else:
                self._tokens -= 1.0
