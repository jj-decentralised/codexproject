"""Return distribution analysis: heavy-tail fitting, power-law tests, Gini coefficient."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats as sp_stats
from scipy.optimize import minimize_scalar


class ReturnDistributionAnalyzer:
    """Analyze the statistical distribution of meme coin returns."""

    def __init__(self, returns_df: pd.DataFrame):
        self.df = returns_df.copy()

    def distribution_table(self, horizons: list[str] | None = None) -> pd.DataFrame:
        """Compute distribution statistics at each return horizon.

        Args:
            horizons: List of return column suffixes (e.g., ['1h', '24h', '7d']).

        Returns:
            DataFrame with rows = horizons, columns = statistics.
        """
        if horizons is None:
            horizons = ["1h", "6h", "24h", "48h", "7d", "30d", "max"]

        rows = []
        for h in horizons:
            col = f"return_{h}"
            if col not in self.df.columns:
                continue

            series = self.df[col].dropna()
            if series.empty:
                continue

            rows.append({
                "horizon": h,
                "n": len(series),
                "mean": series.mean(),
                "median": series.median(),
                "std": series.std(),
                "skewness": series.skew(),
                "kurtosis": series.kurtosis(),
                "min": series.min(),
                "max": series.max(),
                "p1": series.quantile(0.01),
                "p5": series.quantile(0.05),
                "p10": series.quantile(0.10),
                "p25": series.quantile(0.25),
                "p75": series.quantile(0.75),
                "p90": series.quantile(0.90),
                "p95": series.quantile(0.95),
                "p99": series.quantile(0.99),
                "pct_positive": (series > 0).mean() * 100,
                "pct_total_loss": (series <= -0.99).mean() * 100,
                "pct_2x": (series >= 1.0).mean() * 100,
                "pct_10x": (series >= 9.0).mean() * 100,
                "pct_100x": (series >= 99.0).mean() * 100,
                "pct_1000x": (series >= 999.0).mean() * 100,
            })

        return pd.DataFrame(rows)

    def distribution_by_chain(self, horizon: str = "7d") -> pd.DataFrame:
        """Compute distribution statistics stratified by chain."""
        col = f"return_{horizon}"
        if col not in self.df.columns or "chain" not in self.df.columns:
            return pd.DataFrame()

        rows = []
        for chain in self.df["chain"].dropna().unique():
            subset = self.df[self.df["chain"] == chain][col].dropna()
            if len(subset) < 10:
                continue

            rows.append({
                "chain": chain,
                "n": len(subset),
                "mean": subset.mean(),
                "median": subset.median(),
                "p10": subset.quantile(0.10),
                "p25": subset.quantile(0.25),
                "p75": subset.quantile(0.75),
                "p90": subset.quantile(0.90),
                "p99": subset.quantile(0.99),
                "pct_positive": (subset > 0).mean() * 100,
                "pct_10x": (subset >= 9.0).mean() * 100,
            })

        return pd.DataFrame(rows)

    def fit_power_law(self, horizon: str = "7d", x_min: float | None = None) -> dict:
        """Fit power law to the right tail of returns using Clauset et al. (2009) MLE.

        Args:
            horizon: Return horizon to analyze.
            x_min: Minimum value for power-law regime. If None, estimated via KS minimization.

        Returns:
            Dict with alpha (exponent), x_min, KS statistic, p-value estimate.
        """
        col = f"return_{horizon}"
        if col not in self.df.columns:
            return {"error": f"Column {col} not found"}

        # Use positive returns only for power-law fit
        positive = self.df[col].dropna()
        positive = positive[positive > 0].values

        if len(positive) < 50:
            return {"error": "Insufficient positive returns for power-law fit"}

        if x_min is None:
            x_min = self._estimate_x_min(positive)

        tail = positive[positive >= x_min]
        if len(tail) < 20:
            return {"error": f"Insufficient tail data above x_min={x_min}"}

        # MLE for power-law exponent: alpha = 1 + n / sum(ln(x/x_min))
        n = len(tail)
        alpha = 1 + n / np.sum(np.log(tail / x_min))
        alpha_se = (alpha - 1) / np.sqrt(n)

        # KS statistic
        ks_stat = self._ks_statistic(tail, alpha, x_min)

        return {
            "alpha": alpha,
            "alpha_se": alpha_se,
            "x_min": x_min,
            "n_tail": n,
            "n_total": len(positive),
            "tail_fraction": n / len(positive),
            "ks_statistic": ks_stat,
        }

    @staticmethod
    def _estimate_x_min(data: np.ndarray) -> float:
        """Estimate x_min by minimizing KS distance."""
        sorted_data = np.sort(data)
        candidates = sorted_data[int(len(sorted_data) * 0.1):int(len(sorted_data) * 0.9)]
        candidates = np.unique(candidates)

        if len(candidates) < 5:
            return np.median(data)

        # Sample candidates for efficiency
        if len(candidates) > 100:
            idx = np.linspace(0, len(candidates) - 1, 100, dtype=int)
            candidates = candidates[idx]

        best_ks = float("inf")
        best_xmin = candidates[0]

        for xm in candidates:
            tail = data[data >= xm]
            if len(tail) < 20:
                continue
            n = len(tail)
            alpha = 1 + n / np.sum(np.log(tail / xm))
            ks = ReturnDistributionAnalyzer._ks_statistic(tail, alpha, xm)
            if ks < best_ks:
                best_ks = ks
                best_xmin = xm

        return best_xmin

    @staticmethod
    def _ks_statistic(tail: np.ndarray, alpha: float, x_min: float) -> float:
        """Compute KS statistic between data and fitted power law."""
        sorted_tail = np.sort(tail)
        n = len(sorted_tail)
        empirical_cdf = np.arange(1, n + 1) / n
        theoretical_cdf = 1 - (x_min / sorted_tail) ** (alpha - 1)
        return np.max(np.abs(empirical_cdf - theoretical_cdf))

    def gini_coefficient(self, horizon: str = "7d") -> float:
        """Compute Gini coefficient of absolute returns."""
        col = f"return_{horizon}"
        if col not in self.df.columns:
            return float("nan")

        values = np.abs(self.df[col].dropna().values)
        if len(values) == 0:
            return float("nan")

        sorted_vals = np.sort(values)
        n = len(sorted_vals)
        index = np.arange(1, n + 1)
        return (2 * np.sum(index * sorted_vals) / (n * np.sum(sorted_vals))) - (n + 1) / n

    def value_decomposition(self, horizon: str = "7d") -> dict:
        """Decompose total value: sum of gains vs sum of losses."""
        col = f"return_{horizon}"
        if col not in self.df.columns:
            return {}

        series = self.df[col].dropna()
        gains = series[series > 0]
        losses = series[series < 0]

        return {
            "total_gain_sum": gains.sum(),
            "total_loss_sum": losses.sum(),
            "net": series.sum(),
            "gain_count": len(gains),
            "loss_count": len(losses),
            "avg_gain": gains.mean() if len(gains) > 0 else 0,
            "avg_loss": losses.mean() if len(losses) > 0 else 0,
            "median_gain": gains.median() if len(gains) > 0 else 0,
            "median_loss": losses.median() if len(losses) > 0 else 0,
        }
