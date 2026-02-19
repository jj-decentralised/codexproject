"""Survival curve construction for Kaplan-Meier analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd


# Death = 24h volume below this threshold
DEATH_VOLUME_THRESHOLD = 100.0


def prepare_survival_data(
    lifecycle_df: pd.DataFrame,
    study_end_unix: int,
) -> pd.DataFrame:
    """Prepare data for survival analysis (Kaplan-Meier, Cox PH).

    Args:
        lifecycle_df: Token lifecycle DataFrame with lifespan, death info.
        study_end_unix: Unix timestamp of study end (for right-censoring).

    Returns:
        DataFrame with columns: duration, event, and covariates.
    """
    records = []

    for _, row in lifecycle_df.iterrows():
        created = row.get("created_at", 0)
        if not created:
            continue

        # Duration in days
        death_ts = row.get("death_timestamp")
        if death_ts is not None and not np.isnan(death_ts):
            duration = (death_ts - created) / 86400  # days
            event = 1  # observed death
        else:
            duration = (study_end_unix - created) / 86400  # right-censored
            event = 0

        duration = max(duration, 0.01)  # Minimum duration to avoid zero

        records.append({
            "address": row.get("address"),
            "chain": row.get("chain"),
            "duration_days": duration,
            "event": event,
            # Covariates for Cox PH
            "sniper_count": row.get("sniper_count", 0) or 0,
            "bundler_count": row.get("bundler_count", 0) or 0,
            "insider_count": row.get("insider_count", 0) or 0,
            "dev_held_pct": row.get("dev_held_pct", 0) or 0,
            "holders": row.get("holders", 0) or 0,
            "liquidity": float(row.get("liquidity", 0) or 0),
            "volume_24h": float(row.get("volume_24h", 0) or 0),
            "buy_count_1h": row.get("buy_count_1h", 0) or 0,
            "sell_count_1h": row.get("sell_count_1h", 0) or 0,
            "wallet_age_avg": row.get("wallet_age_avg", 0) or 0,
            "exchange_name": row.get("exchange_name"),
            "stage": row.get("stage"),
        })

    df = pd.DataFrame(records)

    # Derived features
    if not df.empty:
        buy_sell = df["buy_count_1h"] + df["sell_count_1h"]
        df["buy_sell_ratio_1h"] = np.where(
            buy_sell > 0,
            df["buy_count_1h"] / buy_sell,
            0.5,
        )
        df["log_liquidity"] = np.log1p(df["liquidity"])
        df["log_volume_24h"] = np.log1p(df["volume_24h"])
        df["log_holders"] = np.log1p(df["holders"])

    return df


def compute_kaplan_meier_table(
    survival_df: pd.DataFrame,
    group_col: str | None = None,
    time_points: list[float] | None = None,
) -> pd.DataFrame:
    """Compute empirical survival probabilities at given time points.

    This is a simple empirical implementation. For full KM with confidence
    intervals, use lifelines.KaplanMeierFitter in the models layer.

    Args:
        survival_df: DataFrame with 'duration_days' and 'event' columns.
        group_col: Optional column to stratify by.
        time_points: Time points (days) at which to evaluate survival.

    Returns:
        DataFrame with survival probabilities.
    """
    if time_points is None:
        time_points = [0.25, 0.5, 1, 3, 7, 14, 30, 60, 90, 180]

    groups = ["overall"]
    if group_col and group_col in survival_df.columns:
        groups.extend(survival_df[group_col].dropna().unique().tolist())

    rows = []
    for group in groups:
        if group == "overall":
            subset = survival_df
        else:
            subset = survival_df[survival_df[group_col] == group]

        n_total = len(subset)
        if n_total == 0:
            continue

        row = {"group": group, "n": n_total}
        for tp in time_points:
            # Survived past time point = either censored after tp or died after tp
            survived = ((subset["duration_days"] > tp) | (subset["event"] == 0)).sum()
            # More accurate: at-risk at time tp
            at_risk = (subset["duration_days"] >= tp).sum()
            died_by = ((subset["duration_days"] <= tp) & (subset["event"] == 1)).sum()
            survival_pct = (1 - died_by / n_total) * 100 if n_total > 0 else 0
            row[f"survived_{tp}d_pct"] = survival_pct

        rows.append(row)

    return pd.DataFrame(rows)
