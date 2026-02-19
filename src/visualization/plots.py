"""Publication-quality figures for meme coin analytics — WSJ white aesthetic.

Every figure uses the design system defined in theme.py: serif titles,
muted navy/steel/sage/tan palette, horizontal-only gridlines, left-aligned
titles, and source attribution at bottom-left.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

from src.visualization.theme import (
    apply_theme,
    style_axis,
    CHAIN_COLORS,
    WALLET_COLORS,
    WSJ_COLORS,
    PALETTE,
    FONT_SERIF,
    FONT_SANS,
    FONT_MONO,
    FONT_SIZE_TITLE,
    FONT_SIZE_SUBTITLE,
    FONT_SIZE_ANNOTATION,
    FONT_SIZE_SOURCE,
    FONT_SIZE_LEGEND,
    FIG_WIDE,
    FIG_SINGLE,
    FIG_SQUARE,
    FIG_TALL,
    FIG_DASHBOARD,
    DPI_PRINT,
)

# Ensure theme is applied
apply_theme()

OUTPUT_DIR = Path("data/results/figures")


def _save(fig: plt.Figure, name: str) -> Path:
    """Save figure as high-DPI PNG on white background."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{name}.png"
    fig.savefig(path, dpi=DPI_PRINT, facecolor="#FFFFFF", bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# F1: Daily Launch Volume — Stacked Area
# ---------------------------------------------------------------------------

def fig1_daily_launch_volume(daily_panel: pd.DataFrame) -> plt.Figure:
    """Stacked area chart of daily meme coin launches by chain.

    Navy/steel/sage/tan layers on pure white, left-aligned serif title.
    """
    fig, ax = plt.subplots(figsize=FIG_WIDE)

    pivot = daily_panel.pivot_table(
        index="created_date", columns="chain", values="launches", aggfunc="sum"
    ).fillna(0)

    chains = [c for c in CHAIN_COLORS if c in pivot.columns]
    colors = [CHAIN_COLORS[c] for c in chains]

    ax.stackplot(
        pivot.index,
        *[pivot[c] for c in chains],
        labels=[c.title() for c in chains],
        colors=colors,
        alpha=0.85,
        linewidth=0.5,
        edgecolor="#FFFFFF",
    )

    style_axis(
        ax,
        title="Daily Meme Coin Launches by Chain",
        subtitle="Aug 2025 – Feb 2026",
        ylabel="Tokens Launched",
    )

    ax.xaxis.set_major_locator(mticker.MaxNLocator(8))
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.legend(loc="upper left", ncol=len(chains))

    _save(fig, "fig1_daily_launch_volume")
    return fig


# ---------------------------------------------------------------------------
# F2: Return Density Plots — Overlaid
# ---------------------------------------------------------------------------

def fig2_return_density(returns_df: pd.DataFrame) -> plt.Figure:
    """Overlaid density plots for 1h, 24h, 7d returns on log-scale x-axis.

    Thin precise lines with shaded fills at 15% opacity.
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    horizons = [
        ("return_1h", "1 Hour", PALETTE[0]),
        ("return_24h", "24 Hours", PALETTE[1]),
        ("return_7d", "7 Days", PALETTE[2]),
    ]

    for ax, (col, label, color) in zip(axes, horizons):
        if col not in returns_df.columns:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    transform=ax.transAxes, color=WSJ_COLORS["medium_gray"])
            continue

        data = returns_df[col].dropna()
        data = data[(data > -1) & (data < 50)]

        if len(data) < 10:
            continue

        ax.hist(data, bins=120, density=True, alpha=0.15, color=color, edgecolor="none")
        # KDE overlay
        from scipy.stats import gaussian_kde
        try:
            kde = gaussian_kde(data, bw_method=0.15)
            x_grid = np.linspace(data.quantile(0.01), data.quantile(0.99), 500)
            ax.plot(x_grid, kde(x_grid), color=color, linewidth=1.5)
        except Exception:
            pass

        # Zero line
        ax.axvline(x=0, color=WSJ_COLORS["medium_gray"], linestyle="-", linewidth=0.6, alpha=0.5)

        # Median annotation
        med = data.median()
        ax.axvline(x=med, color=WSJ_COLORS["accent"], linestyle="--", linewidth=1.0, alpha=0.7)
        ax.text(
            med, ax.get_ylim()[1] * 0.92, f"  Median: {med:.0%}",
            fontfamily=FONT_MONO, fontsize=FONT_SIZE_ANNOTATION,
            color=WSJ_COLORS["accent"], va="top",
        )

        style_axis(ax, title=f"{label} Returns", xlabel="Return", source="")

    # Single source line for the whole figure
    axes[1].text(
        0.5, -0.18, "Source: Codex.io API  |  Returns clipped to [-100%, +5,000%]",
        transform=axes[1].transAxes,
        fontfamily=FONT_SANS, fontsize=FONT_SIZE_SOURCE,
        fontstyle="italic", color=WSJ_COLORS["medium_gray"], ha="center",
    )

    fig.subplots_adjust(wspace=0.3)
    _save(fig, "fig2_return_density")
    return fig


# ---------------------------------------------------------------------------
# F3: Power-Law Scatter (Log-Log)
# ---------------------------------------------------------------------------

def fig3_power_law(returns_df: pd.DataFrame, horizon: str = "7d") -> plt.Figure:
    """Log-log rank vs return scatter — small navy dots, muted-red fit line."""
    fig, ax = plt.subplots(figsize=FIG_TALL)

    col = f"return_{horizon}"
    if col not in returns_df.columns:
        return fig

    positive = returns_df[col].dropna()
    positive = positive[positive > 0].sort_values(ascending=False).values

    if len(positive) < 10:
        return fig

    rank = np.arange(1, len(positive) + 1)

    ax.scatter(
        np.log10(positive), np.log10(rank),
        s=2, alpha=0.4, color=WSJ_COLORS["primary"], rasterized=True,
    )

    # Fit power-law line to top decile
    tail_mask = positive >= np.percentile(positive, 90)
    if tail_mask.sum() > 5:
        tail_returns = positive[tail_mask]
        tail_rank = rank[:len(tail_returns)]
        z = np.polyfit(np.log10(tail_returns), np.log10(tail_rank), 1)
        x_fit = np.linspace(np.log10(tail_returns.min()), np.log10(tail_returns.max()), 100)
        ax.plot(x_fit, np.polyval(z, x_fit), color=WSJ_COLORS["accent"],
                linewidth=2, linestyle="--")

        # Annotation box
        alpha = -z[0]
        ax.text(
            0.97, 0.97,
            f"Tail exponent\n$\\alpha$ = {alpha:.2f}",
            transform=ax.transAxes, ha="right", va="top",
            fontfamily=FONT_SERIF, fontsize=FONT_SIZE_ANNOTATION + 1,
            color=WSJ_COLORS["accent"],
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF",
                      edgecolor=WSJ_COLORS["light_gray"], linewidth=0.5),
        )

    style_axis(
        ax,
        title=f"Power-Law Tail in {horizon} Returns",
        subtitle="Rank-size plot of positive returns",
        xlabel="log₁₀(Return)",
        ylabel="log₁₀(Rank)",
    )

    _save(fig, "fig3_power_law")
    return fig


# ---------------------------------------------------------------------------
# F4: Kaplan-Meier by Chain
# ---------------------------------------------------------------------------

def fig4_km_by_chain(km_fitters: dict) -> plt.Figure:
    """Step-function survival curves, one color per chain, 95% CI dashed."""
    fig, ax = plt.subplots(figsize=FIG_TALL)

    for name, kmf in km_fitters.items():
        color = CHAIN_COLORS.get(name.lower(), PALETTE[0])
        kmf.plot_survival_function(
            ax=ax, ci_show=True, color=color,
            linewidth=1.8, ci_alpha=0.08,
        )
        # Integrated legend: label at end of line
        timeline = kmf.survival_function_
        if not timeline.empty:
            last_t = timeline.index[-1]
            last_val = timeline.iloc[-1, 0]
            ax.text(
                last_t + 0.5, last_val, f"  {name.title()}",
                fontfamily=FONT_SANS, fontsize=FONT_SIZE_LEGEND,
                color=color, va="center",
            )

    # Remove default legend (we use integrated labels)
    legend = ax.get_legend()
    if legend:
        legend.remove()

    ax.set_xlim(0, 92)
    ax.set_ylim(0, 1.02)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0%}"))

    style_axis(
        ax,
        title="Meme Coin Survival by Chain",
        subtitle="Kaplan-Meier estimates with 95% confidence intervals",
        xlabel="Days Since Launch",
        ylabel="Survival Probability",
    )

    _save(fig, "fig4_km_by_chain")
    return fig


# ---------------------------------------------------------------------------
# F5: Kaplan-Meier by Launchpad
# ---------------------------------------------------------------------------

def fig5_km_by_launchpad(km_fitters: dict) -> plt.Figure:
    """Step-function survival curves by launchpad, integrated line labels."""
    fig, ax = plt.subplots(figsize=FIG_TALL)

    for idx, (name, kmf) in enumerate(km_fitters.items()):
        color = PALETTE[idx % len(PALETTE)]
        kmf.plot_survival_function(
            ax=ax, ci_show=True, color=color,
            linewidth=1.8, ci_alpha=0.08,
        )
        timeline = kmf.survival_function_
        if not timeline.empty:
            last_t = timeline.index[-1]
            last_val = timeline.iloc[-1, 0]
            ax.text(
                last_t + 0.5, last_val, f"  {name}",
                fontfamily=FONT_SANS, fontsize=FONT_SIZE_LEGEND,
                color=color, va="center",
            )

    legend = ax.get_legend()
    if legend:
        legend.remove()

    ax.set_xlim(0, 92)
    ax.set_ylim(0, 1.02)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0%}"))

    style_axis(
        ax,
        title="Meme Coin Survival by Launchpad",
        subtitle="Kaplan-Meier estimates with 95% confidence intervals",
        xlabel="Days Since Launch",
        ylabel="Survival Probability",
    )

    _save(fig, "fig5_km_by_launchpad")
    return fig


# ---------------------------------------------------------------------------
# F6: Survival Heatmap
# ---------------------------------------------------------------------------

def fig6_survival_heatmap(panel_df: pd.DataFrame) -> plt.Figure:
    """White-to-navy sequential heatmap: survival rate by sniper count x dev held %."""
    fig, ax = plt.subplots(figsize=FIG_SQUARE)

    if "sniper_count" not in panel_df.columns or "survived_7d" not in panel_df.columns:
        return fig

    df = panel_df.copy()
    df["sniper_bucket"] = pd.cut(
        df["sniper_count"],
        bins=[0, 1, 5, 10, 50, float("inf")],
        labels=["0", "1–5", "6–10", "11–50", "50+"],
        right=False,
    )
    df["dev_held_bucket"] = pd.cut(
        df["dev_held_pct"],
        bins=[0, 1, 5, 10, 25, 100],
        labels=["<1%", "1–5%", "5–10%", "10–25%", "25%+"],
        right=False,
    )

    pivot = df.pivot_table(
        index="dev_held_bucket", columns="sniper_bucket",
        values="survived_7d", aggfunc="mean",
    ) * 100

    # Custom white→navy colormap
    from matplotlib.colors import LinearSegmentedColormap
    wsj_cmap = LinearSegmentedColormap.from_list(
        "wsj_navy", ["#FFFFFF", "#C5D5E8", "#6B9AC4", "#2E6DA4", "#0A2240"]
    )

    im = ax.imshow(pivot.values, cmap=wsj_cmap, aspect="auto", vmin=0, vmax=100)

    # Cell annotations
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.iloc[i, j]
            if pd.notna(val):
                text_color = "#FFFFFF" if val > 50 else WSJ_COLORS["dark_gray"]
                ax.text(
                    j, i, f"{val:.1f}%",
                    ha="center", va="center",
                    fontfamily=FONT_MONO, fontsize=FONT_SIZE_ANNOTATION,
                    color=text_color, fontweight="bold",
                )

    ax.set_xticks(range(pivot.shape[1]))
    ax.set_xticklabels(pivot.columns, fontfamily=FONT_SANS)
    ax.set_yticks(range(pivot.shape[0]))
    ax.set_yticklabels(pivot.index, fontfamily=FONT_SANS)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, shrink=0.8, aspect=30, pad=0.02)
    cbar.set_label("7-Day Survival Rate (%)", fontfamily=FONT_SANS,
                    fontsize=FONT_SIZE_AXIS_LABEL, color=WSJ_COLORS["dark_gray"])
    cbar.outline.set_linewidth(0.5)
    cbar.outline.set_edgecolor(WSJ_COLORS["light_gray"])

    style_axis(
        ax,
        title="Survival Rate by Sniper Activity\nand Developer Holdings",
        xlabel="Sniper Count at Launch",
        ylabel="Developer Held %",
    )

    # Remove spines for heatmap (looks cleaner)
    for spine in ax.spines.values():
        spine.set_visible(False)

    _save(fig, "fig6_survival_heatmap")
    return fig


# Need this import at top level for F6
from src.visualization.theme import FONT_SIZE_AXIS_LABEL


# ---------------------------------------------------------------------------
# F7: ROC Curve
# ---------------------------------------------------------------------------

def fig7_roc_curves(sklearn_results: dict) -> plt.Figure:
    """Navy ROC line, light gray diagonal, AUC annotation in serif."""
    fig, ax = plt.subplots(figsize=FIG_SQUARE)

    roc = sklearn_results.get("roc_curve", {})
    fpr = roc.get("fpr", [])
    tpr = roc.get("tpr", [])
    auc_val = sklearn_results.get("auc", 0)

    # Reference line
    ax.plot([0, 1], [0, 1], color=WSJ_COLORS["light_gray"], linewidth=1.0, linestyle="-")

    if len(fpr) > 0:
        ax.plot(fpr, tpr, color=WSJ_COLORS["primary"], linewidth=2.2)

        # AUC annotation box
        ax.text(
            0.97, 0.05,
            f"AUC = {auc_val:.3f}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontfamily=FONT_SERIF, fontsize=14, fontweight="bold",
            color=WSJ_COLORS["primary"],
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF",
                      edgecolor=WSJ_COLORS["light_gray"], linewidth=0.5),
        )

    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_aspect("equal")

    style_axis(
        ax,
        title="7-Day Survival Prediction",
        subtitle="Receiver operating characteristic curve",
        xlabel="False Positive Rate",
        ylabel="True Positive Rate",
    )

    _save(fig, "fig7_roc_curves")
    return fig


# ---------------------------------------------------------------------------
# F8: Feature Importance — Horizontal Bar
# ---------------------------------------------------------------------------

def fig8_feature_importance(importance_df: pd.DataFrame) -> plt.Figure:
    """Horizontal bars sorted by magnitude, muted red for negative effects."""
    fig, ax = plt.subplots(figsize=FIG_SINGLE)

    if importance_df.empty:
        return fig

    df = importance_df.sort_values("odds_ratio").copy()

    # Color: sage green for OR > 1 (protective), muted red for OR < 1 (harmful)
    colors = [
        WSJ_COLORS["tertiary"] if x >= 1 else WSJ_COLORS["accent"]
        for x in df["odds_ratio"]
    ]

    bars = ax.barh(df["feature"], df["odds_ratio"], color=colors, height=0.6, edgecolor="none")

    # Reference line at OR = 1
    ax.axvline(x=1, color=WSJ_COLORS["dark_gray"], linestyle="-", linewidth=0.8, alpha=0.5)

    # Confidence interval whiskers if available
    if "ci_lower" in df.columns and "ci_upper" in df.columns:
        for idx, row in df.reset_index(drop=True).iterrows():
            y_pos = idx
            ax.plot(
                [row["ci_lower"], row["ci_upper"]], [y_pos, y_pos],
                color=WSJ_COLORS["dark_gray"], linewidth=1.0,
            )

    # Value labels
    for bar, val in zip(bars, df["odds_ratio"]):
        x_pos = bar.get_width() + 0.02
        ax.text(
            x_pos, bar.get_y() + bar.get_height() / 2,
            f"{val:.2f}",
            fontfamily=FONT_MONO, fontsize=FONT_SIZE_ANNOTATION,
            color=WSJ_COLORS["dark_gray"], va="center",
        )

    # Clean feature names
    labels = ax.get_yticklabels()
    for label in labels:
        label.set_fontfamily(FONT_SANS)
        label.set_fontsize(FONT_SIZE_ANNOTATION)

    style_axis(
        ax,
        title="What Predicts Meme Coin Survival?",
        subtitle="Odds ratios from logistic regression — values >1 increase survival odds",
        xlabel="Odds Ratio",
    )

    _save(fig, "fig8_feature_importance")
    return fig


# ---------------------------------------------------------------------------
# F9: Value Flow (Sankey Approximation)
# ---------------------------------------------------------------------------

def fig9_value_flow_sankey(sankey_data: dict) -> plt.Figure:
    """Horizontal bar chart showing value flows between wallet types."""
    fig, ax = plt.subplots(figsize=FIG_SINGLE)

    sources = sankey_data.get("sources", [])
    targets = sankey_data.get("targets", [])
    values = sankey_data.get("values", [])

    if not values:
        return fig

    # Aggregate flows
    flows = {}
    for s, t, v in zip(sources, targets, values):
        key = f"{s} → {t}"
        flows[key] = flows.get(key, 0) + v

    sorted_flows = sorted(flows.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
    labels = [f[0] for f in sorted_flows]
    vals = [f[1] for f in sorted_flows]

    # Color by direction: negative (outflow from retail) = red, positive = green
    colors = [WSJ_COLORS["accent"] if v > 0 else WSJ_COLORS["tertiary"] for v in vals]

    bars = ax.barh(labels, vals, color=colors, height=0.6, edgecolor="none")

    # Value annotations
    for bar, val in zip(bars, vals):
        x_pos = bar.get_width()
        ha = "left" if val >= 0 else "right"
        offset = abs(val) * 0.02
        ax.text(
            x_pos + (offset if val >= 0 else -offset),
            bar.get_y() + bar.get_height() / 2,
            f"${abs(val):,.0f}",
            fontfamily=FONT_MONO, fontsize=FONT_SIZE_ANNOTATION,
            color=WSJ_COLORS["dark_gray"], va="center", ha=ha,
        )

    ax.axvline(x=0, color=WSJ_COLORS["dark_gray"], linewidth=0.8)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${abs(x):,.0f}"))

    # Clean labels
    for label in ax.get_yticklabels():
        label.set_fontfamily(FONT_SANS)
        label.set_fontsize(FONT_SIZE_ANNOTATION)

    style_axis(
        ax,
        title="Where Does the Money Go?",
        subtitle="Net value transfer between wallet types",
        xlabel="USD Value",
    )

    _save(fig, "fig9_value_flow")
    return fig


# ---------------------------------------------------------------------------
# F10: Monthly Trends Dashboard — Small Multiples
# ---------------------------------------------------------------------------

def fig10_monthly_trends(daily_panel: pd.DataFrame, returns_df: pd.DataFrame) -> plt.Figure:
    """4-panel dashboard: launches, median return, survival rate, sniper %.

    Shared x-axis, individual y-axes, thin navy lines with gray CI fills.
    """
    fig, axes = plt.subplots(2, 2, figsize=FIG_DASHBOARD)

    # --- Panel 1: Monthly launches ---
    ax = axes[0, 0]
    if not daily_panel.empty and "created_date" in daily_panel.columns:
        monthly = daily_panel.copy()
        monthly["month"] = pd.to_datetime(monthly["created_date"]).dt.to_period("M").astype(str)
        launches = monthly.groupby("month")["launches"].sum()
        ax.bar(range(len(launches)), launches.values, color=WSJ_COLORS["primary"],
               width=0.7, edgecolor="none")
        ax.set_xticks(range(len(launches)))
        ax.set_xticklabels(launches.index, rotation=0, ha="center", fontsize=FONT_SIZE_ANNOTATION)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    style_axis(ax, title="Total Launches", source="")

    # --- Panel 2: Median 7-day return ---
    ax = axes[0, 1]
    if not returns_df.empty and "return_7d" in returns_df.columns and "created_at" in returns_df.columns:
        ret_df = returns_df.copy()
        ret_df["month"] = pd.to_datetime(ret_df["created_at"], unit="s", utc=True).dt.to_period("M").astype(str)
        med_ret = ret_df.groupby("month")["return_7d"].median()
        bar_colors = [WSJ_COLORS["tertiary"] if v >= 0 else WSJ_COLORS["accent"] for v in med_ret.values]
        ax.bar(range(len(med_ret)), med_ret.values * 100, color=bar_colors,
               width=0.7, edgecolor="none")
        ax.set_xticks(range(len(med_ret)))
        ax.set_xticklabels(med_ret.index, rotation=0, ha="center", fontsize=FONT_SIZE_ANNOTATION)
        ax.axhline(y=0, color=WSJ_COLORS["dark_gray"], linewidth=0.6)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    style_axis(ax, title="Median 7-Day Return", source="")

    # --- Panel 3: Monthly survival rate ---
    ax = axes[1, 0]
    if not daily_panel.empty and "avg_survival_7d" in daily_panel.columns:
        monthly = daily_panel.copy()
        monthly["month"] = pd.to_datetime(monthly["created_date"]).dt.to_period("M").astype(str)
        surv = monthly.groupby("month")["avg_survival_7d"].mean()
        ax.plot(range(len(surv)), surv.values * 100, color=WSJ_COLORS["primary"],
                linewidth=2, marker="o", markersize=5)
        ax.fill_between(range(len(surv)), 0, surv.values * 100,
                        alpha=0.08, color=WSJ_COLORS["primary"])
        ax.set_xticks(range(len(surv)))
        ax.set_xticklabels(surv.index, rotation=0, ha="center", fontsize=FONT_SIZE_ANNOTATION)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    else:
        ax.text(0.5, 0.5, "Computed from lifecycle data",
                ha="center", va="center", transform=ax.transAxes,
                color=WSJ_COLORS["medium_gray"], fontfamily=FONT_SANS,
                fontsize=FONT_SIZE_SUBTITLE)
    style_axis(ax, title="7-Day Survival Rate", source="")

    # --- Panel 4: Average sniper count ---
    ax = axes[1, 1]
    if not daily_panel.empty and "avg_sniper_count" in daily_panel.columns:
        monthly = daily_panel.copy()
        monthly["month"] = pd.to_datetime(monthly["created_date"]).dt.to_period("M").astype(str)
        sniper = monthly.groupby("month")["avg_sniper_count"].mean()
        ax.plot(range(len(sniper)), sniper.values, color=WSJ_COLORS["accent"],
                linewidth=2, marker="o", markersize=5)
        ax.fill_between(range(len(sniper)), 0, sniper.values,
                        alpha=0.08, color=WSJ_COLORS["accent"])
        ax.set_xticks(range(len(sniper)))
        ax.set_xticklabels(sniper.index, rotation=0, ha="center", fontsize=FONT_SIZE_ANNOTATION)
    else:
        ax.text(0.5, 0.5, "Computed from census data",
                ha="center", va="center", transform=ax.transAxes,
                color=WSJ_COLORS["medium_gray"], fontfamily=FONT_SANS,
                fontsize=FONT_SIZE_SUBTITLE)
    style_axis(ax, title="Avg. Sniper Count per Token", source="")

    # Bottom source line
    fig.text(
        0.02, 0.01, "Source: Codex.io API  |  Study period: Aug 2025 – Feb 2026",
        fontfamily=FONT_SANS, fontsize=FONT_SIZE_SOURCE,
        fontstyle="italic", color=WSJ_COLORS["medium_gray"],
    )

    fig.subplots_adjust(hspace=0.35, wspace=0.25)
    _save(fig, "fig10_monthly_trends")
    return fig
