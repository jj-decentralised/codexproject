"""Construct cross-sectional panel datasets for regression analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_token_panel(
    lifecycle_df: pd.DataFrame,
    returns_df: pd.DataFrame,
    survival_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build the master token-level panel dataset.

    Merges lifecycle classifications, return data, and survival covariates
    into a single cross-sectional dataset for regression.

    Args:
        lifecycle_df: From lifecycle.py — stages, lifespan, survival flags.
        returns_df: From returns.py — multi-horizon returns per token.
        survival_df: From survival.py — duration, event, covariates.

    Returns:
        Merged panel DataFrame with one row per token.
    """
    # Start with lifecycle data
    panel = lifecycle_df.copy()

    # Merge returns
    if not returns_df.empty and "address" in returns_df.columns:
        return_cols = [c for c in returns_df.columns if c.startswith("return_") or c == "address"]
        panel = panel.merge(returns_df[return_cols], on="address", how="left")

    # Merge survival covariates
    if not survival_df.empty and "address" in survival_df.columns:
        surv_cols = [
            "address", "duration_days", "event", "buy_sell_ratio_1h",
            "log_liquidity", "log_volume_24h", "log_holders",
        ]
        existing = [c for c in surv_cols if c in survival_df.columns]
        panel = panel.merge(survival_df[existing], on="address", how="left")

    # Create categorical indicators
    if "chain" in panel.columns:
        chain_dummies = pd.get_dummies(panel["chain"], prefix="chain", drop_first=True)
        panel = pd.concat([panel, chain_dummies], axis=1)

    if "exchange_name" in panel.columns:
        panel["is_pumpfun"] = (panel["exchange_name"] == "Pump.fun").astype(int)
        panel["is_raydium"] = panel["exchange_name"].str.contains("Raydium", na=False).astype(int)

    # Numeric conversions for regression
    numeric_cols = [
        "sniper_count", "bundler_count", "insider_count", "dev_held_pct",
        "holders", "liquidity", "volume_24h", "buy_count_1h", "sell_count_1h",
        "wallet_age_avg", "lifespan_hours", "lifespan_days",
    ]
    for col in numeric_cols:
        if col in panel.columns:
            panel[col] = pd.to_numeric(panel[col], errors="coerce").fillna(0)

    return panel


def build_daily_panel(
    census_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build daily aggregate panel: launches, deaths, volume by chain-day.

    Args:
        census_df: Raw census data with per-token records.

    Returns:
        Chain-day level panel.
    """
    token_records = census_df[census_df["tier"] != "summary"].copy()
    if token_records.empty:
        return pd.DataFrame()

    token_records["created_date"] = pd.to_datetime(
        token_records["created_at"], unit="s", utc=True
    ).dt.date

    daily = (
        token_records.groupby(["chain", "created_date"])
        .agg(
            launches=("address", "count"),
            total_volume=("volume_24h", lambda x: pd.to_numeric(x, errors="coerce").sum()),
            avg_liquidity=("liquidity", lambda x: pd.to_numeric(x, errors="coerce").mean()),
            avg_holders=("holders", lambda x: pd.to_numeric(x, errors="coerce").mean()),
            avg_sniper_count=("sniper_count", lambda x: pd.to_numeric(x, errors="coerce").mean()),
            avg_dev_held_pct=("dev_held_pct", lambda x: pd.to_numeric(x, errors="coerce").mean()),
            scam_flagged=("tier", lambda x: 0),  # Would need potentialScam column
        )
        .reset_index()
    )

    return daily
