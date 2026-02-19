"use client";

import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { colors, fonts, formatCompact } from "@/lib/theme";
import type { MonthlyTrend } from "@/lib/types";

interface Props {
  data: MonthlyTrend[];
}

export default function MonthlyTrendsChart({ data }: Props) {
  const axisProps = {
    tick: { fill: colors.darkGray, fontSize: 10, fontFamily: fonts.sans },
    axisLine: { stroke: colors.darkGray, strokeWidth: 0.8 } as const,
    tickLine: false as const,
  };

  const gridProps = {
    stroke: colors.lightGray,
    strokeWidth: 0.5,
    vertical: false as const,
  };

  const shortMonth = (m: string) => m.replace("20", "'").replace(" ", " ");

  return (
    <div className="grid grid-cols-2 gap-8">
      {/* Panel 1: Launches */}
      <div>
        <h4 className="text-sm font-semibold mb-2" style={{ color: colors.darkGray }}>Total Launches</h4>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey="month" {...axisProps} tickFormatter={shortMonth} />
            <YAxis {...axisProps} tickFormatter={formatCompact} />
            <Bar dataKey="launches" fill={colors.primary} radius={[2, 2, 0, 0]} barSize={28} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Panel 2: Median Return */}
      <div>
        <h4 className="text-sm font-semibold mb-2" style={{ color: colors.darkGray }}>Median 7-Day Return</h4>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey="month" {...axisProps} tickFormatter={shortMonth} />
            <YAxis {...axisProps} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
            <Bar dataKey="medianReturn7d" barSize={28} radius={[2, 2, 0, 0]}>
              {data.map((entry, idx) => (
                <Cell key={idx} fill={entry.medianReturn7d >= 0 ? colors.tertiary : colors.accent} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Panel 3: Survival Rate */}
      <div>
        <h4 className="text-sm font-semibold mb-2" style={{ color: colors.darkGray }}>7-Day Survival Rate</h4>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={data} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey="month" {...axisProps} tickFormatter={shortMonth} />
            <YAxis {...axisProps} tickFormatter={(v) => `${(v * 100).toFixed(1)}%`} />
            <Line
              type="monotone" dataKey="survivalRate7d" stroke={colors.primary}
              strokeWidth={2} dot={{ r: 4, fill: colors.primary }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Panel 4: Sniper Count */}
      <div>
        <h4 className="text-sm font-semibold mb-2" style={{ color: colors.darkGray }}>Avg. Sniper Count</h4>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={data} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey="month" {...axisProps} tickFormatter={shortMonth} />
            <YAxis {...axisProps} />
            <Line
              type="monotone" dataKey="avgSniperCount" stroke={colors.accent}
              strokeWidth={2} dot={{ r: 4, fill: colors.accent }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
