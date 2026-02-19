"""Publication-quality figures for meme coin analytics."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

# Publication style defaults
plt.rcParams.update({
    "figure.figsize": (10, 6),
    "figure.dpi": 150,
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.grid": True,
    "grid.alpha": 0.3,
})

CHAIN_COLORS = {
    "solana": "#9945FF",
    "base": "#0052FF",
    "ethereum": "#627EEA",
    "bsc": "#F0B90B",
}

OUTPUT_DIR = Path("data/results/figures")


def save_fig(fig: plt.Figure, name: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return path


def fig1_daily_launch_volume(daily_panel: pd.DataFrame) -> plt.Figure:
    """F1: Daily launch volume stacked area chart by chain."""
    fig, ax = plt.subplots(figsize=(14, 6))

    pivot = daily_panel.pivot_table(
        index="created_date", columns="chain", values="launches", aggfunc="sum"
    ).fillna(0)

    chains = [c for c in CHAIN_COLORS if c in pivot.columns]
    colors = [CHAIN_COLORS[c] for c in chains]

    ax.stackplot(pivot.index, *[pivot[c] for c in chains], labels=chains, colors=colors, alpha=0.8)
    ax.set_xlabel("Date")
    ax.set_ylabel("Tokens Launched")
    ax.set_title("Daily Meme Coin Launches by Chain (Aug 2025 - Feb 2026)")
    ax.legend(loc="upper left")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(12))
    plt.xticks(rotation=45)

    save_fig(fig, "fig1_daily_launch_volume")
    return fig


def fig2_return_density(returns_df: pd.DataFrame) -> plt.Figure:
    """F2: Return density plots at multiple horizons."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    horizons = [("return_1h", "1 Hour"), ("return_24h", "24 Hours"), ("return_7d", "7 Days")]

    for ax, (col, label) in zip(axes, horizons):
        if col not in returns_df.columns:
            continue
        data = returns_df[col].dropna()
        data = data[(data > -1) & (data < 50)]  # Clip for visualization

        sns.histplot(data, bins=100, ax=ax, stat="density", alpha=0.7, color="#4C72B0")
        ax.axvline(x=0, color="red", linestyle="--", alpha=0.5)
        ax.axvline(x=data.median(), color="green", linestyle="--", alpha=0.5, label=f"Median: {data.median():.2%}")
        ax.set_xlabel("Return")
        ax.set_title(f"{label} Returns")
        ax.legend()

    fig.suptitle("Meme Coin Return Distributions", fontsize=14)
    plt.tight_layout()

    save_fig(fig, "fig2_return_density")
    return fig


def fig3_power_law(returns_df: pd.DataFrame, horizon: str = "7d") -> plt.Figure:
    """F3: Log-log rank-return plot showing power-law tail."""
    fig, ax = plt.subplots(figsize=(10, 7))

    col = f"return_{horizon}"
    if col not in returns_df.columns:
        return fig

    positive = returns_df[col].dropna()
    positive = positive[positive > 0].sort_values(ascending=False).values

    if len(positive) < 10:
        return fig

    rank = np.arange(1, len(positive) + 1)

    ax.scatter(np.log10(positive), np.log10(rank), s=2, alpha=0.5, color="#4C72B0")
    ax.set_xlabel("log10(Return)")
    ax.set_ylabel("log10(Rank)")
    ax.set_title(f"Power-Law Analysis: {horizon} Returns (Rank-Size Plot)")

    # Fit line to tail
    tail_mask = positive >= np.percentile(positive, 90)
    if tail_mask.sum() > 5:
        tail_returns = positive[tail_mask]
        tail_rank = rank[:len(tail_returns)]
        z = np.polyfit(np.log10(tail_returns), np.log10(tail_rank), 1)
        x_fit = np.linspace(np.log10(tail_returns.min()), np.log10(tail_returns.max()), 100)
        ax.plot(x_fit, np.polyval(z, x_fit), "r--", linewidth=2, label=f"slope = {z[0]:.2f}")
        ax.legend()

    save_fig(fig, "fig3_power_law")
    return fig


def fig4_km_by_chain(km_fitters: dict) -> plt.Figure:
    """F4: Kaplan-Meier survival curves stratified by chain."""
    fig, ax = plt.subplots(figsize=(10, 7))

    for name, kmf in km_fitters.items():
        color = CHAIN_COLORS.get(name.lower(), None)
        kmf.plot_survival_function(ax=ax, ci_show=True, color=color)

    ax.set_xlabel("Days Since Launch")
    ax.set_ylabel("Survival Probability")
    ax.set_title("Meme Coin Survival Curves by Chain")
    ax.set_xlim(0, 90)
    ax.legend(title="Chain")

    save_fig(fig, "fig4_km_by_chain")
    return fig


def fig5_km_by_launchpad(km_fitters: dict) -> plt.Figure:
    """F5: Kaplan-Meier survival curves stratified by launchpad."""
    fig, ax = plt.subplots(figsize=(10, 7))

    for name, kmf in km_fitters.items():
        kmf.plot_survival_function(ax=ax, ci_show=True)

    ax.set_xlabel("Days Since Launch")
    ax.set_ylabel("Survival Probability")
    ax.set_title("Meme Coin Survival Curves by Launchpad")
    ax.set_xlim(0, 90)
    ax.legend(title="Launchpad")

    save_fig(fig, "fig5_km_by_launchpad")
    return fig


def fig6_survival_heatmap(panel_df: pd.DataFrame) -> plt.Figure:
    """F6: Heatmap of survival rate by sniper count x dev held percentage."""
    fig, ax = plt.subplots(figsize=(10, 8))

    if "sniper_count" not in panel_df.columns or "survived_7d" not in panel_df.columns:
        return fig

    df = panel_df.copy()
    df["sniper_bucket"] = pd.cut(df["sniper_count"], bins=[0, 1, 5, 10, 50, float("inf")],
                                  labels=["0", "1-5", "6-10", "11-50", "50+"], right=False)
    df["dev_held_bucket"] = pd.cut(df["dev_held_pct"], bins=[0, 1, 5, 10, 25, 100],
                                    labels=["<1%", "1-5%", "5-10%", "10-25%", "25%+"], right=False)

    pivot = df.pivot_table(index="dev_held_bucket", columns="sniper_bucket",
                           values="survived_7d", aggfunc="mean") * 100

    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdYlGn", ax=ax,
                cbar_kws={"label": "7-Day Survival Rate (%)"})
    ax.set_xlabel("Sniper Count")
    ax.set_ylabel("Dev Held %")
    ax.set_title("7-Day Survival Rate by Sniper Activity and Dev Holdings")

    save_fig(fig, "fig6_survival_heatmap")
    return fig


def fig7_roc_curves(sklearn_results: dict) -> plt.Figure:
    """F7: ROC curves for survival prediction model."""
    fig, ax = plt.subplots(figsize=(8, 8))

    roc = sklearn_results.get("roc_curve", {})
    fpr = roc.get("fpr", [])
    tpr = roc.get("tpr", [])
    auc = sklearn_results.get("auc", 0)

    if len(fpr) > 0:
        ax.plot(fpr, tpr, color="#4C72B0", linewidth=2, label=f"Logistic (AUC = {auc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve: 7-Day Survival Prediction")
    ax.legend()
    ax.set_aspect("equal")

    save_fig(fig, "fig7_roc_curves")
    return fig


def fig8_feature_importance(importance_df: pd.DataFrame) -> plt.Figure:
    """F8: Feature importance bar chart with confidence intervals."""
    fig, ax = plt.subplots(figsize=(10, 7))

    if importance_df.empty:
        return fig

    df = importance_df.sort_values("odds_ratio")

    colors = ["#D64541" if x < 1 else "#27AE60" for x in df["odds_ratio"]]
    ax.barh(df["feature"], df["odds_ratio"], color=colors, alpha=0.8)
    ax.axvline(x=1, color="black", linestyle="--", alpha=0.5)
    ax.set_xlabel("Odds Ratio")
    ax.set_title("Feature Importance: Odds Ratios for 7-Day Survival")

    save_fig(fig, "fig8_feature_importance")
    return fig


def fig9_value_flow_sankey(sankey_data: dict) -> plt.Figure:
    """F9: Simplified value flow bar chart (Sankey approximation)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    sources = sankey_data.get("sources", [])
    targets = sankey_data.get("targets", [])
    values = sankey_data.get("values", [])

    if not values:
        return fig

    # Aggregate flows
    flows = {}
    for s, t, v in zip(sources, targets, values):
        key = f"{s} -> {t}"
        flows[key] = flows.get(key, 0) + v

    sorted_flows = sorted(flows.items(), key=lambda x: x[1], reverse=True)[:10]
    labels = [f[0] for f in sorted_flows]
    vals = [f[1] for f in sorted_flows]

    ax.barh(labels, vals, color="#E74C3C", alpha=0.8)
    ax.set_xlabel("USD Value Flow")
    ax.set_title("Value Transfer: Who Pays Whom?")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    save_fig(fig, "fig9_value_flow")
    return fig


def fig10_monthly_trends(daily_panel: pd.DataFrame, returns_df: pd.DataFrame) -> plt.Figure:
    """F10: Monthly trends dashboard (4-panel)."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: Monthly launches
    if not daily_panel.empty and "created_date" in daily_panel.columns:
        monthly = daily_panel.copy()
        monthly["month"] = pd.to_datetime(monthly["created_date"]).dt.to_period("M")
        launches = monthly.groupby("month")["launches"].sum()
        axes[0, 0].bar(launches.index.astype(str), launches.values, color="#4C72B0")
        axes[0, 0].set_title("Monthly Launches")
        axes[0, 0].tick_params(axis="x", rotation=45)

    # Panel 2: Monthly median return
    if not returns_df.empty and "return_7d" in returns_df.columns and "created_at" in returns_df.columns:
        ret_df = returns_df.copy()
        ret_df["month"] = pd.to_datetime(ret_df["created_at"], unit="s", utc=True).dt.to_period("M")
        med_ret = ret_df.groupby("month")["return_7d"].median()
        axes[0, 1].bar(med_ret.index.astype(str), med_ret.values * 100, color="#27AE60")
        axes[0, 1].set_title("Median 7-Day Return (%)")
        axes[0, 1].tick_params(axis="x", rotation=45)

    # Panel 3: Survival rate trend (placeholder)
    axes[1, 0].set_title("Monthly 7-Day Survival Rate")
    axes[1, 0].text(0.5, 0.5, "Computed from lifecycle data", ha="center", va="center",
                    transform=axes[1, 0].transAxes)

    # Panel 4: Sniper % trend (placeholder)
    axes[1, 1].set_title("Monthly Avg Sniper Count")
    axes[1, 1].text(0.5, 0.5, "Computed from census data", ha="center", va="center",
                    transform=axes[1, 1].transAxes)

    fig.suptitle("Monthly Trends Dashboard", fontsize=14)
    plt.tight_layout()

    save_fig(fig, "fig10_monthly_trends")
    return fig
