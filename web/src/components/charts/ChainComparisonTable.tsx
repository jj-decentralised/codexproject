"use client";

import { colors, formatNumber } from "@/lib/theme";
import type { ChainComparison } from "@/lib/types";

interface Props {
  data: ChainComparison[];
}

export default function ChainComparisonTable({ data }: Props) {
  return (
    <div className="overflow-x-auto">
      <table>
        <thead>
          <tr>
            <th>Chain</th>
            <th className="text-right">Launched</th>
            <th className="text-right">Graduated</th>
            <th className="text-right">Survived 7d</th>
            <th className="text-right">Survived 30d</th>
            <th className="text-right">Survival Rate</th>
            <th className="text-right">Median Return</th>
            <th className="text-right">Avg Snipers</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.chain}>
              <td className="font-semibold">{row.chain}</td>
              <td className="text-right num">{formatNumber(row.totalLaunched)}</td>
              <td className="text-right num">{formatNumber(row.graduated)}</td>
              <td className="text-right num">{formatNumber(row.survived7d)}</td>
              <td className="text-right num">{formatNumber(row.survived30d)}</td>
              <td className="text-right num">{(row.survivalRate7d * 100).toFixed(1)}%</td>
              <td className="text-right num negative">{(row.medianReturn7d * 100).toFixed(0)}%</td>
              <td className="text-right num">{row.avgSniperCount.toFixed(1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="source">Source: Codex.io API &middot; Study period: Aug 2025 – Feb 2026</p>
    </div>
  );
}
