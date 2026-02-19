"""Swap event data collector using getTokenEvents with pagination."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.api.client import CodexGraphQLClient
from src.api.queries import GET_TOKEN_EVENTS

logger = logging.getLogger(__name__)

MODULE = "events"


class EventCollector:
    """Collect swap-level event data for tokens."""

    def __init__(self, client: CodexGraphQLClient, output_dir: str = "data/raw/events"):
        self.client = client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def collect_token_events(
        self,
        token_address: str,
        network_id: int,
        max_pages: int = 20,
    ) -> pd.DataFrame:
        """Fetch paginated swap events for a token.

        Args:
            token_address: Token contract address.
            network_id: Codex network ID.
            max_pages: Maximum pages to fetch.

        Returns:
            DataFrame of swap events.
        """
        all_events = []
        cursor = None

        for page in range(max_pages):
            variables = {
                "query": {
                    "address": token_address,
                    "networkId": network_id,
                },
            }
            if cursor:
                variables["cursor"] = cursor

            data = await self.client.execute(
                GET_TOKEN_EVENTS,
                variables,
                module=MODULE,
                query_type="getTokenEvents",
            )

            result = data.get("getTokenEvents", {})
            items = result.get("items", [])
            cursor = result.get("cursor")

            for item in items:
                event_data = item.get("data", {})
                all_events.append({
                    "timestamp": item.get("timestamp"),
                    "event_type": item.get("eventType"),
                    "price_usd": item.get("priceUsd"),
                    "price_usd_total": item.get("priceUsdTotal"),
                    "maker": item.get("maker"),
                    "block_number": item.get("blockNumber"),
                    "tx_hash": item.get("transactionHash"),
                    "token0_swap_value_usd": item.get("token0SwapValueUsd"),
                    "token1_swap_value_usd": item.get("token1SwapValueUsd"),
                    "trade_type": event_data.get("type"),
                    "buy_amount": event_data.get("buyAmount"),
                    "sell_amount": event_data.get("sellAmount"),
                })

            if not cursor or not items:
                break

        df = pd.DataFrame(all_events)
        if not df.empty:
            path = self.output_dir / f"{token_address}_{network_id}_events.parquet"
            df.to_parquet(path, index=False)
            logger.info("Events saved: %s (%d events)", path, len(df))
        return df

    async def collect_batch(self, tokens: list[dict], max_pages: int = 15) -> dict[str, pd.DataFrame]:
        """Collect events for a batch of tokens."""
        results = {}
        for i, token in enumerate(tokens):
            logger.info("Events %d/%d: %s", i + 1, len(tokens), token.get("address", "?"))
            df = await self.collect_token_events(
                token_address=token["address"],
                network_id=token["network_id"],
                max_pages=max_pages,
            )
            results[token["address"]] = df
        return results
