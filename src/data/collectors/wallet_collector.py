"""Wallet-level trade data collector using getTokenEventsForMaker."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.api.client import CodexGraphQLClient
from src.api.queries import GET_TOKEN_EVENTS_FOR_MAKER

logger = logging.getLogger(__name__)

MODULE = "wallet_pnl"


class WalletCollector:
    """Collect wallet-specific trade history for PnL computation."""

    def __init__(self, client: CodexGraphQLClient, output_dir: str = "data/raw/wallets"):
        self.client = client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def collect_maker_events(
        self,
        maker_address: str,
        network_id: int,
        token_address: str | None = None,
        max_pages: int = 10,
    ) -> pd.DataFrame:
        """Fetch trade events for a specific wallet (maker).

        Args:
            maker_address: Wallet address.
            network_id: Codex network ID.
            token_address: Optional token to filter events.
            max_pages: Max pages to fetch.

        Returns:
            DataFrame of wallet events.
        """
        all_events = []
        cursor = None

        for page in range(max_pages):
            input_vars: dict = {
                "maker": maker_address,
                "networkId": network_id,
            }
            if token_address:
                input_vars["tokenAddress"] = token_address
            if cursor:
                input_vars["cursor"] = cursor

            data = await self.client.execute(
                GET_TOKEN_EVENTS_FOR_MAKER,
                {"input": input_vars},
                module=MODULE,
                query_type="getTokenEventsForMaker",
            )

            result = data.get("getTokenEventsForMaker", {})
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
            safe_addr = maker_address[:16]
            path = self.output_dir / f"wallet_{safe_addr}_{network_id}.parquet"
            df.to_parquet(path, index=False)
        return df

    async def collect_top_wallets(
        self, wallets: list[dict], max_pages: int = 10
    ) -> dict[str, pd.DataFrame]:
        """Collect events for a list of top wallets.

        Args:
            wallets: List of dicts with 'address' and 'network_id'.
        """
        results = {}
        for i, wallet in enumerate(wallets):
            logger.info("Wallet %d/%d: %s", i + 1, len(wallets), wallet["address"][:16])
            df = await self.collect_maker_events(
                maker_address=wallet["address"],
                network_id=wallet["network_id"],
                max_pages=max_pages,
            )
            results[wallet["address"]] = df
        return results
