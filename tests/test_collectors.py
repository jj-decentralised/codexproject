"""Tests for data collectors."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.data.collectors.token_census import TokenCensus
from src.data.collectors.ohlcv_collector import OHLCVCollector


class TestTokenCensus:
    def test_flatten_token(self):
        token = {
            "createdAt": 1700000000,
            "lastTransaction": 1700100000,
            "buyCount1": 50,
            "buyCount24": 200,
            "sellCount1": 30,
            "sellCount24": 150,
            "change1": 0.05,
            "change24": 0.15,
            "volume24": "50000",
            "liquidity": "10000",
            "marketCap": "100000",
            "priceUSD": "0.001",
            "holders": 100,
            "walletAgeAvg": 30,
            "sniperCount": 5,
            "bundlerCount": 2,
            "insiderCount": 1,
            "devHeldPercentage": 10.5,
            "sniperHeldPercentage": 3.2,
            "bundlerHeldPercentage": 1.5,
            "insiderHeldPercentage": 0.8,
            "token": {
                "address": "0xabc123",
                "name": "TestMeme",
                "symbol": "TMEME",
                "networkId": 1,
                "creatorAddress": "0xdev456",
            },
            "pair": {"address": "0xpair789", "networkId": 1},
            "exchanges": [{"address": "0xexch", "name": "Pump.fun"}],
        }

        result = TokenCensus._flatten_token(token, "solana", "tier_a")

        assert result["address"] == "0xabc123"
        assert result["name"] == "TestMeme"
        assert result["symbol"] == "TMEME"
        assert result["chain"] == "solana"
        assert result["tier"] == "tier_a"
        assert result["sniper_count"] == 5
        assert result["dev_held_pct"] == 10.5
        assert result["exchange_name"] == "Pump.fun"
        assert result["created_at"] == 1700000000


class TestOHLCVCollector:
    def test_window_seconds(self):
        client_mock = MagicMock()
        collector = OHLCVCollector(client_mock)

        assert collector._window_seconds("1") == 60 * 1400
        assert collector._window_seconds("60") == 3600 * 1400
        assert collector._window_seconds("1D") == 86400 * 1400

    def test_make_symbol(self):
        client_mock = MagicMock()
        collector = OHLCVCollector(client_mock)

        symbol = collector._make_symbol("0xpair123", 1)
        assert symbol == "0xpair123:1"
