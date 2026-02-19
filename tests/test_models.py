"""Tests for econometric models with synthetic data."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.data.processors.returns import return_distribution_stats
from src.data.processors.pnl import compute_wallet_pnl
from src.models.return_distribution import ReturnDistributionAnalyzer


class TestReturnDistribution:
    def setup_method(self):
        np.random.seed(42)
        n = 1000
        self.returns_df = pd.DataFrame({
            "address": [f"0x{i:04d}" for i in range(n)],
            "chain": np.random.choice(["solana", "base", "ethereum", "bsc"], n),
            "return_1h": np.random.normal(-0.3, 1.0, n),
            "return_24h": np.random.normal(-0.5, 2.0, n),
            "return_7d": np.random.normal(-0.6, 3.0, n),
            "return_30d": np.random.normal(-0.7, 4.0, n),
            "return_max": np.abs(np.random.pareto(1.5, n)),
        })

    def test_distribution_table(self):
        analyzer = ReturnDistributionAnalyzer(self.returns_df)
        table = analyzer.distribution_table()

        assert len(table) > 0
        assert "horizon" in table.columns
        assert "mean" in table.columns
        assert "median" in table.columns
        assert "p99" in table.columns

    def test_distribution_by_chain(self):
        analyzer = ReturnDistributionAnalyzer(self.returns_df)
        chain_table = analyzer.distribution_by_chain("7d")

        assert len(chain_table) == 4  # 4 chains
        assert "chain" in chain_table.columns

    def test_gini_coefficient(self):
        analyzer = ReturnDistributionAnalyzer(self.returns_df)
        gini = analyzer.gini_coefficient("7d")
        assert 0 <= gini <= 1

    def test_value_decomposition(self):
        analyzer = ReturnDistributionAnalyzer(self.returns_df)
        decomp = analyzer.value_decomposition("7d")
        assert "total_gain_sum" in decomp
        assert "total_loss_sum" in decomp
        assert decomp["gain_count"] + decomp["loss_count"] <= len(self.returns_df)


class TestReturnStats:
    def test_return_distribution_stats(self):
        df = pd.DataFrame({"return_7d": [0.5, -0.3, 1.0, -0.8, 10.0, -1.0, 0.1, 0.2]})
        stats = return_distribution_stats(df, "return_7d")

        assert stats["count"] == 8
        assert stats["pct_positive"] > 0
        assert stats["pct_10x"] > 0
        assert "p90" in stats


class TestWalletPnL:
    def test_compute_wallet_pnl(self):
        events = pd.DataFrame({
            "trade_type": ["buy", "buy", "sell"],
            "price_usd_total": ["100", "200", "500"],
            "timestamp": [1000, 2000, 3000],
        })

        pnl = compute_wallet_pnl(events)
        assert pnl["total_bought_usd"] == 300
        assert pnl["total_sold_usd"] == 500
        assert pnl["realized_pnl"] == 200
        assert pnl["trade_count"] == 3

    def test_empty_events(self):
        pnl = compute_wallet_pnl(pd.DataFrame())
        assert pnl["total_bought_usd"] == 0
        assert pnl["realized_pnl"] == 0
