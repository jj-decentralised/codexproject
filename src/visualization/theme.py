"""WSJ-inspired design system for publication-quality meme coin analytics.

Plain white aesthetic with serif titles, precise lines, and muted colors.
All figures and tables in this project use this theme for visual consistency.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

# ---------------------------------------------------------------------------
# Color Palette
# ---------------------------------------------------------------------------

WSJ_COLORS = {
    "primary": "#0A2240",       # Deep navy — main data series
    "secondary": "#4A7FB5",     # Steel blue — comparison / second series
    "accent": "#C4403D",        # Muted red — danger, negative, highlight
    "tertiary": "#7B9E87",      # Sage green — positive, survival
    "quaternary": "#D4A574",    # Warm tan — neutral, fourth series
    "quinary": "#8B6C5C",       # Warm brown — fifth series
    "light_gray": "#E8E8E8",    # Gridlines
    "medium_gray": "#999999",   # Secondary text, tick marks
    "dark_gray": "#333333",     # Primary text, spines
    "text_black": "#1A1A1A",    # Titles
    "background": "#FFFFFF",    # Pure white
    "panel_bg": "#FAFAFA",      # Subtle off-white (alt row)
    "negative": "#C4403D",      # Same as accent — losses
    "positive": "#7B9E87",      # Same as tertiary — gains
}

# Ordered palette for multi-series charts
PALETTE = [
    WSJ_COLORS["primary"],
    WSJ_COLORS["secondary"],
    WSJ_COLORS["accent"],
    WSJ_COLORS["tertiary"],
    WSJ_COLORS["quaternary"],
    WSJ_COLORS["quinary"],
]

# Chain-specific colors (muted, distinguishable)
CHAIN_COLORS = {
    "solana": "#0A2240",        # Deep navy
    "base": "#4A7FB5",          # Steel blue
    "ethereum": "#7B9E87",      # Sage green
    "bsc": "#D4A574",           # Warm tan
}

# Wallet type colors
WALLET_COLORS = {
    "sniper": "#C4403D",        # Muted red
    "bundler": "#D4A574",       # Warm tan
    "insider": "#8B6C5C",       # Warm brown
    "dev": "#4A7FB5",           # Steel blue
    "retail": "#0A2240",        # Deep navy
}

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------

# Preferred fonts with system fallbacks
FONT_SERIF = "Georgia"          # Title font (Merriweather if available)
FONT_SANS = "Helvetica Neue"    # Labels, annotations (Inter if available)
FONT_MONO = "Menlo"             # Data labels (IBM Plex Mono if available)

# Try to use better fonts if installed
for name in ["Merriweather", "Playfair Display", "Georgia"]:
    if any(name.lower() in f.name.lower() for f in fm.fontManager.ttflist):
        FONT_SERIF = name
        break

for name in ["Inter", "Helvetica Neue", "Helvetica", "Arial"]:
    if any(name.lower() in f.name.lower() for f in fm.fontManager.ttflist):
        FONT_SANS = name
        break

for name in ["IBM Plex Mono", "JetBrains Mono", "Menlo", "Consolas"]:
    if any(name.lower() in f.name.lower() for f in fm.fontManager.ttflist):
        FONT_MONO = name
        break

# Font sizes
FONT_SIZE_TITLE = 18
FONT_SIZE_SUBTITLE = 12
FONT_SIZE_AXIS_LABEL = 11
FONT_SIZE_TICK = 10
FONT_SIZE_ANNOTATION = 9
FONT_SIZE_SOURCE = 8
FONT_SIZE_LEGEND = 9

# ---------------------------------------------------------------------------
# Figure Dimensions
# ---------------------------------------------------------------------------

FIG_SINGLE = (7, 4.5)          # Standard single chart
FIG_WIDE = (10, 5)             # Time series, dashboards
FIG_SQUARE = (6, 6)            # Scatter, heatmaps
FIG_TALL = (7, 7)              # Survival curves, ROC
FIG_DASHBOARD = (14, 9)        # Multi-panel layouts
DPI_SCREEN = 150
DPI_PRINT = 300

# ---------------------------------------------------------------------------
# matplotlib rcParams
# ---------------------------------------------------------------------------

WSJ_RC = {
    # Background
    "figure.facecolor": WSJ_COLORS["background"],
    "axes.facecolor": WSJ_COLORS["background"],
    "savefig.facecolor": WSJ_COLORS["background"],

    # Spines — left and bottom only
    "axes.edgecolor": WSJ_COLORS["dark_gray"],
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,

    # Grid — horizontal only, subtle
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.color": WSJ_COLORS["light_gray"],
    "grid.linewidth": 0.5,
    "grid.linestyle": "-",

    # Ticks
    "xtick.color": WSJ_COLORS["dark_gray"],
    "ytick.color": WSJ_COLORS["dark_gray"],
    "xtick.labelsize": FONT_SIZE_TICK,
    "ytick.labelsize": FONT_SIZE_TICK,
    "xtick.major.size": 4,
    "ytick.major.size": 0,      # No y-tick marks (grid is enough)
    "xtick.major.width": 0.8,
    "xtick.direction": "out",

    # Text
    "text.color": WSJ_COLORS["text_black"],
    "font.family": "sans-serif",
    "font.sans-serif": [FONT_SANS, "Helvetica", "Arial", "sans-serif"],
    "font.size": FONT_SIZE_AXIS_LABEL,

    # Legend — no frame, clean
    "legend.frameon": False,
    "legend.fontsize": FONT_SIZE_LEGEND,
    "legend.loc": "upper right",

    # Figure
    "figure.dpi": DPI_SCREEN,
    "savefig.dpi": DPI_PRINT,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.2,

    # Lines
    "lines.linewidth": 1.8,
    "lines.markersize": 4,

    # Patches (bars, etc)
    "patch.edgecolor": WSJ_COLORS["background"],
    "patch.linewidth": 0.5,
}


def apply_theme():
    """Apply the WSJ theme globally to all matplotlib figures."""
    plt.rcParams.update(WSJ_RC)


def _set_wsj_title(ax: plt.Axes, title: str, subtitle: str | None = None):
    """Left-aligned serif title with optional subtitle."""
    ax.set_title(
        title,
        fontfamily=FONT_SERIF,
        fontsize=FONT_SIZE_TITLE,
        fontweight="bold",
        color=WSJ_COLORS["text_black"],
        loc="left",
        pad=12,
    )
    if subtitle:
        ax.text(
            0, 1.02, subtitle,
            transform=ax.transAxes,
            fontfamily=FONT_SANS,
            fontsize=FONT_SIZE_SUBTITLE,
            color=WSJ_COLORS["medium_gray"],
            ha="left", va="bottom",
        )


def _set_wsj_source(ax: plt.Axes, source: str = "Source: Codex.io API"):
    """Bottom-left source line in small gray italic."""
    ax.text(
        0, -0.12, source,
        transform=ax.transAxes,
        fontfamily=FONT_SANS,
        fontsize=FONT_SIZE_SOURCE,
        fontstyle="italic",
        color=WSJ_COLORS["medium_gray"],
        ha="left", va="top",
    )


def _format_axis(ax: plt.Axes, xlabel: str = "", ylabel: str = ""):
    """Apply WSJ axis formatting."""
    if xlabel:
        ax.set_xlabel(
            xlabel,
            fontfamily=FONT_SANS,
            fontsize=FONT_SIZE_AXIS_LABEL,
            color=WSJ_COLORS["dark_gray"],
        )
    else:
        ax.set_xlabel("")

    if ylabel:
        ax.set_ylabel(
            ylabel,
            fontfamily=FONT_SANS,
            fontsize=FONT_SIZE_AXIS_LABEL,
            color=WSJ_COLORS["dark_gray"],
        )
    else:
        ax.set_ylabel("")


def _clean_legend(ax: plt.Axes, loc: str = "upper right"):
    """Restyle legend with no frame, WSJ fonts."""
    legend = ax.get_legend()
    if legend:
        legend.set_frame_on(False)
        for text in legend.get_texts():
            text.set_fontfamily(FONT_SANS)
            text.set_fontsize(FONT_SIZE_LEGEND)
            text.set_color(WSJ_COLORS["dark_gray"])


def style_axis(
    ax: plt.Axes,
    title: str = "",
    subtitle: str | None = None,
    xlabel: str = "",
    ylabel: str = "",
    source: str = "Source: Codex.io API",
):
    """One-call convenience to fully style an axis in WSJ style."""
    if title:
        _set_wsj_title(ax, title, subtitle)
    _format_axis(ax, xlabel, ylabel)
    if source:
        _set_wsj_source(ax, source)
    _clean_legend(ax)


# ---------------------------------------------------------------------------
# Table Styling Constants
# ---------------------------------------------------------------------------

TABLE_HEADER_BORDER = "2pt solid #333333"
TABLE_SUBHEADER_BORDER = "1pt solid #999999"
TABLE_BOTTOM_BORDER = "1pt solid #333333"
TABLE_ALT_ROW_BG = WSJ_COLORS["panel_bg"]
TABLE_NUMBER_COLOR = WSJ_COLORS["dark_gray"]
TABLE_NEGATIVE_COLOR = WSJ_COLORS["negative"]
TABLE_SIGNIFICANCE = {0.01: "***", 0.05: "**", 0.10: "*"}


def format_number(x, fmt: str = ",.0f", prefix: str = "", suffix: str = "") -> str:
    """Format a number with WSJ conventions."""
    if pd.isna(x):
        return ""
    return f"{prefix}{x:{fmt}}{suffix}"


def format_pct(x, decimals: int = 1) -> str:
    """Format as percentage."""
    if pd.isna(x):
        return ""
    return f"{x:.{decimals}f}%"


def format_currency(x, decimals: int = 0) -> str:
    """Format as USD with comma separators."""
    if pd.isna(x):
        return ""
    if x < 0:
        return f"-${abs(x):,.{decimals}f}"
    return f"${x:,.{decimals}f}"


def significance_stars(p_value: float) -> str:
    """Return significance stars based on p-value."""
    for threshold, stars in TABLE_SIGNIFICANCE.items():
        if p_value <= threshold:
            return stars
    return ""


# Need pandas for format helpers
import pandas as pd

# Apply theme on import
apply_theme()
