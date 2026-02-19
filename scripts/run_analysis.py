"""Phase 3: Run all econometric models and generate publication outputs."""

from __future__ import annotations

import logging
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.time_windows import STUDY_END_UNIX
from src.data.processors.lifecycle import classify_lifecycle, compute_survival_table
from src.data.processors.returns import compute_batch_returns
from src.data.processors.survival import prepare_survival_data
from src.data.processors.panel_builder import build_token_panel, build_daily_panel
from src.models.survival_analysis import SurvivalAnalyzer
from src.models.return_distribution import ReturnDistributionAnalyzer
from src.models.predictive import PredictiveModel
from src.models.panel import PanelRegression
from src.visualization import plots, tables

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_data() -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """Load collected data from parquet files."""
    census = pd.read_parquet("data/raw/census/full_census.parquet")
    sample = pd.read_parquet("data/processed/stratified_sample.parquet")

    # Load OHLCV data for sampled tokens
    from pathlib import Path
    ohlcv_dir = Path("data/raw/ohlcv")
    ohlcv_data = {}
    for addr in sample["address"].dropna().unique():
        daily_path = ohlcv_dir / f"{addr}_daily.parquet"
        hourly_path = ohlcv_dir / f"{addr}_hourly_first_48h.parquet"
        ohlcv_data[addr] = {
            "daily": pd.read_parquet(daily_path) if daily_path.exists() else pd.DataFrame(),
            "hourly_first_48h": pd.read_parquet(hourly_path) if hourly_path.exists() else pd.DataFrame(),
        }

    return census, ohlcv_data, sample


def main():
    logger.info("=== Loading data ===")
    census, ohlcv_data, sample = load_data()

    # Step 1: Lifecycle classification
    logger.info("=== Step 1: Lifecycle Classification ===")
    daily_ohlcv = {addr: data["daily"] for addr, data in ohlcv_data.items()}
    lifecycle_df = classify_lifecycle(census, daily_ohlcv)
    lifecycle_df.to_parquet("data/processed/lifecycle.parquet", index=False)
    survival_table = compute_survival_table(lifecycle_df)
    logger.info("Lifecycle: %d tokens classified", len(lifecycle_df))

    # Step 2: Returns
    logger.info("=== Step 2: Return Computation ===")
    returns_df = compute_batch_returns(ohlcv_data, sample)
    returns_df.to_parquet("data/processed/returns.parquet", index=False)
    logger.info("Returns: %d tokens computed", len(returns_df))

    # Step 3: Survival data
    logger.info("=== Step 3: Survival Data Preparation ===")
    survival_df = prepare_survival_data(lifecycle_df, STUDY_END_UNIX)
    survival_df.to_parquet("data/processed/survival.parquet", index=False)

    # Step 4: Panel dataset
    logger.info("=== Step 4: Panel Construction ===")
    panel_df = build_token_panel(lifecycle_df, returns_df, survival_df)
    panel_df.to_parquet("data/processed/panel.parquet", index=False)
    daily_panel = build_daily_panel(census)
    daily_panel.to_parquet("data/processed/daily_panel.parquet", index=False)

    # Step 5: Survival Analysis
    logger.info("=== Step 5: Survival Analysis ===")
    analyzer = SurvivalAnalyzer(survival_df)

    km_overall = analyzer.fit_kaplan_meier()
    km_chain = analyzer.fit_kaplan_meier(group_col="chain")
    logrank = analyzer.logrank_test("chain")
    logger.info("Log-rank test (chain): stat=%.2f, p=%.4f", logrank["test_statistic"], logrank["p_value"])

    cox = analyzer.fit_cox_ph()
    cox_summary = analyzer.cox_summary_table()
    c_index = analyzer.concordance_index()
    logger.info("Cox PH C-index: %.3f", c_index)

    aft = analyzer.fit_aft_weibull()
    aft_summary = aft.summary

    # Step 6: Return Distribution
    logger.info("=== Step 6: Return Distribution Analysis ===")
    ret_analyzer = ReturnDistributionAnalyzer(returns_df)
    dist_table = ret_analyzer.distribution_table()
    chain_dist = ret_analyzer.distribution_by_chain()
    power_law = ret_analyzer.fit_power_law()
    gini = ret_analyzer.gini_coefficient()
    logger.info("Power law alpha: %.2f, Gini: %.3f", power_law.get("alpha", 0), gini)

    # Step 7: Predictive Model
    logger.info("=== Step 7: Predictive Modeling ===")
    predictor = PredictiveModel(panel_df)
    logit_result = predictor.fit_logistic_statsmodels()
    logistic_summary = predictor.logistic_summary_table()
    sklearn_results = predictor.fit_sklearn_logistic()
    logger.info("Logistic AUC: %.3f", sklearn_results["auc"])

    # Step 8: Panel Regression
    logger.info("=== Step 8: Panel Regression ===")
    panel_reg = PanelRegression(panel_df)
    ols_7d = panel_reg.ols_cross_section(dependent="survived_7d")
    chain_comp = panel_reg.chain_comparison()
    lp_comp = panel_reg.launchpad_comparison()

    # Step 9: Generate Tables
    logger.info("=== Step 9: Generating Tables ===")
    tables.table1_summary_stats(survival_table, daily_panel)
    tables.table2_return_distribution(dist_table)
    tables.table3_returns_by_chain(chain_dist)
    tables.table4_cox_ph(cox_summary)
    tables.table5_aft(aft_summary)
    tables.table6_logistic(logistic_summary)
    tables.table7_model_performance(sklearn_results)
    tables.table9_panel_regression(ols_7d)
    tables.table10_monthly_trends(daily_panel)

    # Step 10: Generate Figures
    logger.info("=== Step 10: Generating Figures ===")
    plots.fig1_daily_launch_volume(daily_panel)
    plots.fig2_return_density(returns_df)
    plots.fig3_power_law(returns_df)
    plots.fig4_km_by_chain(km_chain)
    plots.fig6_survival_heatmap(panel_df)
    plots.fig7_roc_curves(sklearn_results)
    plots.fig8_feature_importance(sklearn_results.get("feature_importance", pd.DataFrame()))
    plots.fig10_monthly_trends(daily_panel, returns_df)

    logger.info("=== COMPLETE ===")
    logger.info("Tables saved to: data/results/tables/")
    logger.info("Figures saved to: data/results/figures/")


if __name__ == "__main__":
    main()
