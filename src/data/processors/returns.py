"""Return calculations at multiple horizons."""

from __future__ import annotations

import numpy as np
import pandas as pd


RETURN_HORIZONS = {
    "1h": 3600,
    "6h": 21600,
    "24h": 86400,
    "48h": 172800,
    "7d": 604800,
    "30d": 2592000,
}


def compute_token_returns(
    ohlcv_hourly: pd.DataFrame,
    ohlcv_daily: pd.DataFrame,
    created_at: int,
) -> dict[str, float | None]:
    """Compute returns at multiple horizons from token creation.

    Uses hourly bars for short horizons, daily for longer.
    Returns are capped at -100% (total loss).
    """
    results = {}

    for horizon_name, horizon_seconds in RETURN_HORIZONS.items():
        target_ts = created_at + horizon_seconds

        # Use hourly data for < 48h, daily for >= 7d
        if horizon_seconds <= 172800 and not ohlcv_hourly.empty:
            df = ohlcv_hourly
        elif not ohlcv_daily.empty:
            df = ohlcv_daily
        else:
            results[f"return_{horizon_name}"] = None
            continue

        # Find initial price (first available close)
        if df.empty or "close" not in df.columns:
            results[f"return_{horizon_name}"] = None
            continue

        initial_price = pd.to_numeric(df["close"].iloc[0], errors="coerce")
        if initial_price is None or initial_price == 0 or np.isnan(initial_price):
            results[f"return_{horizon_name}"] = None
            continue

        # Find price at horizon
        target_df = df[df["timestamp"] <= target_ts]
        if target_df.empty:
            results[f"return_{horizon_name}"] = None
            continue

        horizon_price = pd.to_numeric(target_df["close"].iloc[-1], errors="coerce")
        if horizon_price is None or np.isnan(horizon_price):
            results[f"return_{horizon_name}"] = None
            continue

        ret = (horizon_price - initial_price) / initial_price
        results[f"return_{horizon_name}"] = max(ret, -1.0)  # Cap at -100%

    # Max return (highest price ever / initial price - 1)
    all_data = pd.concat([ohlcv_hourly, ohlcv_daily]).drop_duplicates(subset=["timestamp"])
    if not all_data.empty and "high" in all_data.columns:
        initial_price = pd.to_numeric(all_data["close"].iloc[0], errors="coerce")
        max_price = pd.to_numeric(all_data["high"], errors="coerce").max()
        if initial_price and initial_price > 0 and not np.isnan(max_price):
            results["return_max"] = (max_price - initial_price) / initial_price
        else:
            results["return_max"] = None
    else:
        results["return_max"] = None

    return results


def compute_batch_returns(
    ohlcv_data: dict[str, dict[str, pd.DataFrame]],
    census_df: pd.DataFrame,
) -> pd.DataFrame:
    """Compute returns for all tokens in the sample.

    Args:
        ohlcv_data: Dict of address -> {'daily': df, 'hourly_first_48h': df}.
        census_df: Census with 'address' and 'created_at'.

    Returns:
        DataFrame with one row per token, columns for each horizon return.
    """
    records = []

    for _, row in census_df.iterrows():
        addr = row.get("address")
        if addr is None or addr not in ohlcv_data:
            continue

        lifecycle = ohlcv_data[addr]
        daily = lifecycle.get("daily", pd.DataFrame())
        hourly = lifecycle.get("hourly_first_48h", pd.DataFrame())

        returns = compute_token_returns(
            ohlcv_hourly=hourly,
            ohlcv_daily=daily,
            created_at=row.get("created_at", 0),
        )
        returns["address"] = addr
        returns["chain"] = row.get("chain")
        records.append(returns)

    return pd.DataFrame(records)


def return_distribution_stats(returns_df: pd.DataFrame, column: str) -> dict:
    """Compute distribution statistics for a return column."""
    series = returns_df[column].dropna()
    if series.empty:
        return {}

    return {
        "count": len(series),
        "mean": series.mean(),
        "median": series.median(),
        "std": series.std(),
        "skewness": series.skew(),
        "kurtosis": series.kurtosis(),
        "min": series.min(),
        "max": series.max(),
        "p10": series.quantile(0.10),
        "p25": series.quantile(0.25),
        "p75": series.quantile(0.75),
        "p90": series.quantile(0.90),
        "p99": series.quantile(0.99),
        "pct_positive": (series > 0).mean() * 100,
        "pct_negative": (series < 0).mean() * 100,
        "pct_total_loss": (series <= -0.99).mean() * 100,
        "pct_10x": (series >= 9.0).mean() * 100,
        "pct_100x": (series >= 99.0).mean() * 100,
    }
