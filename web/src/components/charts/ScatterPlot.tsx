"use client";

import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { colors, fonts, formatCompact } from "@/lib/theme";

interface ScatterPoint {
  x: number;
  y: number;
  label?: string;
  chain?: string;
}

interface Props {
  data: ScatterPoint[];
  xLabel: string;
  yLabel: string;
  xFormatter?: (v: number) => string;
  yFormatter?: (v: number) => string;
}

export default function ScatterPlot({ data, xLabel, yLabel, xFormatter, yFormatter }: Props) {
  const xFmt = xFormatter ?? formatCompact;
  const yFmt = yFormatter ?? ((v: number) => `${(v * 100).toFixed(0)}%`);

  return (
    <div>
      <ResponsiveContainer width="100%" height={420}>
        <ScatterChart margin={{ top: 10, right: 30, bottom: 10, left: 20 }}>
          <CartesianGrid stroke={colors.lightGray} strokeWidth={0.5} vertical={false} />
          <XAxis
            dataKey="x"
            name={xLabel}
            type="number"
            tick={{ fill: colors.darkGray, fontSize: 10, fontFamily: fonts.sans }}
            axisLine={{ stroke: colors.darkGray, strokeWidth: 0.8 }}
            tickLine={false}
            tickFormatter={xFmt}
            label={{ value: xLabel, position: "insideBottom", offset: -5, fill: colors.darkGray, fontSize: 11, fontFamily: fonts.sans }}
          />
          <YAxis
            dataKey="y"
            name={yLabel}
            type="number"
            tick={{ fill: colors.darkGray, fontSize: 10, fontFamily: fonts.sans }}
            axisLine={false}
            tickLine={false}
            tickFormatter={yFmt}
            label={{ value: yLabel, angle: -90, position: "insideLeft", offset: 10, fill: colors.darkGray, fontSize: 11, fontFamily: fonts.sans }}
          />
          <ReferenceLine y={0} stroke={colors.mediumGray} strokeWidth={0.5} strokeDasharray="4 4" />
          <Tooltip
            contentStyle={{
              background: "#fff",
              border: `1px solid ${colors.lightGray}`,
              borderRadius: 4,
              fontFamily: fonts.sans,
              fontSize: 12,
              padding: "8px 12px",
            }}
            formatter={(value: number | undefined, name: string | undefined) => {
              if (name === xLabel) return [xFmt(value ?? 0), xLabel];
              return [yFmt(value ?? 0), yLabel];
            }}
          />
          <Scatter
            data={data}
            fill={colors.primary}
            fillOpacity={0.35}
            stroke={colors.primary}
            strokeOpacity={0.6}
            strokeWidth={0.5}
            r={3}
          />
        </ScatterChart>
      </ResponsiveContainer>
      <p className="source">Source: Codex.io API</p>
    </div>
  );
}
