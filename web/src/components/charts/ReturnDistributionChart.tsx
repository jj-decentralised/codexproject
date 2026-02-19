"use client";

import { colors, fonts, palette } from "@/lib/theme";
import type { ReturnDistribution } from "@/lib/types";

interface Props {
  data: ReturnDistribution[];
}

export default function ReturnDistributionChart({ data }: Props) {
  return (
    <div className="overflow-x-auto">
      <table>
        <thead>
          <tr>
            <th>Horizon</th>
            <th className="text-right">N</th>
            <th className="text-right">Mean</th>
            <th className="text-right">Median</th>
            <th className="text-right">P10</th>
            <th className="text-right">P25</th>
            <th className="text-right">P75</th>
            <th className="text-right">P90</th>
            <th className="text-right">P99</th>
            <th className="text-right">% Positive</th>
            <th className="text-right">% 10x</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.horizon}>
              <td className="font-semibold">{row.horizon}</td>
              <td className="text-right num">{row.n.toLocaleString()}</td>
              <td className={`text-right num ${row.mean < 0 ? "negative" : "positive"}`}>
                {(row.mean * 100).toFixed(1)}%
              </td>
              <td className={`text-right num ${row.median < 0 ? "negative" : "positive"}`}>
                {(row.median * 100).toFixed(1)}%
              </td>
              <td className="text-right num negative">{(row.p10 * 100).toFixed(0)}%</td>
              <td className="text-right num negative">{(row.p25 * 100).toFixed(0)}%</td>
              <td className={`text-right num ${row.p75 < 0 ? "negative" : "positive"}`}>
                {(row.p75 * 100).toFixed(0)}%
              </td>
              <td className="text-right num positive">+{(row.p90 * 100).toFixed(0)}%</td>
              <td className="text-right num positive">+{(row.p99 * 100).toFixed(0)}%</td>
              <td className="text-right num">{(row.pctPositive * 100).toFixed(1)}%</td>
              <td className="text-right num">{(row.pct10x * 100).toFixed(2)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="source">Source: Codex.io API &middot; Returns clipped at -100%</p>
    </div>
  );
}
