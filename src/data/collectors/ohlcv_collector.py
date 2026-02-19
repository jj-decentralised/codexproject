"""OHLCV data collector using getBars with windowed chunking."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.api.client import CodexGraphQLClient
from src.api.queries import GET_BARS

logger = logging.getLogger(__name__)

MODULE = "ohlcv"

# Resolution string -> seconds per bar
RESOLUTION_SECONDS = {
    "1": 60,
    "5": 300,
    "15": 900,
    "60": 3600,
    "240": 14400,
    "720": 43200,
    "1D": 86400,
    "7D": 604800,
}

# Max bars per call (Codex limit ~1500, use 1400 for safety)
MAX_BARS_PER_CALL = 1400


class OHLCVCollector:
    """Fetch OHLCV data via getBars with automatic time-window chunking."""

    def __init__(self, client: CodexGraphQLClient, output_dir: str = "data/raw/ohlcv"):
        self.client = client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _window_seconds(self, resolution: str) -> int:
        """Seconds per fetch window for a given resolution."""
        return RESOLUTION_SECONDS[resolution] * MAX_BARS_PER_CALL

    def _make_symbol(self, pair_address: str, network_id: int) -> str:
        """Construct the Codex symbol format: pair_address:network_id."""
        return f"{pair_address}:{network_id}"

    async def fetch_bars(
        self,
        pair_address: str,
        network_id: int,
        resolution: str,
        from_ts: int,
        to_ts: int,
    ) -> pd.DataFrame:
        """Fetch OHLCV bars for a token pair, automatically chunking time windows.

        Args:
            pair_address: DEX pair contract address.
            network_id: Codex network ID.
            resolution: Bar resolution (e.g., '1', '60', '1D').
            from_ts: Start Unix timestamp.
            to_ts: End Unix timestamp.

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume.
        """
        symbol = self._make_symbol(pair_address, network_id)
        window_size = self._window_seconds(resolution)
        all_bars = []

        current_from = from_ts
        while current_from < to_ts:
            current_to = min(current_from + window_size, to_ts)

            variables = {
                "symbol": symbol,
                "from": current_from,
                "to": current_to,
                "resolution": resolution,
            }

            data = await self.client.execute(
                GET_BARS,
                variables,
                module=MODULE,
                query_type="getBars",
            )

            bars = data.get("getBars", {})
            status = bars.get("s", "error")

            if status == "ok":
                timestamps = bars.get("t", [])
                opens = bars.get("o", [])
                highs = bars.get("h", [])
                lows = bars.get("l", [])
                closes = bars.get("c", [])
                volumes = bars.get("volume", bars.get("v", []))

                for i in range(len(timestamps)):
                    all_bars.append({
                        "timestamp": timestamps[i],
                        "open": opens[i] if i < len(opens) else None,
                        "high": highs[i] if i < len(highs) else None,
                        "low": lows[i] if i < len(lows) else None,
                        "close": closes[i] if i < len(closes) else None,
                        "volume": volumes[i] if i < len(volumes) else None,
                    })

            current_from = current_to

        df = pd.DataFrame(all_bars)
        if not df.empty:
            df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

        return df

    async def collect_token_lifecycle(
        self,
        pair_address: str,
        network_id: int,
        created_at: int,
        last_transaction: int | None = None,
    ) -> dict[str, pd.DataFrame]:
        """Collect full lifecycle OHLCV for a token.

        Returns:
            Dict with 'daily' and 'hourly_first_48h' DataFrames.
        """
        end_ts = last_transaction or created_at + (180 * 86400)

        # Daily bars for full lifespan
        daily = await self.fetch_bars(pair_address, network_id, "1D", created_at, end_ts)

        # Hourly bars for first 48 hours
        hourly_end = min(created_at + (48 * 3600), end_ts)
        hourly = await self.fetch_bars(pair_address, network_id, "60", created_at, hourly_end)

        return {"daily": daily, "hourly_first_48h": hourly}

    async def collect_batch(self, tokens: list[dict]) -> dict[str, dict[str, pd.DataFrame]]:
        """Collect OHLCV for a batch of tokens.

        Args:
            tokens: List of dicts with 'pair_address', 'network_id', 'created_at', 'address'.

        Returns:
            Dict keyed by token address -> lifecycle DataFrames.
        """
        results = {}
        for i, token in enumerate(tokens):
            logger.info("OHLCV %d/%d: %s", i + 1, len(tokens), token.get("address", "?"))
            lifecycle = await self.collect_token_lifecycle(
                pair_address=token["pair_address"],
                network_id=token["network_id"],
                created_at=token["created_at"],
                last_transaction=token.get("last_transaction"),
            )
            results[token["address"]] = lifecycle

            # Save incrementally
            addr = token["address"]
            for key, df in lifecycle.items():
                if not df.empty:
                    path = self.output_dir / f"{addr}_{key}.parquet"
                    df.to_parquet(path, index=False)

        return results
