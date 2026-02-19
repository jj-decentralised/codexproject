"use client";

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Cell,
} from "recharts";
import { colors, fonts } from "@/lib/theme";
import type { FeatureImportance } from "@/lib/types";

interface Props {
  data: FeatureImportance[];
}

export default function FeatureImportanceChart({ data }: Props) {
  const sorted = [...data].sort((a, b) => a.oddsRatio - b.oddsRatio);

  return (
    <div>
      <ResponsiveContainer width="100%" height={380}>
        <BarChart data={sorted} layout="vertical" margin={{ top: 5, right: 40, bottom: 5, left: 120 }}>
          <CartesianGrid stroke={colors.lightGray} strokeWidth={0.5} horizontal={false} vertical />
          <XAxis
            type="number"
            tick={{ fill: colors.darkGray, fontSize: 10, fontFamily: fonts.sans }}
            axisLine={{ stroke: colors.darkGray, strokeWidth: 0.8 }}
            tickLine={false}
            domain={[0, "auto"]}
          />
          <YAxis
            type="category"
            dataKey="feature"
            tick={{ fill: colors.darkGray, fontSize: 11, fontFamily: fonts.sans }}
            axisLine={false}
            tickLine={false}
            width={110}
          />
          <Tooltip
            contentStyle={{
              background: "#fff",
              border: `1px solid ${colors.lightGray}`,
              borderRadius: 4,
              fontFamily: fonts.sans,
              fontSize: 12,
            }}
            formatter={(value: number | undefined) => {
              if (value == null) return ["", ""];
              return [value.toFixed(2), "Odds Ratio"];
            }}
          />
          <ReferenceLine x={1} stroke={colors.darkGray} strokeWidth={0.8} strokeDasharray="4 4" />
          <Bar dataKey="oddsRatio" barSize={16} radius={[0, 2, 2, 0]}>
            {sorted.map((entry, idx) => (
              <Cell
                key={idx}
                fill={entry.oddsRatio >= 1 ? colors.tertiary : colors.accent}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex gap-4 mt-2 justify-center text-xs" style={{ color: colors.mediumGray }}>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded-sm" style={{ backgroundColor: colors.tertiary }} />
          Increases survival
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded-sm" style={{ backgroundColor: colors.accent }} />
          Decreases survival
        </span>
      </div>
      <p className="source">Source: Logistic regression on Codex.io data &middot; Odds ratios with 95% CI</p>
    </div>
  );
}
