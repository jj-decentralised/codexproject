"use client";

import { placeholderData } from "@/data/placeholder";
import StatCard from "@/components/StatCard";
import SectionHeader from "@/components/SectionHeader";
import Pullquote from "@/components/Pullquote";
import LaunchVolumeChart from "@/components/charts/LaunchVolumeChart";
import SurvivalChart from "@/components/charts/SurvivalChart";
import ReturnDistributionChart from "@/components/charts/ReturnDistributionChart";
import ChainComparisonTable from "@/components/charts/ChainComparisonTable";
import FeatureImportanceChart from "@/components/charts/FeatureImportanceChart";
import WalletPnlTable from "@/components/charts/WalletPnlTable";
import ValueFlowChart from "@/components/charts/ValueFlowChart";
import MonthlyTrendsChart from "@/components/charts/MonthlyTrendsChart";
import ScatterPlot from "@/components/charts/ScatterPlot";
import { formatCompact } from "@/lib/theme";

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

        <Pullquote
          quote="Nearly 5.8 million meme coins were launched in six months — more than 31,000 per day. Fewer than 4% survived a week."
          attribution="Codex.io census, Aug 2025 – Feb 2026"
        />

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

        <Pullquote
          quote="The median 7-day return is -94%. Only 0.9% of tokens achieve a 10x return. The distribution has a power-law right tail — a few enormous winners masking catastrophic losses for the vast majority."
        />

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

        <Pullquote
          quote="Retail wallets lost a combined $1.54 billion over six months. Devs extracted $878M, snipers $355M, insiders $178M. The house always wins — and in meme coins, the house is everyone who arrived before you."
        />

        {/* ── Section 6: What Predicts Survival ──── */}
        <div className="section-divider" />
        <SectionHeader
          number={6}
          title="What Predicts Survival?"
          subtitle="Logistic regression odds ratios — which first-hour metrics actually predict whether a meme coin lives past 7 days."
        />
        <FeatureImportanceChart data={data.featureImportance} />

        {/* ── Section 7: Scatter Analysis ──────────── */}
        <div className="section-divider" />
        <SectionHeader
          number={7}
          title="Liquidity and Predation"
          subtitle="Two key relationships: initial liquidity predicts survival, and sniper count predicts negative returns."
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h3
              className="text-base mb-3"
              style={{ fontFamily: "Georgia, serif", color: "#1a1a1a" }}
            >
              Initial Liquidity vs. 7-Day Survival Rate
            </h3>
            <ScatterPlot
              data={data.liquidityVsSurvival}
              xLabel="Initial Liquidity ($)"
              yLabel="Survival Rate"
              xFormatter={formatCompact}
              yFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
            />
          </div>
          <div>
            <h3
              className="text-base mb-3"
              style={{ fontFamily: "Georgia, serif", color: "#1a1a1a" }}
            >
              Sniper Count vs. 7-Day Return
            </h3>
            <ScatterPlot
              data={data.sniperVsReturn}
              xLabel="Sniper Count"
              yLabel="7-Day Return"
              xFormatter={(v: number) => String(Math.round(v))}
              yFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
            />
          </div>
        </div>

        {/* ── Section 8: Monthly Trends ──────────── */}
        <div className="section-divider" />
        <SectionHeader
          number={8}
          title="Monthly Trends"
          subtitle="How the meme coin market evolved over the 6-month study period."
        />
        <MonthlyTrendsChart data={data.monthlyTrends} />

        {/* ── Methodology ─────────────────────────── */}
        <div className="section-divider" />
        <section className="py-8">
          <h2
            className="text-xl mb-4"
            style={{ fontFamily: "Georgia, serif", color: "#1a1a1a" }}
          >
            Methodology
          </h2>
          <div
            className="text-sm leading-relaxed space-y-3 max-w-3xl"
            style={{ color: "#666666" }}
          >
            <p>
              <strong style={{ color: "#333" }}>Data source.</strong> All on-chain data is collected via
              the Codex.io GraphQL API (Enterprise tier, 100k call budget). The study covers four chains:
              Solana, Base, Ethereum, and Binance Smart Chain.
            </p>
            <p>
              <strong style={{ color: "#333" }}>Census.</strong> Token census uses <code>filterTokens</code> with
              daily <code>createdAt</code> windows. Tokens with 24h volume &gt; $1,000 are enumerated
              exhaustively; lower-volume tokens are statistically sampled and extrapolated.
            </p>
            <p>
              <strong style={{ color: "#333" }}>Survival analysis.</strong> Kaplan-Meier estimates with
              right-censoring for tokens still alive at study end. &ldquo;Death&rdquo; is defined as 24-hour
              trading volume dropping below $100 and remaining below for 48+ hours. Cox proportional
              hazards and accelerated failure time (Weibull) models are used for covariate analysis.
            </p>
            <p>
              <strong style={{ color: "#333" }}>Return calculation.</strong> Returns are measured from
              first-trade price using OHLCV data at hourly and daily resolution. Tokens that reach zero
              liquidity are assigned -100% return.
            </p>
            <p>
              <strong style={{ color: "#333" }}>Wallet classification.</strong> Snipers: buy within 4
              seconds of first swap. Bundlers: 4+ buys in the same block. Insiders: early buyer with
              &gt;1% of supply. Dev: contract deployer address. Retail: all remaining wallets.
            </p>
            <p>
              <strong style={{ color: "#333" }}>Predictive model.</strong> Logistic regression with L2
              regularization, trained on months 1&ndash;4, validated on months 5&ndash;6. Features are
              first-hour metrics only (no lookahead bias). ROC-AUC reported on the out-of-sample test set.
            </p>
          </div>
        </section>

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
