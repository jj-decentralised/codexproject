"""Async GraphQL client for Codex.io API with caching and budget tracking."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

import httpx
import pyarrow as pa
import pyarrow.parquet as pq
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.api.budget_tracker import BudgetTracker, BudgetExhaustedError
from src.api.rate_limiter import TokenBucketRateLimiter

logger = logging.getLogger(__name__)


class CodexGraphQLClient:
    """Async GraphQL client for Codex.io with caching, budget tracking, and retries."""

    ENDPOINT = "https://graph.codex.io/graphql"

    def __init__(
        self,
        api_key: str,
        budget_limit: int = 100_000,
        cache_dir: str = "data/raw/cache",
        db_path: str = "data/raw/budget.db",
    ):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": api_key,
        }
        self.budget = BudgetTracker(limit=budget_limit, db_path=db_path)
        self.rate_limiter = TokenBucketRateLimiter()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers=self.headers,
                timeout=httpx.Timeout(30.0, connect=10.0),
                limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _cache_key(self, query: str, variables: dict) -> str:
        content = json.dumps({"q": query.strip(), "v": variables}, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def _get_cached(self, key: str) -> dict | None:
        path = self._cache_path(key)
        if path.exists():
            return json.loads(path.read_text())
        return None

    def _set_cached(self, key: str, data: dict) -> None:
        path = self._cache_path(key)
        path.write_text(json.dumps(data))

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=2, min=2, max=16),
        retry=retry_if_exception_type((httpx.TransportError, httpx.TimeoutException)),
        reraise=True,
    )
    async def _post(self, payload: dict) -> dict:
        client = await self._get_client()
        response = await client.post(self.ENDPOINT, json=payload)
        response.raise_for_status()
        result = response.json()
        if "errors" in result:
            error_msg = "; ".join(e.get("message", str(e)) for e in result["errors"])
            raise RuntimeError(f"GraphQL errors: {error_msg}")
        return result.get("data", {})

    async def execute(
        self,
        query: str,
        variables: dict,
        module: str = "default",
        query_type: str = "unknown",
    ) -> dict:
        """Execute a GraphQL query with caching, budget tracking, and rate limiting.

        Args:
            query: GraphQL query string.
            variables: Query variables dict.
            module: Module name for budget tracking (e.g., 'census', 'ohlcv').
            query_type: Query type for budget tracking (e.g., 'filterTokens', 'getBars').

        Returns:
            Query result data dict.
        """
        cache_key = self._cache_key(query, variables)

        cached = self._get_cached(cache_key)
        if cached is not None:
            self.budget.record_call(module, query_type, cache_key, cached=True)
            logger.debug("Cache hit: %s/%s", module, query_type)
            return cached

        self.budget.record_call(module, query_type, cache_key, cached=False)
        await self.rate_limiter.acquire()

        data = await self._post({"query": query, "variables": variables})

        self._set_cached(cache_key, data)
        logger.info(
            "API call: %s/%s (total: %d, remaining: %d)",
            module,
            query_type,
            self.budget.total_calls,
            self.budget.remaining,
        )
        return data

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
