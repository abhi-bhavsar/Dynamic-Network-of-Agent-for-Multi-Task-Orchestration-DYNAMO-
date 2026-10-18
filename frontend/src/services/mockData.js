export const MOCK_QUERIES = [
  {
    label: "Simple Price Check",
    query: "What is the current stock price and moving averages for Apple (AAPL)?",
    category: "simple",
  },
  {
    label: "Earnings & Sentiment",
    query: "Analyze Tesla's Q4 earnings, revenue growth, and Wall Street analyst sentiment.",
    category: "medium",
  },
  {
    label: "Full Conglomerate Research",
    query: "Comprehensive investment thesis for Reliance Industries across petrochemicals, Jio telecom, and retail scale-up.",
    category: "complex",
  },
  {
    label: "Macro & Risk Assessment",
    query: "Evaluate US inflation stickiness, Fed interest rate outlook, and portfolio downside hedging strategies.",
    category: "complex",
  },
];

export const MOCK_AGENTS = [
  {
    id: "deploy_market",
    name: "Market Data Agent",
    role: "market_specialist",
    domain: "Prices, Trading Volumes, Momentum, Moving Averages, Technicals",
    keywords: ["query", "ticker", "symbol", "price", "stock", "market", "volume", "trading", "technical", "chart", "momentum"],
    description: "Analyzes real-time market data, technical patterns, moving averages (50-DMA, 200-DMA), and volume surges.",
    color: "#06B6D4",
    icon: "TrendingUp",
  },
  {
    id: "deploy_sentiment",
    name: "Sentiment Agent",
    role: "sentiment_specialist",
    domain: "News Sentiment, Analyst Ratings, Social Buzz, Media Perception",
    keywords: ["query", "news", "sentiment", "analyst", "rating", "opinion", "media", "social", "buzz", "perception", "coverage"],
    description: "Performs NLP analysis on financial journalism, analyst revisions, and market chatter to gauge market mood.",
    color: "#8B5CF6",
    icon: "MessageSquare",
  },
  {
    id: "deploy_fundamental",
    name: "Fundamental Agent",
    role: "fundamental_specialist",
    domain: "Earnings, Balance Sheets, Valuation Ratios, SEC Filings",
    keywords: ["query", "earnings", "revenue", "eps", "ratio", "balance", "cash", "debt", "equity", "filing", "sec", "income"],
    description: "Extracts quarterly 10-Q/10-K data, assesses free cash flows, P/E multiples, and capital allocation metrics.",
    color: "#10B981",
    icon: "PieChart",
  },
  {
    id: "deploy_risk",
    name: "Risk Assessment Agent",
    role: "risk_specialist",
    domain: "Volatility, Beta, Downside Risk, VaR, Hedging",
    keywords: ["query", "risk", "volatility", "beta", "var", "downside", "hedge", "exposure", "liquidity", "concentration"],
    description: "Evaluates standard deviation, Value-at-Risk (VaR), beta sensitivity, maximum drawdowns, and hedging mechanisms.",
    color: "#F59E0B",
    icon: "ShieldAlert",
  },
  {
    id: "deploy_macro",
    name: "Macroeconomic Agent",
    role: "macro_specialist",
    domain: "GDP, Inflation, Interest Rates, Central Bank Policy, Currency",
    keywords: ["query", "gdp", "inflation", "interest", "fed", "macro", "economic", "currency", "rate", "policy", "trade"],
    description: "Evaluates sovereign bond yields, central bank rate cycles, inflation indices (CPI/PCE), and trade balance effects.",
    color: "#EC4899",
    icon: "Globe",
  },
];

export const MOCK_POLICIES = [
  {
    type: "on_demand",
    name: "On-Demand Spawning",
    condition: "N ≥ 0.7, C ≤ 2, U < 0.6",
    best_for: "Novel, simple, non-urgent queries",
    description: "Zero idle overhead. Agents created fresh per query and torn down immediately upon completion.",
  },
  {
    type: "pool_based",
    name: "Pool-Based Spawning",
    condition: "N < 0.4, U ≥ 0.7",
    best_for: "Time-critical, predictable queries",
    description: "Near-zero spawn latency. Pulls warm agents from a pre-allocated execution pool.",
  },
  {
    type: "predictive",
    name: "Predictive Provisioning",
    condition: "R ≥ 0.6, U < 0.7",
    best_for: "Recurring session query patterns",
    description: "Proactive provisioning based on historical Markov transition probabilities from prior queries.",
  },
  {
    type: "hierarchical",
    name: "Hierarchical Decomposition",
    condition: "C ≥ 4, N ≥ 0.5",
    best_for: "Deeply complex, novel multi-domain research",
    description: "Decomposes complex requests into nested sub-tasks, orchestrating the full specialist suite.",
  },
  {
    type: "composite",
    name: "Composite Hybrid",
    condition: "Mixed signals / boundary conditions",
    best_for: "Ambiguous query profiles",
    description: "Weighted hybrid policy that hedges by bumping agent cardinality up one tier.",
  },
];

export function generateSimulatedResponse(query, isBenchmark = false) {
  const lower = query.toLowerCase();
  let complexity = 2;
  let policy = "on_demand";
  let activeAgents = ["deploy_market"];

  if (lower.includes("comprehensive") || lower.includes("deep dive") || lower.includes("thesis") || lower.includes("portfolio")) {
    complexity = 5;
    policy = "hierarchical";
    activeAgents = ["deploy_market", "deploy_sentiment", "deploy_fundamental", "deploy_risk", "deploy_macro"];
  } else if (lower.includes("earnings") || lower.includes("growth") || lower.includes("revenue") || lower.includes("sentiment")) {
    complexity = 3;
    policy = "composite";
    activeAgents = ["deploy_market", "deploy_sentiment", "deploy_fundamental"];
  } else if (lower.includes("real-time") || lower.includes("now") || lower.includes("today") || lower.includes("live")) {
    complexity = 1;
    policy = "pool_based";
    activeAgents = ["deploy_market"];
  }

  const agentOutputs = {};
  const memorySlices = {};

  if (activeAgents.includes("deploy_market")) {
    agentOutputs["deploy_market"] = {
      agent_name: "deploy_market",
      findings: `**Market Dynamics Analysis**: Price action indicates solid structural support with 50-day moving average crossing above 200-day DMA (Golden Cross pattern). 30-day average daily volume is +18% above median. Momentum indicators (RSI: 58.4) confirm steady accumulation without entering overbought territory. Key resistance identified at +4.8% from current levels.`,
      confidence: 0.94,
      tokens_used: 320,
      error: "",
    };
    memorySlices["deploy_market"] = {
      query,
      ticker: "Identified Asset",
      price_metrics: "Historical OHLCV + Momentum Indicators",
      agent_role: "market_specialist",
    };
  }

  if (activeAgents.includes("deploy_sentiment")) {
    agentOutputs["deploy_sentiment"] = {
      agent_name: "deploy_sentiment",
      findings: `**Sentiment & Media Resonance**: Aggregated sentiment score stands at +0.72 (bullish). Institutional analyst revisions across the last 14 days show 8 Upgrades vs 1 Downgrade. Media narrative centers on operational efficiency, product pipeline velocity, and margins expansion. Retail commentary reflects sustained positive interest.`,
      confidence: 0.89,
      tokens_used: 285,
      error: "",
    };
    memorySlices["deploy_sentiment"] = {
      query,
      media_feed: "Analyst Notes, SEC Filings, Media Transcripts",
      buzz_index: "+0.72 Bullish",
      agent_role: "sentiment_specialist",
    };
  }

  if (activeAgents.includes("deploy_fundamental")) {
    agentOutputs["deploy_fundamental"] = {
      agent_name: "deploy_fundamental",
      findings: `**Fundamental Valuation & Health**: Forward P/E trades at 24.2x against an industry peer average of 28.5x. Operating margins expanded by 180 bps YoY to 26.4%, driven by favorable unit economics. Free cash flow conversion remains robust at 94% of Net Income. Balance sheet showcases a conservative Debt-to-Equity ratio of 0.38 with $14.2B in liquid reserves.`,
      confidence: 0.92,
      tokens_used: 395,
      error: "",
    };
    memorySlices["deploy_fundamental"] = {
      query,
      balance_sheet: "Debt/Equity 0.38, Liquid Reserves $14.2B",
      income_statement: "Margins +180 bps YoY",
      agent_role: "fundamental_specialist",
    };
  }

  if (activeAgents.includes("deploy_risk")) {
    agentOutputs["deploy_risk"] = {
      agent_name: "deploy_risk",
      findings: `**Risk Exposure & Stress Test**: Annualized historical volatility stands at 22.8% with a market Beta of 1.12. 95% Daily Value-at-Risk (VaR) is estimated at 2.45%. Concentration risk is well-mitigated across diversified revenue streams. Primary downside catalyst remains potential supply chain disruptions or regulatory shifts in cross-border trade.`,
      confidence: 0.88,
      tokens_used: 340,
      error: "",
    };
    memorySlices["deploy_risk"] = {
      query,
      volatility_beta: "Beta 1.12, Vol 22.8%",
      downside_stress: "95% Daily VaR 2.45%",
      agent_role: "risk_specialist",
    };
  }

  if (activeAgents.includes("deploy_macro")) {
    agentOutputs["deploy_macro"] = {
      agent_name: "deploy_macro",
      findings: `**Macroeconomic Environment**: Global monetary policy conditions are gradually transitioning into an easing stance. Headline CPI moderation supports real wage growth and corporate capital expenditure. Currency headwinds appear muted, with the USD Index consolidating within a tight multi-month band. Sovereign bond yield stability provides a constructive backdrop.`,
      confidence: 0.91,
      tokens_used: 310,
      error: "",
    };
    memorySlices["deploy_macro"] = {
      query,
      macro_indicators: "Fed Easing Path, Headline CPI Moderation",
      fx_rates: "USD Index consolidating, 10Y Yields stable",
      agent_role: "macro_specialist",
    };
  }

  const dynTokens = Object.values(agentOutputs).reduce((acc, curr) => acc + curr.tokens_used, 0) + 420;
  const staticTokens = dynTokens + (5 - activeAgents.length) * 350 + 280;
  const dynLatency = Math.round(280 + Math.random() * 250);
  const staticLatency = Math.round(dynLatency * 2.8 + Math.random() * 300);
  const tokenSavingsPct = Math.round(((staticTokens - dynTokens) / staticTokens) * 1000) / 10;
  const latencyImprovPct = Math.round(((staticLatency - dynLatency) / staticLatency) * 1000) / 10;

  const finalReport = `## Executive Summary
Comprehensive dynamic research demonstrates a highly favorable outlook for the requested asset. Market microstructure metrics indicate sustained institutional accumulation, supported by above-peer margin expansion and resilient cash flows.

## Key Findings
- **Technical & Market Momentum**: Moving averages reflect strong positive momentum with above-average volume confirmation and minimal overhead supply.
- **Valuation Advantage**: Trading at an attractive discount relative to historical 5-year averages and sector peers.
- **Operational Efficiency**: Operating margins increased by +180 bps YoY with disciplined debt governance and robust liquidity.
- **Risk Mitigation**: Portfolio beta remains controlled at 1.12 with VaR within acceptable risk budgets.

## Detailed Analysis
The synthesis of specialist findings highlights a convergent thesis. The market specialist notes that the Golden Cross formation reinforces an upward structural trend. Simultaneously, fundamental metrics confirm that recent earnings beats were driven by genuine volume expansion rather than accounting anomalies. Institutional sentiment is heavily tilted toward long accumulation.

## Risk & Caveats
- Sensitivity to unexpected shifts in central bank benchmark rate commentary.
- Intermediate resistance levels may induce short-term consolidation before further upside continuation.

## Conclusion
The asset demonstrates high investment attractiveness with balanced risk-reward asymmetry. Recommended strategy favors accumulate on pullbacks with downside stops placed below key moving average support.

Overall Confidence: 0.92`;

  const featureVector = {
    N: complexity >= 4 ? 0.85 : 0.42,
    U: lower.includes("real-time") || lower.includes("now") ? 0.88 : 0.35,
    C: complexity,
    R: 0.25,
  };

  const spawnManifest = {
    agents: activeAgents,
    policy,
    complexity,
    reasoning: `PSE selected ${policy.toUpperCase()} policy: Cardinality ${activeAgents.length}/5 specialist subagents activated.`,
    memory_keys: ["query", "price", "earnings", "sentiment", "risk", "macro"].slice(0, complexity + 1),
  };

  return {
    query,
    policy,
    policy_selected: policy,
    agents_used: activeAgents,
    agents_spawned: activeAgents.length,
    static_agents: 5,
    feature_vector: featureVector,
    spawn_manifest: spawnManifest,
    memory_slices: memorySlices,
    report: finalReport,
    confidence: 0.92,
    tokens_used: dynTokens,
    dynamic_tokens: dynTokens,
    static_tokens: isBenchmark ? staticTokens : undefined,
    latency_ms: dynLatency,
    dynamic_latency_ms: dynLatency,
    static_latency_ms: isBenchmark ? staticLatency : undefined,
    token_savings_pct: isBenchmark ? tokenSavingsPct : undefined,
    latency_improvement_pct: isBenchmark ? latencyImprovPct : undefined,
    agent_outputs: agentOutputs,
    errors: [],
  };
}
