"""Publication-quality tables for meme coin analytics."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from tabulate import tabulate

OUTPUT_DIR = Path("data/results/tables")


def save_table(content: str, name: str, fmt: str = "md") -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ext = "md" if fmt == "md" else "tex"
    path = OUTPUT_DIR / f"{name}.{ext}"
    path.write_text(content)
    return path


def table1_summary_stats(survival_table: pd.DataFrame, daily_panel: pd.DataFrame) -> str:
    """T1: Summary statistics — launches/day by chain, totals, survival rates."""
    lines = ["# Table 1: Meme Coin Market Summary (Aug 2025 - Feb 2026)", ""]

    if not survival_table.empty:
        md = tabulate(survival_table, headers="keys", tablefmt="pipe", floatfmt=".1f", showindex=False)
        lines.append(md)

    content = "\n".join(lines)
    save_table(content, "table1_summary_stats")
    return content


def table2_return_distribution(dist_table: pd.DataFrame) -> str:
    """T2: Return distribution by horizon."""
    lines = ["# Table 2: Return Distribution by Horizon", ""]

    if not dist_table.empty:
        display_cols = ["horizon", "n", "mean", "median", "p10", "p25", "p75", "p90", "p99",
                        "pct_positive", "pct_10x", "pct_100x"]
        available = [c for c in display_cols if c in dist_table.columns]
        formatted = dist_table[available].copy()

        for col in ["mean", "median", "p10", "p25", "p75", "p90", "p99"]:
            if col in formatted.columns:
                formatted[col] = formatted[col].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "")

        for col in ["pct_positive", "pct_10x", "pct_100x"]:
            if col in formatted.columns:
                formatted[col] = formatted[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")

        md = tabulate(formatted, headers="keys", tablefmt="pipe", showindex=False)
        lines.append(md)

    content = "\n".join(lines)
    save_table(content, "table2_return_distribution")
    return content


def table3_returns_by_chain(chain_dist: pd.DataFrame) -> str:
    """T3: Return percentiles by chain."""
    lines = ["# Table 3: 7-Day Returns by Chain", ""]

    if not chain_dist.empty:
        md = tabulate(chain_dist, headers="keys", tablefmt="pipe", floatfmt=".2f", showindex=False)
        lines.append(md)

    content = "\n".join(lines)
    save_table(content, "table3_returns_by_chain")
    return content


def table4_cox_ph(cox_summary: pd.DataFrame) -> str:
    """T4: Cox Proportional Hazards regression results."""
    lines = ["# Table 4: Cox Proportional Hazards Model — Hazard Ratios", ""]

    if not cox_summary.empty:
        md = tabulate(cox_summary.reset_index(), headers="keys", tablefmt="pipe",
                      floatfmt=".3f", showindex=False)
        lines.append(md)

    content = "\n".join(lines)
    save_table(content, "table4_cox_ph")
    return content


def table5_aft(aft_summary: pd.DataFrame) -> str:
    """T5: Accelerated Failure Time model results."""
    lines = ["# Table 5: Weibull AFT Model — Acceleration Factors", ""]

    if not aft_summary.empty:
        md = tabulate(aft_summary.reset_index(), headers="keys", tablefmt="pipe",
                      floatfmt=".3f", showindex=False)
        lines.append(md)

    content = "\n".join(lines)
    save_table(content, "table5_aft")
    return content


def table6_logistic(logistic_summary: pd.DataFrame) -> str:
    """T6: Logistic regression odds ratios."""
    lines = ["# Table 6: Logistic Regression — P(Survive 7 Days)", ""]

    if not logistic_summary.empty:
        md = tabulate(logistic_summary.reset_index(), headers="keys", tablefmt="pipe",
                      floatfmt=".3f", showindex=False)
        lines.append(md)

    content = "\n".join(lines)
    save_table(content, "table6_logistic")
    return content


def table7_model_performance(sklearn_results: dict) -> str:
    """T7: Predictive model performance metrics."""
    lines = ["# Table 7: Predictive Model Performance", ""]

    report = sklearn_results.get("classification_report", {})
    auc = sklearn_results.get("auc", 0)

    lines.append(f"**AUC-ROC:** {auc:.3f}")
    lines.append(f"**Train N:** {sklearn_results.get('n_train', 0)}")
    lines.append(f"**Test N:** {sklearn_results.get('n_test', 0)}")
    lines.append("")

    if report:
        rows = []
        for label, metrics in report.items():
            if isinstance(metrics, dict):
                rows.append({
                    "class": label,
                    "precision": metrics.get("precision", 0),
                    "recall": metrics.get("recall", 0),
                    "f1-score": metrics.get("f1-score", 0),
                    "support": metrics.get("support", 0),
                })
        if rows:
            df = pd.DataFrame(rows)
            md = tabulate(df, headers="keys", tablefmt="pipe", floatfmt=".3f", showindex=False)
            lines.append(md)

    content = "\n".join(lines)
    save_table(content, "table7_model_performance")
    return content


def table8_pnl_by_wallet_type(decomp_table: pd.DataFrame) -> str:
    """T8: PnL by wallet type."""
    lines = ["# Table 8: Profit & Loss by Wallet Type", ""]

    if not decomp_table.empty:
        display = decomp_table.copy()
        for col in ["total_bought_usd", "total_sold_usd", "total_pnl", "mean_pnl", "median_pnl"]:
            if col in display.columns:
                display[col] = display[col].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "")

        md = tabulate(display, headers="keys", tablefmt="pipe", showindex=False)
        lines.append(md)

    content = "\n".join(lines)
    save_table(content, "table8_pnl_by_wallet_type")
    return content


def table9_panel_regression(ols_result) -> str:
    """T9: Panel regression results."""
    lines = ["# Table 9: Cross-Sectional Regression — Chain & Launchpad Effects", ""]

    if ols_result is not None:
        summary = ols_result.summary2().tables[1]
        md = tabulate(summary.reset_index(), headers="keys", tablefmt="pipe",
                      floatfmt=".4f", showindex=False)
        lines.append(md)
        lines.append("")
        lines.append(f"**R-squared:** {ols_result.rsquared:.4f}")
        lines.append(f"**N:** {int(ols_result.nobs)}")

    content = "\n".join(lines)
    save_table(content, "table9_panel_regression")
    return content


def table10_monthly_trends(daily_panel: pd.DataFrame) -> str:
    """T10: Monthly trends."""
    lines = ["# Table 10: Monthly Trends", ""]

    if not daily_panel.empty and "created_date" in daily_panel.columns:
        monthly = daily_panel.copy()
        monthly["month"] = pd.to_datetime(monthly["created_date"]).dt.to_period("M").astype(str)

        agg = monthly.groupby("month").agg(
            total_launches=("launches", "sum"),
            avg_daily_launches=("launches", "mean"),
            total_volume=("total_volume", "sum"),
            avg_sniper_count=("avg_sniper_count", "mean"),
        ).reset_index()

        md = tabulate(agg, headers="keys", tablefmt="pipe", floatfmt=".1f", showindex=False)
        lines.append(md)

    content = "\n".join(lines)
    save_table(content, "table10_monthly_trends")
    return content
