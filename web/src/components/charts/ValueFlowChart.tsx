"use client";

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { colors, fonts, formatUSD } from "@/lib/theme";
import type { ValueFlow } from "@/lib/types";

interface Props {
  data: ValueFlow[];
}

export default function ValueFlowChart({ data }: Props) {
  const chartData = data
    .sort((a, b) => b.value - a.value)
    .map((d) => ({
      label: `${d.source} \u2192 ${d.target}`,
      value: d.value,
    }));

  return (
    <div>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 80, bottom: 5, left: 100 }}>
          <CartesianGrid stroke={colors.lightGray} strokeWidth={0.5} horizontal={false} vertical />
          <XAxis
            type="number"
            tick={{ fill: colors.darkGray, fontSize: 10, fontFamily: fonts.sans }}
            axisLine={{ stroke: colors.darkGray, strokeWidth: 0.8 }}
            tickLine={false}
            tickFormatter={(v) => `$${(v / 1e6).toFixed(0)}M`}
          />
          <YAxis
            type="category"
            dataKey="label"
            tick={{ fill: colors.darkGray, fontSize: 11, fontFamily: fonts.sans }}
            axisLine={false}
            tickLine={false}
            width={90}
          />
          <Tooltip
            contentStyle={{
              background: "#fff",
              border: `1px solid ${colors.lightGray}`,
              borderRadius: 4,
              fontFamily: fonts.sans,
              fontSize: 12,
            }}
            formatter={(value: number | undefined) => [formatUSD(value ?? 0), "Value"]}
          />
          <Bar dataKey="value" barSize={20} radius={[0, 3, 3, 0]}>
            {chartData.map((_, idx) => (
              <Cell key={idx} fill={colors.accent} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="source">Source: Codex.io API &middot; Net value transfer from retail to other wallet types</p>
    </div>
  );
}
