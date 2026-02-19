"""Token lifecycle classification: birth, graduation, death, scam."""

from __future__ import annotations

import numpy as np
import pandas as pd


# Death threshold: 24h volume drops below $100
DEATH_VOLUME_THRESHOLD = 100.0

# Lifecycle stages
STAGE_LAUNCHED = "launched"
STAGE_GRADUATED = "graduated"
STAGE_ALIVE = "alive"
STAGE_DEAD = "dead"
STAGE_SCAM = "scam"


def classify_lifecycle(
    census_df: pd.DataFrame,
    ohlcv_daily: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Classify each token into a lifecycle stage.

    Args:
        census_df: Token census data with columns: address, created_at, last_transaction,
                   volume_24h, liquidity, holders, exchange_name.
        ohlcv_daily: Dict of address -> daily OHLCV DataFrame.

    Returns:
        DataFrame with lifecycle classifications and computed metrics.
    """
    records = []

    for _, row in census_df.iterrows():
        if row.get("tier") == "summary":
            continue

        addr = row.get("address")
        if addr is None:
            continue

        record = {
            "address": addr,
            "chain": row.get("chain"),
            "name": row.get("name"),
            "symbol": row.get("symbol"),
            "created_at": row.get("created_at"),
            "last_transaction": row.get("last_transaction"),
            "exchange_name": row.get("exchange_name"),
        }

        # Compute lifespan
        created = row.get("created_at") or 0
        last_tx = row.get("last_transaction") or created
        lifespan_seconds = max(0, last_tx - created)
        record["lifespan_hours"] = lifespan_seconds / 3600
        record["lifespan_days"] = lifespan_seconds / 86400

        # Check if token has daily OHLCV data
        daily = ohlcv_daily.get(addr, pd.DataFrame())

        if not daily.empty and "volume" in daily.columns:
            volumes = daily["volume"].astype(float)
            record["ath_volume"] = volumes.max()
            record["final_volume"] = volumes.iloc[-1] if len(volumes) > 0 else 0

            # Find death date: first day where volume < threshold after ATH
            ath_idx = volumes.idxmax()
            post_ath = volumes.loc[ath_idx:]
            death_mask = post_ath < DEATH_VOLUME_THRESHOLD
            if death_mask.any():
                death_idx = death_mask.idxmax()
                death_ts = daily.loc[death_idx, "timestamp"]
                record["death_timestamp"] = death_ts
                record["time_to_death_hours"] = (death_ts - created) / 3600
            else:
                record["death_timestamp"] = None
                record["time_to_death_hours"] = None
        else:
            record["ath_volume"] = row.get("volume_24h")
            record["final_volume"] = None
            record["death_timestamp"] = None
            record["time_to_death_hours"] = None

        # Classify stage
        stage = _classify_stage(row, record)
        record["stage"] = stage

        # Survival flags at various horizons
        record["survived_1d"] = record["lifespan_hours"] >= 24
        record["survived_7d"] = record["lifespan_days"] >= 7
        record["survived_30d"] = record["lifespan_days"] >= 30
        record["survived_90d"] = record["lifespan_days"] >= 90

        records.append(record)

    return pd.DataFrame(records)


def _classify_stage(census_row: pd.Series, computed: dict) -> str:
    """Classify a token's lifecycle stage."""
    # Check scam flag
    if census_row.get("potential_scam"):
        return STAGE_SCAM

    # Check if still alive (has recent volume)
    death_ts = computed.get("death_timestamp")
    if death_ts is None and computed.get("lifespan_hours", 0) > 24:
        return STAGE_ALIVE

    # Check graduation (present on a major DEX vs still on launchpad)
    exchange = census_row.get("exchange_name", "")
    launchpad_names = {"Pump.fun", "Moonshot", "Four.meme", "ape.store"}
    if exchange and exchange not in launchpad_names:
        if death_ts is not None:
            return STAGE_DEAD
        return STAGE_GRADUATED

    if death_ts is not None:
        return STAGE_DEAD

    return STAGE_LAUNCHED


def compute_survival_table(lifecycle_df: pd.DataFrame) -> pd.DataFrame:
    """Compute survival statistics grouped by chain and overall."""
    groups = ["overall"] + lifecycle_df["chain"].dropna().unique().tolist()
    rows = []

    for group in groups:
        if group == "overall":
            subset = lifecycle_df
        else:
            subset = lifecycle_df[lifecycle_df["chain"] == group]

        total = len(subset)
        if total == 0:
            continue

        rows.append({
            "group": group,
            "total": total,
            "survived_1d": subset["survived_1d"].sum(),
            "survived_1d_pct": subset["survived_1d"].mean() * 100,
            "survived_7d": subset["survived_7d"].sum(),
            "survived_7d_pct": subset["survived_7d"].mean() * 100,
            "survived_30d": subset["survived_30d"].sum(),
            "survived_30d_pct": subset["survived_30d"].mean() * 100,
            "survived_90d": subset["survived_90d"].sum(),
            "survived_90d_pct": subset["survived_90d"].mean() * 100,
            "median_lifespan_hours": subset["lifespan_hours"].median(),
            "mean_lifespan_hours": subset["lifespan_hours"].mean(),
            "alive_count": (subset["stage"] == STAGE_ALIVE).sum(),
            "dead_count": (subset["stage"] == STAGE_DEAD).sum(),
            "scam_count": (subset["stage"] == STAGE_SCAM).sum(),
            "graduated_count": (subset["stage"] == STAGE_GRADUATED).sum(),
        })

    return pd.DataFrame(rows)
