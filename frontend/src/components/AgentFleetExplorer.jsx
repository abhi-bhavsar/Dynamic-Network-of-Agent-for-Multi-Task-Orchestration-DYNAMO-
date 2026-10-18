import React from 'react';
import {
  TrendingUp,
  MessageSquare,
  PieChart,
  ShieldAlert,
  Globe,
  Layers,
  KeyRound,
  FileQuestion,
  Sparkles,
} from 'lucide-react';
import { MOCK_AGENTS } from '../services/mockData';

const AGENT_ICON_MAP = {
  deploy_market: TrendingUp,
  deploy_sentiment: MessageSquare,
  deploy_fundamental: PieChart,
  deploy_risk: ShieldAlert,
  deploy_macro: Globe,
};

const AGENT_DETAILS = {
  deploy_market: {
    samples: [
      "What is the 50-day moving average and current price momentum for NVDA?",
      "Compare 30-day trading volume surges in Tesla vs historical medians.",
    ],
    execution: "Async Groq API call, 200-400 tokens, ~280ms execution latency.",
    specialty: "Market microstructure, technical chart patterns, liquidity spreads, and OHLCV analytics.",
  },
  deploy_sentiment: {
    samples: [
      "What is the consensus analyst rating and recent news sentiment on Apple?",
      "Analyze media perception shifts following Microsoft's AI announcements.",
    ],
    execution: "Async NLP extraction over media and analyst revisions, ~320 tokens, ~310ms.",
    specialty: "Natural language processing of financial news, media transcripts, social buzz, and Wall Street rating changes.",
  },
  deploy_fundamental: {
    samples: [
      "Analyze Reliance Industries petrochemicals margin breakdown and debt obligations.",
      "Evaluate Alphabet's free cash flow conversion rate and forward P/E multiple.",
    ],
    execution: "Async financial statement synthesis, ~400 tokens, ~340ms.",
    specialty: "10-Q/10-K quarterly filings, operating margin expansion, EPS quality, and balance sheet solvency.",
  },
  deploy_risk: {
    samples: [
      "Calculate portfolio 95% Daily Value-at-Risk (VaR) and beta sensitivity for tech stocks.",
      "What downside hedging strategies are appropriate for rate volatility?",
    ],
    execution: "Async volatility modeling, ~350 tokens, ~300ms.",
    specialty: "Standard deviation, Value-at-Risk (VaR), beta sensitivity to benchmark indices, drawdowns, and tail-risk hedging.",
  },
  deploy_macro: {
    samples: [
      "Assess how US Fed interest rate policy and sticky CPI inflation impact tech valuations.",
      "Analyze currency headwinds on Indian IT services exports given USD/INR dynamics.",
    ],
    execution: "Async macroeconomic analysis, ~360 tokens, ~310ms.",
    specialty: "Central bank monetary policy, sovereign yield curves, inflation metrics (CPI/PCE), and foreign exchange shifts.",
  },
};

export default function AgentFleetExplorer() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="glass-panel" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <Layers size={24} color="#06b6d4" />
          <div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800 }}>Specialist Agent Fleet Registry</h2>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Ephemeral specialist agents orchestrated dynamically via LangGraph & asyncio.gather()
            </div>
          </div>
        </div>

        <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          Rather than keeping all agents idle and processing full context sequentially, DYNAMO activates only
          the specialized agents demanded by the query's complexity tier, injecting strictly filtered memory slices.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.25rem' }}>
        {MOCK_AGENTS.map((agent) => {
          const IconComponent = AGENT_ICON_MAP[agent.id] || Sparkles;
          const details = AGENT_DETAILS[agent.id];

          return (
            <div
              key={agent.id}
              className="glass-panel"
              style={{
                padding: '1.5rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1rem',
                border: `1px solid ${agent.color}35`,
                background: `linear-gradient(135deg, ${agent.color}08 0%, var(--bg-card) 100%)`,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div
                  className="agent-icon"
                  style={{
                    backgroundColor: `${agent.color}25`,
                    color: agent.color,
                    border: `1px solid ${agent.color}50`,
                  }}
                >
                  <IconComponent size={20} />
                </div>
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    {agent.name}
                  </h3>
                  <div className="mono" style={{ fontSize: '0.72rem', color: agent.color }}>
                    {agent.id} · {agent.role}
                  </div>
                </div>
              </div>

              <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {agent.description}
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <KeyRound size={13} color="var(--cyan-bright)" />
                  Domain Relevance Keywords:
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
                  {agent.keywords.map((kw) => (
                    <span key={kw} className="slice-tag" style={{ fontSize: '0.68rem', color: agent.color, borderColor: `${agent.color}40` }}>
                      {kw}
                    </span>
                  ))}
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', background: 'var(--bg-input)', padding: '0.75rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <FileQuestion size={12} color="var(--amber-bright)" />
                  Sample Queries Triggering this Agent:
                </div>
                {details?.samples.map((s, idx) => (
                  <div key={idx} style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                    "{s}"
                  </div>
                ))}
              </div>

              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.65rem' }}>
                ⚡ {details?.execution}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
