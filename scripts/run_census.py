"""Phase 1: Token census — enumerate all meme coins launched in the study period."""

from __future__ import annotations

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.client import CodexGraphQLClient
from src.data.collectors.token_census import TokenCensus

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


async def main(dry_run: bool = False):
    api_key = os.getenv("CODEX_API_KEY")
    if not api_key:
        logger.error("CODEX_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    if dry_run:
        logger.info("DRY RUN: validating query construction without API calls")
        from config.time_windows import daily_windows
        from config.settings import STUDY_CHAINS, STUDY_NETWORK_IDS
        windows = daily_windows()
        logger.info("Study period: %d days", len(windows))
        logger.info("Chains: %s", STUDY_CHAINS)
        logger.info("Network IDs: %s", STUDY_NETWORK_IDS)
        logger.info(
            "Estimated census calls: ~%d (4 chains x %d days x ~20 pages)",
            4 * len(windows) * 20,
            len(windows),
        )
        return

    async with CodexGraphQLClient(api_key=api_key) as client:
        census = TokenCensus(client)
        logger.info("Starting full census...")

        df = await census.run_full_census()

        # Summary
        token_records = df[df["tier"] != "summary"]
        summary_records = df[df["tier"] == "summary"]

        logger.info("Census complete:")
        logger.info("  Tier A tokens: %d", len(token_records[token_records["tier"] == "tier_a"]))
        logger.info("  Tier B samples: %d", len(token_records[token_records["tier"] == "tier_b"]))
        logger.info("  Total estimated (from summaries): %s",
                     summary_records["total_estimated"].sum() if "total_estimated" in summary_records else "N/A")
        logger.info("  API calls used: %d", client.budget.total_calls)
        logger.info("  Remaining budget: %d", client.budget.remaining)

        # Budget breakdown
        for module, count in client.budget.summary_by_module().items():
            logger.info("  Module '%s': %d calls", module, count)


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    asyncio.run(main(dry_run=dry))
