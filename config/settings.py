"""API endpoints, network IDs, and launchpad configuration."""

from __future__ import annotations

CODEX_GRAPHQL_ENDPOINT = "https://graph.codex.io/graphql"

# Chain network IDs used by Codex.io
NETWORKS = {
    "ethereum": 1,
    "arbitrum": 42161,
    "base": 8453,
    "solana": 1399811149,
    "bsc": 56,
    "polygon": 137,
    "optimism": 10,
    "avalanche": 43114,
}

# Chains included in this study
STUDY_CHAINS = ["solana", "base", "ethereum", "bsc"]
STUDY_NETWORK_IDS = [NETWORKS[chain] for chain in STUDY_CHAINS]

# Known launchpad names on Codex.io
LAUNCHPADS = [
    "Pump.fun",
    "PumpSwap",
    "Moonshot",
    "Four.meme",
    "Believe",
    "Virtuals",
    "Clanker",
    "ape.store",
    "Raydium LaunchLab",
]

# Minimum volume threshold for Tier A census (full enumeration)
TIER_A_VOLUME_MIN = 1000  # USD

# Stratified sample sizes per chain
SAMPLE_PER_CHAIN = 2500
SAMPLE_STRATA = {
    "winners": 500,
    "survivors": 500,
    "fast_deaths": 500,
    "graduated": 500,
    "random": 500,
}
