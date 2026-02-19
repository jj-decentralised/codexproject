/**
 * WSJ-inspired design system for meme coin analytics dashboard.
 *
 * Plain white aesthetic, serif titles, muted palette, precise lines.
 */

export const colors = {
  primary: "#0A2240",      // Deep navy
  secondary: "#4A7FB5",    // Steel blue
  accent: "#C4403D",       // Muted red
  tertiary: "#7B9E87",     // Sage green
  quaternary: "#D4A574",   // Warm tan
  quinary: "#8B6C5C",      // Warm brown

  lightGray: "#E8E8E8",    // Gridlines
  mediumGray: "#999999",   // Secondary text
  darkGray: "#333333",     // Primary text
  textBlack: "#1A1A1A",    // Titles
  background: "#FFFFFF",   // Pure white
  panelBg: "#FAFAFA",      // Alt rows

  negative: "#C4403D",     // Losses
  positive: "#7B9E87",     // Gains
} as const;

export const palette = [
  colors.primary,
  colors.secondary,
  colors.accent,
  colors.tertiary,
  colors.quaternary,
  colors.quinary,
];

export const chainColors: Record<string, string> = {
  solana: colors.primary,
  base: colors.secondary,
  ethereum: colors.tertiary,
  bsc: colors.quaternary,
};

export const walletColors: Record<string, string> = {
  sniper: colors.accent,
  bundler: colors.quaternary,
  insider: colors.quinary,
  dev: colors.secondary,
  retail: colors.primary,
};

export const fonts = {
  serif: "'Georgia', 'Merriweather', serif",
  sans: "'Inter', 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
  mono: "'IBM Plex Mono', 'JetBrains Mono', 'Menlo', monospace",
} as const;

/** Recharts common axis props for WSJ style */
export const axisStyle = {
  tick: { fill: colors.darkGray, fontSize: 11, fontFamily: fonts.sans },
  axisLine: { stroke: colors.darkGray, strokeWidth: 0.8 },
  tickLine: { stroke: colors.darkGray, strokeWidth: 0.5 },
};

/** Recharts grid props */
export const gridStyle = {
  stroke: colors.lightGray,
  strokeWidth: 0.5,
  horizontal: true,
  vertical: false,
};

/** Format large numbers with commas */
export function formatNumber(n: number): string {
  return new Intl.NumberFormat("en-US").format(n);
}

/** Format as compact number (1.2K, 3.4M) */
export function formatCompact(n: number): string {
  return new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(n);
}

/** Format as percentage */
export function formatPct(n: number, decimals = 1): string {
  return `${(n * 100).toFixed(decimals)}%`;
}

/** Format as USD */
export function formatUSD(n: number): string {
  if (n < 0) return `-$${formatNumber(Math.round(Math.abs(n)))}`;
  return `$${formatNumber(Math.round(n))}`;
}
