"""Panel regression: chain and launchpad effects on survival and returns."""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS, RandomEffects


class PanelRegression:
    """Cross-sectional panel regression for meme coin outcomes."""

    def __init__(self, panel_df: pd.DataFrame):
        self.df = panel_df.copy()

    def ols_cross_section(
        self,
        dependent: str,
        controls: list[str] | None = None,
        chain_fe: bool = True,
        launchpad_fe: bool = True,
    ) -> sm.OLS:
        """Run OLS cross-sectional regression with fixed effects.

        Args:
            dependent: Outcome variable column.
            controls: Control variable columns.
            chain_fe: Include chain dummies.
            launchpad_fe: Include launchpad dummy (is_pumpfun).

        Returns:
            Fitted OLS result.
        """
        if controls is None:
            controls = [
                "sniper_count", "bundler_count", "dev_held_pct",
                "log_liquidity", "log_holders", "buy_sell_ratio_1h",
                "wallet_age_avg",
            ]

        available = [c for c in controls if c in self.df.columns]
        rhs_cols = available.copy()

        if chain_fe:
            chain_dummies = [c for c in self.df.columns if c.startswith("chain_")]
            rhs_cols.extend(chain_dummies)

        if launchpad_fe and "is_pumpfun" in self.df.columns:
            rhs_cols.append("is_pumpfun")

        model_df = self.df[[dependent] + rhs_cols].dropna()
        if len(model_df) < len(rhs_cols) + 10:
            raise ValueError(f"Insufficient observations: {len(model_df)} rows, {len(rhs_cols)} vars")

        X = sm.add_constant(model_df[rhs_cols])
        y = model_df[dependent]

        result = sm.OLS(y, X).fit(cov_type="HC1")  # Heteroskedasticity-robust SEs
        return result

    def logit_survival(
        self,
        target: str = "survived_7d",
        controls: list[str] | None = None,
    ) -> sm.Logit:
        """Logistic regression for binary survival outcome with chain/launchpad FEs."""
        if controls is None:
            controls = [
                "sniper_count", "bundler_count", "dev_held_pct",
                "log_liquidity", "log_holders", "buy_sell_ratio_1h",
            ]

        available = [c for c in controls if c in self.df.columns]
        rhs_cols = available.copy()

        chain_dummies = [c for c in self.df.columns if c.startswith("chain_")]
        rhs_cols.extend(chain_dummies)

        if "is_pumpfun" in self.df.columns:
            rhs_cols.append("is_pumpfun")

        model_df = self.df[[target] + rhs_cols].dropna()
        X = sm.add_constant(model_df[rhs_cols])
        y = model_df[target].astype(int)

        result = sm.Logit(y, X).fit(disp=0, maxiter=100)
        return result

    def chain_comparison(
        self,
        outcomes: list[str] | None = None,
    ) -> pd.DataFrame:
        """Compare outcomes across chains with controlled means.

        Args:
            outcomes: List of outcome columns to compare.

        Returns:
            DataFrame with chain-level statistics.
        """
        if outcomes is None:
            outcomes = [
                "survived_1d", "survived_7d", "survived_30d",
                "return_24h", "return_7d", "return_30d",
                "lifespan_days",
            ]

        available = [o for o in outcomes if o in self.df.columns]
        rows = []

        for chain in self.df["chain"].dropna().unique():
            subset = self.df[self.df["chain"] == chain]
            row = {"chain": chain, "n": len(subset)}

            for outcome in available:
                series = pd.to_numeric(subset[outcome], errors="coerce").dropna()
                if not series.empty:
                    row[f"{outcome}_mean"] = series.mean()
                    row[f"{outcome}_median"] = series.median()
                    row[f"{outcome}_std"] = series.std()

            rows.append(row)

        return pd.DataFrame(rows)

    def launchpad_comparison(self) -> pd.DataFrame:
        """Compare outcomes across launchpads."""
        if "exchange_name" not in self.df.columns:
            return pd.DataFrame()

        outcomes = ["survived_7d", "survived_30d", "return_7d", "lifespan_days"]
        available = [o for o in outcomes if o in self.df.columns]

        rows = []
        for lp in self.df["exchange_name"].dropna().unique():
            subset = self.df[self.df["exchange_name"] == lp]
            if len(subset) < 10:
                continue

            row = {"launchpad": lp, "n": len(subset)}
            for outcome in available:
                series = pd.to_numeric(subset[outcome], errors="coerce").dropna()
                if not series.empty:
                    row[f"{outcome}_mean"] = series.mean()
                    row[f"{outcome}_median"] = series.median()

            rows.append(row)

        return pd.DataFrame(rows).sort_values("n", ascending=False)
