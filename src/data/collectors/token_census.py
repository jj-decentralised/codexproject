"""Token census: enumerate all meme coins launched across chains during study period."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.api.client import CodexGraphQLClient
from src.api.queries import FILTER_TOKENS, FILTER_TOKENS_WITH_SNIPER_DATA
from config.settings import STUDY_NETWORK_IDS, STUDY_CHAINS, TIER_A_VOLUME_MIN
from config.time_windows import daily_windows

logger = logging.getLogger(__name__)

MODULE = "census"
MAX_RESULTS_PER_CALL = 200


class TokenCensus:
    """Enumerate meme coins launched during the study period.

    Strategy:
      Tier A: Tokens with volume24 > $1,000 — full enumeration via paginated filterTokens.
      Tier B: Low-volume tokens — statistical sample to extrapolate total counts.
    """

    def __init__(self, client: CodexGraphQLClient, output_dir: str = "data/raw/census"):
        self.client = client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def collect_tier_a(self, network_id: int, day_start: int, day_end: int) -> list[dict]:
        """Full census of tokens with meaningful volume for a single day + chain."""
        all_results = []
        offset = 0

        while True:
            variables = {
                "filters": {
                    "network": [network_id],
                    "createdAt": {"gte": day_start, "lte": day_end},
                    "volume24": {"gte": TIER_A_VOLUME_MIN},
                    "potentialScam": False,
                },
                "rankings": {"attribute": "volume24", "direction": "DESC"},
                "limit": MAX_RESULTS_PER_CALL,
                "offset": offset,
            }

            data = await self.client.execute(
                FILTER_TOKENS_WITH_SNIPER_DATA,
                variables,
                module=MODULE,
                query_type="filterTokens",
            )

            results = data.get("filterTokens", {}).get("results", [])
            if not results:
                break

            all_results.extend(results)
            offset += len(results)

            if len(results) < MAX_RESULTS_PER_CALL:
                break

        return all_results

    async def collect_tier_b_sample(
        self, network_id: int, day_start: int, day_end: int, sample_size: int = 200
    ) -> tuple[list[dict], int]:
        """Sample low-volume tokens and return (sample, estimated_total_count)."""
        variables = {
            "filters": {
                "network": [network_id],
                "createdAt": {"gte": day_start, "lte": day_end},
                "volume24": {"lt": TIER_A_VOLUME_MIN},
            },
            "rankings": {"attribute": "createdAt", "direction": "DESC"},
            "limit": min(sample_size, MAX_RESULTS_PER_CALL),
            "offset": 0,
        }

        data = await self.client.execute(
            FILTER_TOKENS,
            variables,
            module=MODULE,
            query_type="filterTokens",
        )

        ft = data.get("filterTokens", {})
        results = ft.get("results", [])
        total_count = ft.get("count", len(results))

        return results, total_count

    async def collect_day(self, network_id: int, chain_name: str, day_start: int, day_end: int) -> dict:
        """Collect all token data for a single chain-day."""
        tier_a = await self.collect_tier_a(network_id, day_start, day_end)
        tier_b_sample, tier_b_total = await self.collect_tier_b_sample(network_id, day_start, day_end)

        return {
            "chain": chain_name,
            "network_id": network_id,
            "day_start": day_start,
            "day_end": day_end,
            "tier_a_tokens": tier_a,
            "tier_a_count": len(tier_a),
            "tier_b_sample": tier_b_sample,
            "tier_b_estimated_total": tier_b_total,
        }

    async def run_full_census(self) -> pd.DataFrame:
        """Run the complete census across all chains and days."""
        windows = daily_windows()
        all_records = []

        for i, (day_start, day_end) in enumerate(windows):
            for chain_name, network_id in zip(STUDY_CHAINS, STUDY_NETWORK_IDS):
                logger.info(
                    "Census day %d/%d, chain=%s", i + 1, len(windows), chain_name
                )
                day_data = await self.collect_day(network_id, chain_name, day_start, day_end)

                # Flatten Tier A tokens into records
                for token in day_data["tier_a_tokens"]:
                    record = self._flatten_token(token, chain_name, "tier_a")
                    all_records.append(record)

                # Flatten Tier B sample
                for token in day_data["tier_b_sample"]:
                    record = self._flatten_token(token, chain_name, "tier_b")
                    all_records.append(record)

                # Store daily summary
                all_records.append({
                    "chain": chain_name,
                    "day_start": day_start,
                    "tier": "summary",
                    "tier_a_count": day_data["tier_a_count"],
                    "tier_b_estimated_total": day_data["tier_b_estimated_total"],
                    "total_estimated": day_data["tier_a_count"] + day_data["tier_b_estimated_total"],
                })

        df = pd.DataFrame(all_records)
        output_path = self.output_dir / "full_census.parquet"
        df.to_parquet(output_path, index=False)
        logger.info("Census saved: %s (%d records)", output_path, len(df))
        return df

    @staticmethod
    def _flatten_token(token: dict, chain: str, tier: str) -> dict:
        """Flatten nested GraphQL token result into a flat dict."""
        token_info = token.get("token", {})
        pair_info = token.get("pair", {})
        exchanges = token.get("exchanges", [])

        return {
            "chain": chain,
            "tier": tier,
            "address": token_info.get("address"),
            "name": token_info.get("name"),
            "symbol": token_info.get("symbol"),
            "network_id": token_info.get("networkId"),
            "creator_address": token_info.get("creatorAddress"),
            "pair_address": pair_info.get("address"),
            "exchange_name": exchanges[0].get("name") if exchanges else None,
            "created_at": token.get("createdAt"),
            "last_transaction": token.get("lastTransaction"),
            "buy_count_1h": token.get("buyCount1"),
            "buy_count_24h": token.get("buyCount24"),
            "sell_count_1h": token.get("sellCount1"),
            "sell_count_24h": token.get("sellCount24"),
            "change_1h": token.get("change1"),
            "change_24h": token.get("change24"),
            "volume_24h": token.get("volume24"),
            "liquidity": token.get("liquidity"),
            "market_cap": token.get("marketCap"),
            "price_usd": token.get("priceUSD"),
            "holders": token.get("holders"),
            "wallet_age_avg": token.get("walletAgeAvg"),
            "sniper_count": token.get("sniperCount"),
            "bundler_count": token.get("bundlerCount"),
            "insider_count": token.get("insiderCount"),
            "dev_held_pct": token.get("devHeldPercentage"),
            "sniper_held_pct": token.get("sniperHeldPercentage"),
            "bundler_held_pct": token.get("bundlerHeldPercentage"),
            "insider_held_pct": token.get("insiderHeldPercentage"),
        }
