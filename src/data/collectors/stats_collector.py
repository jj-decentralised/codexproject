"""Detailed pair stats collector using getDetailedPairStats."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.api.client import CodexGraphQLClient
from src.api.queries import GET_DETAILED_PAIR_STATS

logger = logging.getLogger(__name__)

MODULE = "pair_stats"


class StatsCollector:
    """Collect bucketed detailed pair statistics."""

    def __init__(self, client: CodexGraphQLClient, output_dir: str = "data/raw/stats"):
        self.client = client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def collect_pair_stats(
        self,
        pair_address: str,
        network_id: int,
        stats_type: str = "FILTERED",
    ) -> dict:
        """Fetch detailed pair stats for a single pair.

        Args:
            pair_address: DEX pair address.
            network_id: Codex network ID.
            stats_type: 'FILTERED' (no MEV) or 'UNFILTERED'.

        Returns:
            Raw stats dict with bucketed time series.
        """
        variables = {
            "pairId": pair_address,
            "networkId": network_id,
            "tokenOfInterest": "token0",
            "statsType": stats_type,
        }

        data = await self.client.execute(
            GET_DETAILED_PAIR_STATS,
            variables,
            module=MODULE,
            query_type="getDetailedPairStats",
        )

        return data.get("getDetailedPairStats", {})

    def _parse_stat_bucket(self, stats: dict, bucket_name: str) -> list[dict]:
        """Parse a single stat bucket into flat records."""
        bucket = stats.get(bucket_name, {})
        usd_stats = bucket.get("statsUsd", {})
        records = []

        close_data = usd_stats.get("close", [])
        volume_data = usd_stats.get("volume", [])
        buyers_data = usd_stats.get("buyers", [])
        sellers_data = usd_stats.get("sellers", [])

        # Use close timestamps as the primary timeline
        for i, point in enumerate(close_data):
            record = {
                "bucket": bucket_name,
                "timestamp": point.get("timestamp"),
                "close_usd": point.get("value"),
                "volume_usd": volume_data[i].get("value") if i < len(volume_data) else None,
                "buyers": buyers_data[i].get("value") if i < len(buyers_data) else None,
                "sellers": sellers_data[i].get("value") if i < len(sellers_data) else None,
            }
            records.append(record)

        return records

    async def collect_batch(
        self, tokens: list[dict], stats_type: str = "FILTERED"
    ) -> dict[str, pd.DataFrame]:
        """Collect detailed stats for a batch of tokens.

        Args:
            tokens: List of dicts with 'pair_address', 'network_id', 'address'.
        """
        results = {}
        buckets = ["stats_min5", "stats_hour1", "stats_hour4", "stats_hour12", "stats_day1"]

        for i, token in enumerate(tokens):
            logger.info("Stats %d/%d: %s", i + 1, len(tokens), token.get("address", "?"))

            stats = await self.collect_pair_stats(
                pair_address=token["pair_address"],
                network_id=token["network_id"],
                stats_type=stats_type,
            )

            all_records = []
            for bucket in buckets:
                all_records.extend(self._parse_stat_bucket(stats, bucket))

            df = pd.DataFrame(all_records)
            if not df.empty:
                path = self.output_dir / f"{token['address']}_stats.parquet"
                df.to_parquet(path, index=False)

            results[token["address"]] = df

        return results
