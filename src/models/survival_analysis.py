"""Survival analysis: Kaplan-Meier, Cox Proportional Hazards, AFT models."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter, CoxPHFitter, WeibullAFTFitter, LogNormalAFTFitter
from lifelines.statistics import logrank_test, multivariate_logrank_test


class SurvivalAnalyzer:
    """Publication-quality survival analysis for meme coin lifespans."""

    def __init__(self, survival_df: pd.DataFrame):
        """
        Args:
            survival_df: DataFrame with 'duration_days', 'event', and covariates.
        """
        self.df = survival_df.copy()
        self.km_results: dict[str, KaplanMeierFitter] = {}
        self.cox_result: CoxPHFitter | None = None
        self.aft_result: WeibullAFTFitter | None = None

    def fit_kaplan_meier(
        self,
        group_col: str | None = None,
        label: str = "Overall",
    ) -> dict[str, KaplanMeierFitter]:
        """Fit Kaplan-Meier survival curves, optionally stratified.

        Args:
            group_col: Column to stratify by (e.g., 'chain', 'exchange_name').
            label: Label for overall curve if no grouping.

        Returns:
            Dict of group_name -> fitted KaplanMeierFitter.
        """
        results = {}

        if group_col is None:
            kmf = KaplanMeierFitter()
            kmf.fit(self.df["duration_days"], event_observed=self.df["event"], label=label)
            results[label] = kmf
        else:
            groups = self.df[group_col].dropna().unique()
            for group in groups:
                mask = self.df[group_col] == group
                subset = self.df[mask]
                if len(subset) < 10:
                    continue
                kmf = KaplanMeierFitter()
                kmf.fit(subset["duration_days"], event_observed=subset["event"], label=str(group))
                results[str(group)] = kmf

        self.km_results.update(results)
        return results

    def logrank_test(self, group_col: str) -> dict[str, Any]:
        """Perform log-rank test for differences between survival curves.

        Args:
            group_col: Column defining groups.

        Returns:
            Dict with test statistic and p-value.
        """
        groups = self.df[group_col].dropna().unique()
        if len(groups) < 2:
            return {"error": "Need at least 2 groups"}

        if len(groups) == 2:
            mask1 = self.df[group_col] == groups[0]
            mask2 = self.df[group_col] == groups[1]
            result = logrank_test(
                self.df[mask1]["duration_days"], self.df[mask2]["duration_days"],
                event_observed_A=self.df[mask1]["event"],
                event_observed_B=self.df[mask2]["event"],
            )
            return {
                "test_statistic": result.test_statistic,
                "p_value": result.p_value,
                "groups": list(groups),
            }
        else:
            result = multivariate_logrank_test(
                self.df["duration_days"],
                self.df[group_col],
                self.df["event"],
            )
            return {
                "test_statistic": result.test_statistic,
                "p_value": result.p_value,
                "groups": list(groups),
            }

    def fit_cox_ph(
        self,
        covariates: list[str] | None = None,
        step_size: float = 0.5,
    ) -> CoxPHFitter:
        """Fit Cox Proportional Hazards model.

        Args:
            covariates: List of covariate columns. If None, uses defaults.

        Returns:
            Fitted CoxPHFitter.
        """
        if covariates is None:
            covariates = [
                "sniper_count", "bundler_count", "dev_held_pct",
                "log_liquidity", "log_holders", "buy_sell_ratio_1h",
                "wallet_age_avg",
            ]

        # Filter to columns that exist and have variance
        available = [c for c in covariates if c in self.df.columns]
        model_df = self.df[["duration_days", "event"] + available].dropna()

        # Remove zero-variance columns
        for col in available:
            if model_df[col].std() == 0:
                model_df = model_df.drop(columns=[col])
                available.remove(col)

        cph = CoxPHFitter()
        cph.fit(model_df, duration_col="duration_days", event_col="event", step_size=step_size)

        self.cox_result = cph
        return cph

    def cox_summary_table(self) -> pd.DataFrame:
        """Extract publication-ready Cox PH results table."""
        if self.cox_result is None:
            raise ValueError("Must fit Cox PH model first")

        summary = self.cox_result.summary
        summary["hazard_ratio"] = np.exp(summary["coef"])
        summary["hr_lower"] = np.exp(summary["coef lower 95%"])
        summary["hr_upper"] = np.exp(summary["coef upper 95%"])

        return summary[["coef", "exp(coef)", "se(coef)", "z", "p", "hazard_ratio", "hr_lower", "hr_upper"]]

    def check_proportional_hazards(self) -> pd.DataFrame:
        """Test proportional hazards assumption via Schoenfeld residuals."""
        if self.cox_result is None:
            raise ValueError("Must fit Cox PH model first")
        return self.cox_result.check_assumptions(self.df, show_plots=False)

    def concordance_index(self) -> float:
        """Return the concordance index (C-statistic) of the Cox model."""
        if self.cox_result is None:
            raise ValueError("Must fit Cox PH model first")
        return self.cox_result.concordance_index_

    def fit_aft_weibull(self, covariates: list[str] | None = None) -> WeibullAFTFitter:
        """Fit Weibull Accelerated Failure Time model as robustness check."""
        if covariates is None:
            covariates = [
                "sniper_count", "bundler_count", "dev_held_pct",
                "log_liquidity", "log_holders", "buy_sell_ratio_1h",
            ]

        available = [c for c in covariates if c in self.df.columns]
        model_df = self.df[["duration_days", "event"] + available].dropna()

        for col in available:
            if model_df[col].std() == 0:
                model_df = model_df.drop(columns=[col])

        aft = WeibullAFTFitter()
        aft.fit(model_df, duration_col="duration_days", event_col="event")
        self.aft_result = aft
        return aft

    def fit_aft_lognormal(self, covariates: list[str] | None = None) -> LogNormalAFTFitter:
        """Fit Log-Normal AFT model as alternative parametric specification."""
        if covariates is None:
            covariates = [
                "sniper_count", "bundler_count", "dev_held_pct",
                "log_liquidity", "log_holders", "buy_sell_ratio_1h",
            ]

        available = [c for c in covariates if c in self.df.columns]
        model_df = self.df[["duration_days", "event"] + available].dropna()

        for col in available:
            if model_df[col].std() == 0:
                model_df = model_df.drop(columns=[col])

        aft = LogNormalAFTFitter()
        aft.fit(model_df, duration_col="duration_days", event_col="event")
        return aft
