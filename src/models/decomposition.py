"""Value flow decomposition: retail vs sniper vs bundler vs insider vs dev PnL."""

from __future__ import annotations

import numpy as np
import pandas as pd


class ValueFlowDecomposition:
    """Decompose total value flow by wallet type."""

    def __init__(
        self,
        wallet_pnls: pd.DataFrame,
        wallet_types: dict[str, str],
    ):
        """
        Args:
            wallet_pnls: DataFrame with columns: wallet, total_bought_usd, total_sold_usd,
                         total_pnl, tokens_traded, hit_rate.
            wallet_types: Dict of wallet_address -> type ('sniper', 'bundler', 'insider', 'dev', 'retail').
        """
        self.pnls = wallet_pnls.copy()
        self.pnls["wallet_type"] = self.pnls["wallet"].map(wallet_types).fillna("retail")

    def aggregate_by_type(self) -> pd.DataFrame:
        """Compute aggregate PnL statistics by wallet type."""
        groups = self.pnls.groupby("wallet_type")

        rows = []
        for wtype, group in groups:
            rows.append({
                "wallet_type": wtype,
                "n_wallets": len(group),
                "total_bought_usd": group["total_bought_usd"].sum(),
                "total_sold_usd": group["total_sold_usd"].sum(),
                "total_pnl": group["total_pnl"].sum(),
                "mean_pnl": group["total_pnl"].mean(),
                "median_pnl": group["total_pnl"].median(),
                "mean_return": (
                    group["total_sold_usd"].sum() / group["total_bought_usd"].sum() - 1
                    if group["total_bought_usd"].sum() > 0 else 0
                ),
                "hit_rate": group["hit_rate"].mean() if "hit_rate" in group.columns else None,
                "total_tokens_traded": group["tokens_traded"].sum(),
                "pct_profitable": (group["total_pnl"] > 0).mean() * 100,
            })

        return pd.DataFrame(rows).sort_values("total_pnl", ascending=False)

    def net_transfer_matrix(self) -> pd.DataFrame:
        """Compute net value transfers between wallet types.

        Positive = net receiver, Negative = net payer.
        This is a simplified analysis: total PnL by type sums to ~0 (zero-sum minus fees).
        """
        agg = self.aggregate_by_type()
        return agg[["wallet_type", "total_pnl", "total_bought_usd", "total_sold_usd"]].copy()

    def sankey_data(self) -> dict:
        """Prepare data for a Sankey diagram of value flow.

        Returns:
            Dict with 'sources', 'targets', 'values' for Sankey visualization.
        """
        agg = self.aggregate_by_type()

        # Losers are sources, winners are targets
        losers = agg[agg["total_pnl"] < 0].sort_values("total_pnl")
        winners = agg[agg["total_pnl"] > 0].sort_values("total_pnl", ascending=False)

        sources = []
        targets = []
        values = []

        # Distribute losses proportionally to gains
        total_gained = winners["total_pnl"].sum()
        if total_gained == 0:
            return {"sources": [], "targets": [], "values": []}

        for _, loser in losers.iterrows():
            loss_amount = abs(loser["total_pnl"])
            for _, winner in winners.iterrows():
                # Proportional allocation
                share = winner["total_pnl"] / total_gained
                flow = loss_amount * share
                if flow > 0:
                    sources.append(loser["wallet_type"])
                    targets.append(winner["wallet_type"])
                    values.append(flow)

        return {"sources": sources, "targets": targets, "values": values}

    def summary_stats(self) -> dict:
        """Overall summary statistics."""
        total_volume = self.pnls["total_bought_usd"].sum() + self.pnls["total_sold_usd"].sum()
        total_pnl = self.pnls["total_pnl"].sum()

        # Wallet type breakdown
        type_counts = self.pnls["wallet_type"].value_counts().to_dict()

        return {
            "total_wallets": len(self.pnls),
            "total_volume_usd": total_volume,
            "net_pnl": total_pnl,
            "pct_wallets_profitable": (self.pnls["total_pnl"] > 0).mean() * 100,
            "wallet_type_counts": type_counts,
            "gini_pnl": _gini(self.pnls["total_pnl"].values),
        }


def _gini(values: np.ndarray) -> float:
    """Compute Gini coefficient."""
    values = np.abs(values)
    if len(values) == 0 or values.sum() == 0:
        return 0.0
    sorted_vals = np.sort(values)
    n = len(sorted_vals)
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * sorted_vals) / (n * np.sum(sorted_vals))) - (n + 1) / n
