"""Statistical test utilities: KS, chi-squared, normality, stationarity."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats as sp_stats


def ks_two_sample(x: np.ndarray, y: np.ndarray) -> dict:
    """Two-sample Kolmogorov-Smirnov test."""
    stat, pval = sp_stats.ks_2samp(x, y)
    return {"statistic": stat, "p_value": pval}


def chi_squared_independence(contingency_table: pd.DataFrame) -> dict:
    """Chi-squared test of independence."""
    chi2, p, dof, expected = sp_stats.chi2_contingency(contingency_table.values)
    return {"chi2": chi2, "p_value": p, "dof": dof}


def jarque_bera(x: np.ndarray) -> dict:
    """Jarque-Bera test for normality."""
    stat, pval = sp_stats.jarque_bera(x)
    return {"statistic": stat, "p_value": pval}


def shapiro_wilk(x: np.ndarray) -> dict:
    """Shapiro-Wilk test for normality (n < 5000)."""
    if len(x) > 5000:
        x = np.random.choice(x, 5000, replace=False)
    stat, pval = sp_stats.shapiro(x)
    return {"statistic": stat, "p_value": pval}


def mann_whitney_u(x: np.ndarray, y: np.ndarray) -> dict:
    """Mann-Whitney U test for comparing distributions."""
    stat, pval = sp_stats.mannwhitneyu(x, y, alternative="two-sided")
    return {"statistic": stat, "p_value": pval}


def kruskal_wallis(*groups: np.ndarray) -> dict:
    """Kruskal-Wallis H-test for comparing multiple groups."""
    stat, pval = sp_stats.kruskal(*groups)
    return {"statistic": stat, "p_value": pval}
