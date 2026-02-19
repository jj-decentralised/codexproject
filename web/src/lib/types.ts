/** Data types for the meme coin analytics dashboard. */

export interface DailyLaunchData {
  date: string;
  solana: number;
  base: number;
  ethereum: number;
  bsc: number;
}

export interface ReturnDistribution {
  horizon: string;
  n: number;
  mean: number;
  median: number;
  p10: number;
  p25: number;
  p75: number;
  p90: number;
  p99: number;
  pctPositive: number;
  pct10x: number;
  pct100x: number;
}

export interface ChainComparison {
  chain: string;
  totalLaunched: number;
  graduated: number;
  survived7d: number;
  survived30d: number;
  medianReturn7d: number;
  avgSniperCount: number;
  survivalRate7d: number;
}

export interface SurvivalPoint {
  day: number;
  [chain: string]: number;
}

export interface WalletPnL {
  type: string;
  count: number;
  totalBought: number;
  totalSold: number;
  totalPnl: number;
  meanPnl: number;
  medianPnl: number;
  hitRate: number;
}

export interface FeatureImportance {
  feature: string;
  oddsRatio: number;
  ciLower: number;
  ciUpper: number;
  pValue: number;
}

export interface MonthlyTrend {
  month: string;
  launches: number;
  medianReturn7d: number;
  survivalRate7d: number;
  avgSniperCount: number;
}

export interface RocPoint {
  fpr: number;
  tpr: number;
}

export interface HeatmapCell {
  sniperBucket: string;
  devHeldBucket: string;
  survivalRate: number;
}

export interface ValueFlow {
  source: string;
  target: string;
  value: number;
}

export interface DashboardData {
  summary: {
    totalLaunched: number;
    totalGraduated: number;
    totalDead: number;
    survivalRate7d: number;
    medianReturn7d: number;
    totalVolumeUsd: number;
    studyPeriod: string;
  };
  dailyLaunches: DailyLaunchData[];
  returnDistribution: ReturnDistribution[];
  chainComparison: ChainComparison[];
  survivalCurves: SurvivalPoint[];
  walletPnl: WalletPnL[];
  featureImportance: FeatureImportance[];
  monthlyTrends: MonthlyTrend[];
  rocCurve: RocPoint[];
  rocAuc: number;
  heatmap: HeatmapCell[];
  valueFlows: ValueFlow[];
  liquidityVsSurvival: { x: number; y: number }[];
  sniperVsReturn: { x: number; y: number }[];
}
