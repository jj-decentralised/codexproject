"use client";

import { placeholderData } from "@/data/placeholder";
import StatCard from "@/components/StatCard";
import SectionHeader from "@/components/SectionHeader";
import LaunchVolumeChart from "@/components/charts/LaunchVolumeChart";
import SurvivalChart from "@/components/charts/SurvivalChart";
import ReturnDistributionChart from "@/components/charts/ReturnDistributionChart";
import ChainComparisonTable from "@/components/charts/ChainComparisonTable";
import FeatureImportanceChart from "@/components/charts/FeatureImportanceChart";
import WalletPnlTable from "@/components/charts/WalletPnlTable";
import ValueFlowChart from "@/components/charts/ValueFlowChart";
import MonthlyTrendsChart from "@/components/charts/MonthlyTrendsChart";

const data = placeholderData;

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      {/* ── Header ─────────────────────────────────── */}
      <header className="max-w-5xl mx-auto px-6 pt-16 pb-10">
        <p
          className="text-xs uppercase tracking-[0.2em] mb-3"
          style={{ color: "#999999" }}
        >
          Econometric Analysis
        </p>
        <h1
          className="text-4xl md:text-5xl leading-tight"
          style={{ fontFamily: "Georgia, serif", color: "#1a1a1a" }}
        >
          Meme Coin Markets
          <br />
          <span style={{ color: "#C4403D" }}>The Last 6 Months</span>
        </h1>
        <p className="mt-4 text-base leading-relaxed max-w-2xl" style={{ color: "#666666" }}>
          A comprehensive analysis of {data.summary.totalLaunched.toLocaleString()} meme coins launched
          across Solana, Base, Ethereum, and BSC from {data.summary.studyPeriod}. How much was made,
          how much was lost, and who walked away with the money.
        </p>
        <div
          className="mt-6 h-px w-full"
          style={{ backgroundColor: "#333333" }}
        />
      </header>

      <div className="max-w-5xl mx-auto px-6">
        {/* ── Key Figures ──────────────────────────── */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
          <StatCard
            label="Tokens Launched"
            value={data.summary.totalLaunched}
            format="number"
          />
          <StatCard
            label="Survived 7 Days"
            value={data.summary.survivalRate7d}
            format="pct"
            trend="negative"
            subtitle={`${data.summary.totalDead.toLocaleString()} dead`}
          />
          <StatCard
            label="Median 7-Day Return"
            value={data.summary.medianReturn7d}
            format="pct"
            trend="negative"
          />
          <StatCard
            label="Total Volume"
            value={data.summary.totalVolumeUsd}
            format="usd"
          />
        </section>

        {/* ── Section 1: Scale ──────────────────────── */}
        <div className="section-divider" />
        <SectionHeader
          number={1}
          title="The Launch Factory"
          subtitle="Daily meme coin deployments across four chains — tens of thousands per day, most dead within hours."
        />
        <LaunchVolumeChart data={data.dailyLaunches} />

        {/* ── Section 2: Survival ──────────────────── */}
        <div className="section-divider" />
        <SectionHeader
          number={2}
          title="The Survival Gauntlet"
          subtitle="Kaplan-Meier survival estimates — what percentage of meme coins are still trading after N days?"
        />
        <SurvivalChart data={data.survivalCurves} />

        {/* ── Section 3: Returns ──────────────────── */}
        <div className="section-divider" />
        <SectionHeader
          number={3}
          title="The Return Distribution"
          subtitle="Full distribution of returns at multiple horizons — the median is brutal, but the right tail is fat."
        />
        <ReturnDistributionChart data={data.returnDistribution} />

        {/* ── Section 4: Chain Comparison ──────────── */}
        <div className="section-divider" />
        <SectionHeader
          number={4}
          title="Chain-by-Chain Breakdown"
          subtitle="Solana dominates volume but Ethereum tokens survive longer. BSC has the most snipers."
        />
        <ChainComparisonTable data={data.chainComparison} />

        {/* ── Section 5: Who Profits ─────────────── */}
        <div className="section-divider" />
        <SectionHeader
          number={5}
          title="Who Walks Away With the Money?"
          subtitle="PnL decomposition by wallet type — snipers, bundlers, insiders, devs, and retail."
        />
        <WalletPnlTable data={data.walletPnl} />

        <div className="mt-10">
          <h3 className="text-lg mb-4" style={{ fontFamily: "Georgia, serif", color: "#1a1a1a" }}>
            Value Flow: Retail to Extractors
          </h3>
          <ValueFlowChart data={data.valueFlows} />
        </div>

        {/* ── Section 6: What Predicts Survival ──── */}
        <div className="section-divider" />
        <SectionHeader
          number={6}
          title="What Predicts Survival?"
          subtitle="Logistic regression odds ratios — which first-hour metrics actually predict whether a meme coin lives past 7 days."
        />
        <FeatureImportanceChart data={data.featureImportance} />

        {/* ── Section 7: Monthly Trends ──────────── */}
        <div className="section-divider" />
        <SectionHeader
          number={7}
          title="Monthly Trends"
          subtitle="How the meme coin market evolved over the 6-month study period."
        />
        <MonthlyTrendsChart data={data.monthlyTrends} />

        {/* ── Footer ────────────────────────────────── */}
        <div className="section-divider" />
        <footer className="py-12 text-center">
          <p className="text-xs" style={{ color: "#999999" }}>
            Data powered by <a href="https://codex.io" className="underline">Codex.io</a> API
            &middot; Analysis computed with Python (statsmodels, lifelines, arch, linearmodels)
          </p>
          <p className="text-xs mt-1" style={{ color: "#CCCCCC" }}>
            {data.summary.studyPeriod}
          </p>
        </footer>
      </div>
    </main>
  );
}
