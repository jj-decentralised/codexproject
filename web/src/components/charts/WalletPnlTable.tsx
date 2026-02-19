"use client";

import { colors, formatUSD } from "@/lib/theme";
import type { WalletPnL } from "@/lib/types";

interface Props {
  data: WalletPnL[];
}

export default function WalletPnlTable({ data }: Props) {
  return (
    <div className="overflow-x-auto">
      <table>
        <thead>
          <tr>
            <th>Wallet Type</th>
            <th className="text-right">Wallets</th>
            <th className="text-right">Total Bought</th>
            <th className="text-right">Total Sold</th>
            <th className="text-right">Net PnL</th>
            <th className="text-right">Mean PnL</th>
            <th className="text-right">Median PnL</th>
            <th className="text-right">Hit Rate</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.type}>
              <td className="font-semibold">{row.type}</td>
              <td className="text-right num">{row.count.toLocaleString()}</td>
              <td className="text-right num">{formatUSD(row.totalBought)}</td>
              <td className="text-right num">{formatUSD(row.totalSold)}</td>
              <td className={`text-right num font-semibold ${row.totalPnl >= 0 ? "positive" : "negative"}`}>
                {formatUSD(row.totalPnl)}
              </td>
              <td className={`text-right num ${row.meanPnl >= 0 ? "positive" : "negative"}`}>
                {formatUSD(row.meanPnl)}
              </td>
              <td className={`text-right num ${row.medianPnl >= 0 ? "positive" : "negative"}`}>
                {formatUSD(row.medianPnl)}
              </td>
              <td className="text-right num">{(row.hitRate * 100).toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="source">Source: Codex.io API &middot; Wallet classification per Codex sniper/bundler detection</p>
    </div>
  );
}
