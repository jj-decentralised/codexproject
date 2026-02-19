"""Phase 2: Stratified sampling and deep data collection."""

from __future__ import annotations

import asyncio
import logging
import os
import sys

import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.client import CodexGraphQLClient
from src.data.collectors.ohlcv_collector import OHLCVCollector
from src.data.collectors.event_collector import EventCollector
from src.data.collectors.wallet_collector import WalletCollector
from src.data.collectors.stats_collector import StatsCollector
from config.settings import SAMPLE_PER_CHAIN, SAMPLE_STRATA, STUDY_CHAINS

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def build_stratified_sample(census_path: str = "data/raw/census/full_census.parquet") -> pd.DataFrame:
    """Build the stratified sample of 10,000 tokens from census data."""
    df = pd.read_parquet(census_path)
    tokens = df[df["tier"] != "summary"].copy()

    # Convert numeric columns
    for col in ["volume_24h", "change_24h", "last_transaction", "created_at"]:
        if col in tokens.columns:
            tokens[col] = pd.to_numeric(tokens[col], errors="coerce")

    sampled = []

    for chain in STUDY_CHAINS:
        chain_tokens = tokens[tokens["chain"] == chain]
        if chain_tokens.empty:
            continue

        n = min(SAMPLE_PER_CHAIN, len(chain_tokens))

        # Winners: top returns
        if "change_24h" in chain_tokens.columns:
            winners = chain_tokens.nlargest(SAMPLE_STRATA["winners"], "change_24h")
            sampled.append(winners)

        # Survivors: still trading (last_transaction recent)
        if "last_transaction" in chain_tokens.columns:
            recent = chain_tokens.nlargest(SAMPLE_STRATA["survivors"], "last_transaction")
            sampled.append(recent)

        # Fast deaths: lowest last_transaction relative to created_at
        if "last_transaction" in chain_tokens.columns and "created_at" in chain_tokens.columns:
            chain_tokens_copy = chain_tokens.copy()
            chain_tokens_copy["lifespan"] = chain_tokens_copy["last_transaction"] - chain_tokens_copy["created_at"]
            fast_deaths = chain_tokens_copy.nsmallest(SAMPLE_STRATA["fast_deaths"], "lifespan")
            sampled.append(fast_deaths.drop(columns=["lifespan"]))

        # Random sample
        remaining_n = min(SAMPLE_STRATA["random"] + SAMPLE_STRATA["graduated"], len(chain_tokens))
        random_sample = chain_tokens.sample(n=remaining_n, random_state=42)
        sampled.append(random_sample)

    result = pd.concat(sampled, ignore_index=True).drop_duplicates(subset=["address"])
    logger.info("Stratified sample: %d tokens", len(result))
    return result


async def main():
    api_key = os.getenv("CODEX_API_KEY")
    if not api_key:
        logger.error("CODEX_API_KEY not set")
        sys.exit(1)

    # Build stratified sample
    sample = build_stratified_sample()
    sample.to_parquet("data/processed/stratified_sample.parquet", index=False)

    async with CodexGraphQLClient(api_key=api_key) as client:
        # Phase 2a: OHLCV collection
        logger.info("=== Phase 2a: OHLCV Collection ===")
        ohlcv = OHLCVCollector(client)
        token_list = sample[["pair_address", "network_id", "created_at", "address", "last_transaction"]].dropna(
            subset=["pair_address", "network_id", "created_at"]
        ).to_dict("records")
        await ohlcv.collect_batch(token_list)
        logger.info("OHLCV complete. Calls: %d", client.budget.total_calls)

        # Phase 2b: Event collection (top 1000 by volume)
        logger.info("=== Phase 2b: Event Collection ===")
        events = EventCollector(client)
        top_volume = sample.nlargest(1000, "volume_24h")
        event_tokens = top_volume[["address", "network_id"]].dropna().to_dict("records")
        await events.collect_batch(event_tokens, max_pages=15)
        logger.info("Events complete. Calls: %d", client.budget.total_calls)

        # Phase 2c: Wallet PnL (identify top wallets from events)
        logger.info("=== Phase 2c: Wallet PnL Collection ===")
        wallets = WalletCollector(client)

        # Extract top wallets from collected event data
        events_dir = "data/raw/events"
        wallet_counts: dict[str, int] = {}
        import glob, json
        for event_file in glob.glob(f"{events_dir}/*.parquet"):
            try:
                edf = pd.read_parquet(event_file)
                if "maker" in edf.columns:
                    for maker in edf["maker"].dropna().unique():
                        wallet_counts[maker] = wallet_counts.get(maker, 0) + 1
            except Exception:
                continue

        if wallet_counts:
            # Top 500 wallets by number of unique tokens traded
            top_wallets = sorted(wallet_counts.items(), key=lambda x: x[1], reverse=True)[:500]
            wallet_addresses = [w[0] for w in top_wallets]
            logger.info("Found %d unique wallets, collecting top %d", len(wallet_counts), len(wallet_addresses))
            await wallets.collect_top_wallets(wallet_addresses, network_id=1399811149)
        else:
            logger.warning("No event data found — skipping wallet collection")
        logger.info("Wallet PnL complete. Calls: %d", client.budget.total_calls)

        # Phase 2d: Detailed stats
        logger.info("=== Phase 2d: Detailed Pair Stats ===")
        stats = StatsCollector(client)
        stats_tokens = sample[["pair_address", "network_id", "address"]].dropna(
            subset=["pair_address", "network_id"]
        ).to_dict("records")
        await stats.collect_batch(stats_tokens)
        logger.info("Stats complete. Calls: %d", client.budget.total_calls)

        # Final budget summary
        logger.info("=== Budget Summary ===")
        logger.info("Total calls: %d", client.budget.total_calls)
        logger.info("Remaining: %d", client.budget.remaining)
        for module, count in client.budget.summary_by_module().items():
            logger.info("  %s: %d", module, count)


if __name__ == "__main__":
    asyncio.run(main())
