"use client";

import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { colors, chainColors, fonts, formatCompact } from "@/lib/theme";
import type { DailyLaunchData } from "@/lib/types";

interface Props {
  data: DailyLaunchData[];
}

export default function LaunchVolumeChart({ data }: Props) {
  // Downsample for performance — show weekly averages
  const weekly = [];
  for (let i = 0; i < data.length; i += 7) {
    const chunk = data.slice(i, i + 7);
    const avg = (key: keyof DailyLaunchData) =>
      Math.round(chunk.reduce((s, d) => s + (d[key] as number), 0) / chunk.length);
    weekly.push({
      date: chunk[0].date,
      solana: avg("solana"),
      base: avg("base"),
      ethereum: avg("ethereum"),
      bsc: avg("bsc"),
    });
  }

  return (
    <div>
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={weekly} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
          <CartesianGrid stroke={colors.lightGray} strokeWidth={0.5} vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: colors.darkGray, fontSize: 10, fontFamily: fonts.sans }}
            axisLine={{ stroke: colors.darkGray, strokeWidth: 0.8 }}
            tickLine={false}
            tickFormatter={(v) => {
              const d = new Date(v);
              return d.toLocaleDateString("en-US", { month: "short" });
            }}
            interval={3}
          />
          <YAxis
            tick={{ fill: colors.darkGray, fontSize: 10, fontFamily: fonts.sans }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => formatCompact(v)}
          />
          <Tooltip
            contentStyle={{
              background: "#fff",
              border: `1px solid ${colors.lightGray}`,
              borderRadius: 4,
              fontFamily: fonts.sans,
              fontSize: 12,
            }}
            formatter={(value: number | undefined, name: string | undefined) => [formatCompact(value ?? 0), (name ?? "").charAt(0).toUpperCase() + (name ?? "").slice(1)]}
            labelFormatter={(label) => `Week of ${label}`}
          />
          <Area type="monotone" dataKey="bsc" stackId="1" fill={chainColors.bsc} stroke={chainColors.bsc} fillOpacity={0.85} />
          <Area type="monotone" dataKey="ethereum" stackId="1" fill={chainColors.ethereum} stroke={chainColors.ethereum} fillOpacity={0.85} />
          <Area type="monotone" dataKey="base" stackId="1" fill={chainColors.base} stroke={chainColors.base} fillOpacity={0.85} />
          <Area type="monotone" dataKey="solana" stackId="1" fill={chainColors.solana} stroke={chainColors.solana} fillOpacity={0.85} />
        </AreaChart>
      </ResponsiveContainer>
      <div className="flex gap-6 mt-3 justify-center">
        {Object.entries(chainColors).map(([chain, color]) => (
          <div key={chain} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: color }} />
            <span className="text-xs" style={{ color: colors.darkGray }}>{chain.charAt(0).toUpperCase() + chain.slice(1)}</span>
          </div>
        ))}
      </div>
      <p className="source">Source: Codex.io API &middot; Weekly averages</p>
    </div>
  );
}
