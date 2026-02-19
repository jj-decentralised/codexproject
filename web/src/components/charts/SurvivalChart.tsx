"use client";

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { colors, chainColors, fonts } from "@/lib/theme";
import type { SurvivalPoint } from "@/lib/types";

interface Props {
  data: SurvivalPoint[];
}

export default function SurvivalChart({ data }: Props) {
  const chains = Object.keys(chainColors);

  return (
    <div>
      <ResponsiveContainer width="100%" height={420}>
        <LineChart data={data} margin={{ top: 5, right: 80, bottom: 5, left: 10 }}>
          <CartesianGrid stroke={colors.lightGray} strokeWidth={0.5} vertical={false} />
          <XAxis
            dataKey="day"
            tick={{ fill: colors.darkGray, fontSize: 10, fontFamily: fonts.sans }}
            axisLine={{ stroke: colors.darkGray, strokeWidth: 0.8 }}
            tickLine={false}
            label={{ value: "Days Since Launch", position: "insideBottom", offset: -2, fill: colors.darkGray, fontSize: 11 }}
          />
          <YAxis
            tick={{ fill: colors.darkGray, fontSize: 10, fontFamily: fonts.sans }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${v.toFixed(0)}%`}
            domain={[0, 100]}
          />
          <Tooltip
            contentStyle={{
              background: "#fff",
              border: `1px solid ${colors.lightGray}`,
              borderRadius: 4,
              fontFamily: fonts.sans,
              fontSize: 12,
            }}
            formatter={(value: number | undefined, name: string | undefined) => [`${(value ?? 0).toFixed(1)}%`, (name ?? "").charAt(0).toUpperCase() + (name ?? "").slice(1)]}
            labelFormatter={(day) => `Day ${day}`}
          />
          {chains.map((chain) => (
            <Line
              key={chain}
              type="stepAfter"
              dataKey={chain}
              stroke={chainColors[chain]}
              strokeWidth={1.8}
              dot={false}
              activeDot={{ r: 3 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
      {/* Integrated line labels */}
      <div className="flex gap-6 mt-3 justify-center">
        {chains.map((chain) => (
          <div key={chain} className="flex items-center gap-1.5">
            <div className="w-4 h-0.5" style={{ backgroundColor: chainColors[chain] }} />
            <span className="text-xs" style={{ color: colors.darkGray }}>{chain.charAt(0).toUpperCase() + chain.slice(1)}</span>
          </div>
        ))}
      </div>
      <p className="source">Source: Codex.io API &middot; Kaplan-Meier estimates</p>
    </div>
  );
}
