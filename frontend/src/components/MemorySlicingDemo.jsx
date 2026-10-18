import React, { useState } from 'react';
import { Scissors, Check, X, Shield, ArrowDownRight, Layers, FileCode } from 'lucide-react';
import { MOCK_AGENTS } from '../services/mockData';

export default function MemorySlicingDemo({ memorySlices, agentsUsed }) {
  const [activeTab, setActiveTab] = useState(agentsUsed?.[0] || 'deploy_market');

  const globalContextKeys = [
    { key: 'query', desc: 'Raw user query', everywhere: true },
    { key: 'ticker / asset', desc: 'Asset identifier & exchange symbols' },
    { key: 'price_metrics', desc: 'Real-time OHLCV, moving averages, momentum' },
    { key: 'media_feed', desc: 'News transcripts, analyst commentary, buzz' },
    { key: 'balance_sheet', desc: '10-Q/10-K ratios, debt, cash flows, filings' },
    { key: 'volatility_beta', desc: 'VaR 95%, Beta, historical volatility' },
    { key: 'macro_indicators', desc: 'Fed rate stance, CPI inflation, currency' },
    { key: 'session_history', desc: 'Past 10 queries in current session' },
  ];

  const agentRelevanceMap = {
    deploy_market: ['query', 'ticker / asset', 'price_metrics', 'session_history'],
    deploy_sentiment: ['query', 'ticker / asset', 'media_feed', 'session_history'],
    deploy_fundamental: ['query', 'ticker / asset', 'balance_sheet', 'session_history'],
    deploy_risk: ['query', 'ticker / asset', 'volatility_beta', 'session_history'],
    deploy_macro: ['query', 'macro_indicators', 'session_history'],
  };

  const selectedAgent = MOCK_AGENTS.find((a) => a.id === activeTab) || MOCK_AGENTS[0];
  const retainedKeys = agentRelevanceMap[selectedAgent.id] || ['query'];
  const prunedCount = globalContextKeys.length - retainedKeys.length;
  const compressionRatio = ((retainedKeys.length / globalContextKeys.length) * 100).toFixed(0);

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Scissors size={20} color="#f59e0b" />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Memory Slicing Inspector</h3>
          <span className="node-badge" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
            M(ai) ⊆ GlobalContext
          </span>
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Eliminates context flooding & cross-agent hallucination
        </div>
      </div>

      <div style={{ background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.25)', borderRadius: '8px', padding: '0.85rem' }}>
        <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          <strong>Mathematical Formalization:</strong> Each spawned agent receives strictly{' '}
          <code className="mono" style={{ color: '#fbbf24' }}>
            M(ai) = &#123; k ∈ G : Relevance(k, role(ai)) ≥ θ &#125;
          </code>
          . In naive multi-agent systems, passing full conversation histories sequentially compounds latency by{' '}
          <strong style={{ color: '#f87171' }}>O(N · M)</strong> and causes LLMs to process redundant context tokens.
        </div>
      </div>

      {/* Agent Selector Tabs */}
      <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
        {MOCK_AGENTS.map((agent) => {
          const isUsed = (agentsUsed || []).includes(agent.id);
          const isSelected = activeTab === agent.id;
          return (
            <button
              key={agent.id}
              onClick={() => setActiveTab(agent.id)}
              className="btn-secondary"
              style={{
                borderColor: isSelected ? 'var(--cyan-bright)' : undefined,
                background: isSelected ? 'rgba(6, 182, 212, 0.15)' : undefined,
                color: isSelected ? '#ffffff' : isUsed ? 'var(--text-main)' : 'var(--text-dim)',
                fontSize: '0.78rem',
                padding: '0.45rem 0.85rem',
              }}
            >
              <span
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: isUsed ? '#10b981' : '#64748b',
                  display: 'inline-block',
                }}
              />
              {agent.name}
            </button>
          );
        })}
      </div>

      {/* Context Partitioning Visual Matrix */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '1.25rem' }}>
        {/* Partitioning Table */}
        <div style={{ background: 'var(--bg-elevated)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--cyan-bright)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span>Context Keys for {selectedAgent.name}</span>
            <span className="mono" style={{ fontSize: '0.72rem', color: '#10b981' }}>
              {retainedKeys.length} Passed / {prunedCount} Pruned
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
            {globalContextKeys.map((item) => {
              const isIncluded = retainedKeys.includes(item.key);
              return (
                <div
                  key={item.key}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.4rem 0.65rem',
                    borderRadius: '6px',
                    background: isIncluded ? 'rgba(6, 182, 212, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                    border: `1px solid ${isIncluded ? 'rgba(6, 182, 212, 0.25)' : 'transparent'}`,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    {isIncluded ? (
                      <Check size={14} color="#34d399" />
                    ) : (
                      <X size={14} color="#64748b" />
                    )}
                    <span className="mono" style={{ fontSize: '0.78rem', color: isIncluded ? 'var(--text-main)' : 'var(--text-dim)' }}>
                      {item.key}
                    </span>
                  </div>
                  <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                    {isIncluded ? 'Scoped' : 'Pruned'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Compression & Advantage Stats */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          <div style={{ background: 'var(--bg-elevated)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              Memory Slice Compression Ratio
            </span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
              <span className="mono" style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--cyan-bright)' }}>
                {compressionRatio}%
              </span>
              <span style={{ fontSize: '0.78rem', color: '#34d399' }}>
                of full context footprint
              </span>
            </div>

            <div style={{ height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '999px', overflow: 'hidden' }}>
              <div
                style={{
                  height: '100%',
                  width: `${compressionRatio}%`,
                  background: 'linear-gradient(90deg, #06b6d4, #10b981)',
                  borderRadius: '999px',
                }}
              />
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Avoided sending ~{prunedCount * 120} irrelevant tokens to {selectedAgent.name}.
            </div>
          </div>

          <div style={{ background: 'var(--bg-elevated)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Domain Keyword Trigger Filter:
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
              {selectedAgent.keywords.slice(0, 8).map((kw) => (
                <span key={kw} className="slice-tag">
                  {kw}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
