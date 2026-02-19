/**
 * Placeholder data for the dashboard — renders with realistic shapes
 * before Codex.io API data is loaded. Based on publicly available
 * meme coin statistics (Pump.fun, CoinLaw, ChainPlay research).
 */

import type { DashboardData } from "@/lib/types";

function generateDailyLaunches() {
  const data = [];
  const start = new Date("2025-08-19");
  for (let i = 0; i < 184; i++) {
    const d = new Date(start);
    d.setDate(d.getDate() + i);
    const base = 28000 + Math.sin(i / 30) * 5000;
    const noise = () => Math.random() * 2000 - 1000;
    data.push({
      date: d.toISOString().slice(0, 10),
      solana: Math.round(base * 0.65 + noise()),
      base: Math.round(base * 0.18 + noise()),
      ethereum: Math.round(base * 0.10 + noise()),
      bsc: Math.round(base * 0.07 + noise()),
    });
  }
  return data;
}

function generateSurvivalCurves() {
  const days = Array.from({ length: 91 }, (_, i) => i);
  return days.map((d) => ({
    day: d,
    solana: Math.exp(-0.15 * d) * 100,
    base: Math.exp(-0.12 * d) * 100,
    ethereum: Math.exp(-0.10 * d) * 100,
    bsc: Math.exp(-0.18 * d) * 100,
  }));
}

function generateRocCurve() {
  const points = [];
  for (let i = 0; i <= 100; i++) {
    const fpr = i / 100;
    // Realistic ROC shape for AUC ~0.73
    const tpr = 1 - Math.pow(1 - fpr, 0.45);
    points.push({ fpr, tpr });
  }
  return points;
}

export const placeholderData: DashboardData = {
  summary: {
    totalLaunched: 5_847_230,
    totalGraduated: 43_854,
    totalDead: 5_614_141,
    survivalRate7d: 0.039,
    medianReturn7d: -0.94,
    totalVolumeUsd: 187_400_000_000,
    studyPeriod: "Aug 19, 2025 – Feb 19, 2026",
  },

  dailyLaunches: generateDailyLaunches(),

  returnDistribution: [
    { horizon: "1h", n: 847230, mean: -0.12, median: -0.34, p10: -0.89, p25: -0.67, p75: 0.15, p90: 1.20, p99: 28.5, pctPositive: 0.31, pct10x: 0.008, pct100x: 0.0003 },
    { horizon: "24h", n: 723100, mean: -0.38, median: -0.72, p10: -0.97, p25: -0.91, p75: -0.12, p90: 2.40, p99: 85.0, pctPositive: 0.18, pct10x: 0.012, pct100x: 0.001 },
    { horizon: "7d", n: 612400, mean: -0.61, median: -0.94, p10: -0.99, p25: -0.98, p75: -0.45, p90: 1.80, p99: 142.0, pctPositive: 0.08, pct10x: 0.009, pct100x: 0.0008 },
    { horizon: "30d", n: 489200, mean: -0.74, median: -0.97, p10: -1.00, p25: -0.99, p75: -0.78, p90: 0.50, p99: 95.0, pctPositive: 0.04, pct10x: 0.005, pct100x: 0.0004 },
  ],

  chainComparison: [
    { chain: "Solana", totalLaunched: 3_800_700, graduated: 28_505, survived7d: 148_227, survived30d: 38_007, medianReturn7d: -0.95, avgSniperCount: 12.4, survivalRate7d: 0.039 },
    { chain: "Base", totalLaunched: 1_052_500, graduated: 8_420, survived7d: 52_625, survived30d: 15_788, medianReturn7d: -0.92, avgSniperCount: 8.1, survivalRate7d: 0.050 },
    { chain: "Ethereum", totalLaunched: 584_720, graduated: 4_678, survived7d: 35_083, survived30d: 11_694, medianReturn7d: -0.88, avgSniperCount: 5.3, survivalRate7d: 0.060 },
    { chain: "BSC", totalLaunched: 409_310, graduated: 2_251, survived7d: 16_372, survived30d: 4_093, medianReturn7d: -0.96, avgSniperCount: 15.7, survivalRate7d: 0.040 },
  ],

  survivalCurves: generateSurvivalCurves(),

  walletPnl: [
    { type: "Sniper", count: 45200, totalBought: 892_000_000, totalSold: 1_247_000_000, totalPnl: 355_000_000, meanPnl: 7854, medianPnl: 1240, hitRate: 0.42 },
    { type: "Bundler", count: 12800, totalBought: 445_000_000, totalSold: 578_000_000, totalPnl: 133_000_000, meanPnl: 10390, medianPnl: 2100, hitRate: 0.38 },
    { type: "Insider", count: 8900, totalBought: 234_000_000, totalSold: 412_000_000, totalPnl: 178_000_000, meanPnl: 20000, medianPnl: 5800, hitRate: 0.54 },
    { type: "Dev", count: 320000, totalBought: 12_000_000, totalSold: 890_000_000, totalPnl: 878_000_000, meanPnl: 2744, medianPnl: 120, hitRate: 0.15 },
    { type: "Retail", count: 2_840_000, totalBought: 4_200_000_000, totalSold: 2_656_000_000, totalPnl: -1_544_000_000, meanPnl: -544, medianPnl: -380, hitRate: 0.11 },
  ],

  featureImportance: [
    { feature: "Initial Liquidity", oddsRatio: 2.34, ciLower: 2.01, ciUpper: 2.72, pValue: 0.001 },
    { feature: "Holder Count (1h)", oddsRatio: 1.89, ciLower: 1.62, ciUpper: 2.20, pValue: 0.001 },
    { feature: "Buy/Sell Ratio", oddsRatio: 1.54, ciLower: 1.31, ciUpper: 1.81, pValue: 0.001 },
    { feature: "Wallet Age Avg", oddsRatio: 1.42, ciLower: 1.18, ciUpper: 1.71, pValue: 0.003 },
    { feature: "Chain: Ethereum", oddsRatio: 1.31, ciLower: 1.08, ciUpper: 1.59, pValue: 0.012 },
    { feature: "Chain: Base", oddsRatio: 1.18, ciLower: 0.97, ciUpper: 1.44, pValue: 0.089 },
    { feature: "Bundler Count", oddsRatio: 0.82, ciLower: 0.68, ciUpper: 0.99, pValue: 0.041 },
    { feature: "Sniper Count", oddsRatio: 0.64, ciLower: 0.52, ciUpper: 0.79, pValue: 0.001 },
    { feature: "Dev Held %", oddsRatio: 0.51, ciLower: 0.41, ciUpper: 0.63, pValue: 0.001 },
    { feature: "Insider Count", oddsRatio: 0.43, ciLower: 0.32, ciUpper: 0.58, pValue: 0.001 },
  ],

  monthlyTrends: [
    { month: "Aug 2025", launches: 892400, medianReturn7d: -0.91, survivalRate7d: 0.045, avgSniperCount: 10.2 },
    { month: "Sep 2025", launches: 1024300, medianReturn7d: -0.93, survivalRate7d: 0.041, avgSniperCount: 11.5 },
    { month: "Oct 2025", launches: 1105200, medianReturn7d: -0.95, survivalRate7d: 0.037, avgSniperCount: 13.1 },
    { month: "Nov 2025", launches: 987600, medianReturn7d: -0.92, survivalRate7d: 0.042, avgSniperCount: 12.3 },
    { month: "Dec 2025", launches: 876500, medianReturn7d: -0.96, survivalRate7d: 0.033, avgSniperCount: 14.7 },
    { month: "Jan 2026", launches: 961230, medianReturn7d: -0.94, survivalRate7d: 0.038, avgSniperCount: 13.8 },
  ],

  rocCurve: generateRocCurve(),
  rocAuc: 0.731,

  heatmap: (() => {
    const sniperBuckets = ["0", "1–5", "6–10", "11–50", "50+"];
    const devBuckets = ["<1%", "1–5%", "5–10%", "10–25%", "25%+"];
    const cells = [];
    for (const dev of devBuckets) {
      for (const sniper of sniperBuckets) {
        const base = dev === "<1%" ? 8 : dev === "1–5%" ? 5 : dev === "5–10%" ? 3.5 : dev === "10–25%" ? 2 : 1;
        const penalty = sniper === "0" ? 1.3 : sniper === "1–5" ? 1.0 : sniper === "6–10" ? 0.7 : sniper === "11–50" ? 0.4 : 0.2;
        cells.push({
          sniperBucket: sniper,
          devHeldBucket: dev,
          survivalRate: +(base * penalty + Math.random() * 0.5).toFixed(1),
        });
      }
    }
    return cells;
  })(),

  valueFlows: [
    { source: "Retail", target: "Dev", value: 878_000_000 },
    { source: "Retail", target: "Sniper", value: 355_000_000 },
    { source: "Retail", target: "Insider", value: 178_000_000 },
    { source: "Retail", target: "Bundler", value: 133_000_000 },
  ],

  // Scatter plot: initial liquidity vs 7-day survival rate
  liquidityVsSurvival: Array.from({ length: 200 }, () => {
    const liq = Math.exp(Math.random() * 8 + 4); // $50 to $150k
    const survivalProb = 0.02 + 0.08 * (1 / (1 + Math.exp(-0.5 * (Math.log(liq) - 8)))) + (Math.random() - 0.5) * 0.04;
    return { x: liq, y: Math.max(0, Math.min(1, survivalProb)) };
  }),

  // Scatter plot: sniper count vs return
  sniperVsReturn: Array.from({ length: 200 }, () => {
    const snipers = Math.floor(Math.random() * 60);
    const baseReturn = -0.5 - snipers * 0.008 + (Math.random() - 0.5) * 0.6;
    return { x: snipers, y: Math.max(-1, Math.min(5, baseReturn)) };
  }),
};
