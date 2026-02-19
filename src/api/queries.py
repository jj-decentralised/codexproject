"""GraphQL query strings for the Codex.io API."""

FILTER_TOKENS = """
query FilterTokens($filters: TokenFilters, $rankings: TokenRankings, $limit: Int, $offset: Int) {
  filterTokens(filters: $filters, rankings: $rankings, limit: $limit, offset: $offset) {
    count
    page
    results {
      createdAt
      lastTransaction
      buyCount1
      buyCount4
      buyCount12
      buyCount24
      sellCount1
      sellCount4
      sellCount12
      sellCount24
      change1
      change4
      change12
      change24
      volume24
      volumeChange24
      high24
      low24
      liquidity
      marketCap
      circulatingMarketCap
      priceUSD
      holders
      walletAgeAvg
      walletAgeStd
      token {
        address
        name
        symbol
        decimals
        networkId
        creatorAddress
        createTransactionHash
      }
      pair {
        address
        fee
        networkId
      }
      exchanges {
        address
        name
      }
      quoteToken
    }
  }
}
"""

FILTER_TOKENS_WITH_SNIPER_DATA = """
query FilterTokensWithSniperData($filters: TokenFilters, $rankings: TokenRankings, $limit: Int, $offset: Int) {
  filterTokens(filters: $filters, rankings: $rankings, limit: $limit, offset: $offset) {
    count
    page
    results {
      createdAt
      lastTransaction
      buyCount1
      buyCount24
      sellCount1
      sellCount24
      change1
      change24
      volume24
      liquidity
      marketCap
      priceUSD
      holders
      walletAgeAvg
      sniperCount
      bundlerCount
      insiderCount
      devHeldPercentage
      sniperHeldPercentage
      bundlerHeldPercentage
      insiderHeldPercentage
      token {
        address
        name
        symbol
        networkId
        creatorAddress
      }
      pair {
        address
        networkId
      }
      exchanges {
        address
        name
      }
    }
  }
}
"""

GET_BARS = """
query GetBars($symbol: String!, $from: Int!, $to: Int!, $resolution: String!) {
  getBars(symbol: $symbol, from: $from, to: $to, resolution: $resolution) {
    o
    h
    l
    c
    v
    volume
    t
    s
  }
}
"""

GET_TOKEN_EVENTS = """
query GetTokenEvents($query: EventsQueryInput!, $cursor: String) {
  getTokenEvents(query: $query, cursor: $cursor) {
    cursor
    items {
      timestamp
      eventType
      priceUsd
      priceUsdTotal
      priceBaseToken
      priceBaseTokenTotal
      maker
      blockNumber
      transactionHash
      token0SwapValueUsd
      token1SwapValueUsd
      data {
        type
        buyAmount
        sellAmount
      }
    }
  }
}
"""

GET_TOKEN_EVENTS_FOR_MAKER = """
query GetTokenEventsForMaker($input: EventsForMakerInput!) {
  getTokenEventsForMaker(input: $input) {
    cursor
    items {
      timestamp
      eventType
      priceUsd
      priceUsdTotal
      maker
      blockNumber
      transactionHash
      token0SwapValueUsd
      token1SwapValueUsd
      data {
        type
        buyAmount
        sellAmount
      }
    }
  }
}
"""

GET_DETAILED_PAIR_STATS = """
query GetDetailedPairStats($pairId: String!, $networkId: Int!, $tokenOfInterest: TokenOfInterest, $statsType: TokenPairStatisticsType) {
  getDetailedPairStats(pairId: $pairId, networkId: $networkId, tokenOfInterest: $tokenOfInterest, statsType: $statsType) {
    stats_min5 {
      statsUsd {
        close { timestamp value }
        volume { timestamp value }
        buyers { timestamp value }
        sellers { timestamp value }
      }
    }
    stats_hour1 {
      statsUsd {
        close { timestamp value }
        volume { timestamp value }
        buyers { timestamp value }
        sellers { timestamp value }
      }
    }
    stats_hour4 {
      statsUsd {
        close { timestamp value }
        volume { timestamp value }
        buyers { timestamp value }
        sellers { timestamp value }
      }
    }
    stats_hour12 {
      statsUsd {
        close { timestamp value }
        volume { timestamp value }
        buyers { timestamp value }
        sellers { timestamp value }
      }
    }
    stats_day1 {
      statsUsd {
        close { timestamp value }
        volume { timestamp value }
        buyers { timestamp value }
        sellers { timestamp value }
      }
    }
  }
}
"""

GET_NETWORKS = """
query GetNetworks {
  getNetworks {
    id
    name
  }
}
"""

LIST_PAIRS_WITH_METADATA = """
query ListPairsWithMetadataForToken($tokenAddress: String!, $networkId: Int!) {
  listPairsWithMetadataForToken(tokenAddress: $tokenAddress, networkId: $networkId) {
    results {
      pair {
        address
        fee
        token0
        token1
        networkId
      }
      volume24
      liquidity
      priceUsd
      exchangeHash
    }
  }
}
"""
