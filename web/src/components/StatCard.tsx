"use client";

import { colors, formatNumber, formatPct, formatUSD } from "@/lib/theme";

interface StatCardProps {
  label: string;
  value: string | number;
  format?: "number" | "pct" | "usd" | "raw";
  subtitle?: string;
  trend?: "positive" | "negative" | "neutral";
}

export default function StatCard({ label, value, format = "raw", subtitle, trend }: StatCardProps) {
  let formatted: string;
  if (format === "number" && typeof value === "number") {
    formatted = formatNumber(value);
  } else if (format === "pct" && typeof value === "number") {
    formatted = formatPct(value);
  } else if (format === "usd" && typeof value === "number") {
    formatted = formatUSD(value);
  } else {
    formatted = String(value);
  }

  const trendColor =
    trend === "positive" ? colors.positive :
    trend === "negative" ? colors.negative :
    colors.darkGray;

  return (
    <div className="stat-card">
      <p
        className="text-xs uppercase tracking-widest mb-1"
        style={{ color: colors.mediumGray, fontFamily: "'Inter', sans-serif" }}
      >
        {label}
      </p>
      <p
        className="text-3xl font-bold num"
        style={{ color: trendColor, fontFamily: "Georgia, serif" }}
      >
        {formatted}
      </p>
      {subtitle && (
        <p className="text-xs mt-1" style={{ color: colors.mediumGray }}>
          {subtitle}
        </p>
      )}
    </div>
  );
}
