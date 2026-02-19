"""Wallet-level profit/loss computation."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_wallet_pnl(events_df: pd.DataFrame) -> dict:
    """Compute PnL for a single wallet from its trade events.

    Args:
        events_df: DataFrame with columns: trade_type, price_usd_total, buy_amount, sell_amount,
                   token0_swap_value_usd, token1_swap_value_usd.

    Returns:
        Dict with PnL metrics.
    """
    if events_df.empty:
        return {"total_bought_usd": 0, "total_sold_usd": 0, "realized_pnl": 0, "trade_count": 0}

    buys = events_df[events_df["trade_type"] == "buy"]
    sells = events_df[events_df["trade_type"] == "sell"]

    total_bought = pd.to_numeric(buys["price_usd_total"], errors="coerce").abs().sum()
    total_sold = pd.to_numeric(sells["price_usd_total"], errors="coerce").abs().sum()

    return {
        "total_bought_usd": total_bought,
        "total_sold_usd": total_sold,
        "realized_pnl": total_sold - total_bought,
        "realized_return": (total_sold / total_bought - 1) if total_bought > 0 else 0,
        "trade_count": len(events_df),
        "buy_count": len(buys),
        "sell_count": len(sells),
        "first_trade_ts": events_df["timestamp"].min(),
        "last_trade_ts": events_df["timestamp"].max(),
    }


def compute_wallet_token_pnl(events_df: pd.DataFrame, token_address: str) -> dict:
    """Compute PnL for a wallet on a specific token."""
    token_events = events_df  # Already filtered by token in collection
    pnl = compute_wallet_pnl(token_events)
    pnl["token_address"] = token_address
    return pnl


def aggregate_wallet_portfolio(
    wallet_events: dict[str, pd.DataFrame],
    wallet_address: str,
) -> dict:
    """Aggregate PnL across all tokens for a wallet.

    Args:
        wallet_events: Dict of token_address -> events DataFrame.
        wallet_address: The wallet address.

    Returns:
        Dict with portfolio-level PnL metrics.
    """
    token_pnls = []

    for token_addr, events in wallet_events.items():
        pnl = compute_wallet_pnl(events)
        pnl["token_address"] = token_addr
        token_pnls.append(pnl)

    if not token_pnls:
        return {"wallet": wallet_address, "total_pnl": 0, "tokens_traded": 0}

    df = pd.DataFrame(token_pnls)

    return {
        "wallet": wallet_address,
        "tokens_traded": len(df),
        "total_bought_usd": df["total_bought_usd"].sum(),
        "total_sold_usd": df["total_sold_usd"].sum(),
        "total_pnl": df["realized_pnl"].sum(),
        "total_return": (
            df["total_sold_usd"].sum() / df["total_bought_usd"].sum() - 1
            if df["total_bought_usd"].sum() > 0
            else 0
        ),
        "hit_rate": (df["realized_pnl"] > 0).mean() * 100,
        "best_trade_pnl": df["realized_pnl"].max(),
        "worst_trade_pnl": df["realized_pnl"].min(),
        "median_trade_pnl": df["realized_pnl"].median(),
        "total_trades": df["trade_count"].sum(),
    }


def classify_wallet_type(
    wallet_address: str,
    events_df: pd.DataFrame,
    creator_addresses: set[str],
    first_swap_timestamps: dict[str, int],
) -> str:
    """Classify a wallet as sniper, bundler, insider, dev, or retail.

    Args:
        wallet_address: The wallet address.
        events_df: Events for this wallet.
        creator_addresses: Set of known token creator addresses.
        first_swap_timestamps: Dict of token_address -> first swap Unix timestamp.

    Returns:
        Wallet type string.
    """
    if wallet_address in creator_addresses:
        return "dev"

    if events_df.empty:
        return "retail"

    # Sniper: bought within 4 seconds of first swap
    buys = events_df[events_df["trade_type"] == "buy"]
    if not buys.empty:
        earliest_buy = buys["timestamp"].min()
        # Check if any of the token's first swaps are within 4s
        for token_addr, first_ts in first_swap_timestamps.items():
            if first_ts and earliest_buy and (earliest_buy - first_ts) <= 4:
                return "sniper"

    # Bundler: 4+ buys in the same block
    if "block_number" in events_df.columns:
        block_buy_counts = buys.groupby("block_number").size()
        if (block_buy_counts >= 4).any():
            return "bundler"

    # Insider: bought early and large position
    if not buys.empty and first_swap_timestamps:
        earliest_buy = buys["timestamp"].min()
        for first_ts in first_swap_timestamps.values():
            if first_ts and earliest_buy and (earliest_buy - first_ts) <= 60:
                total_bought = pd.to_numeric(buys["price_usd_total"], errors="coerce").abs().sum()
                if total_bought > 5000:
                    return "insider"

    return "retail"
