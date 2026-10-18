import React, { useState } from 'react';
import { Cpu, CheckCircle2, ArrowRight, Sparkles, Layers, Sliders } from 'lucide-react';
import { MOCK_POLICIES, MOCK_AGENTS } from '../services/mockData';

export default function PseSimulator() {
  const [n, setN] = useState(0.85);
  const [u, setU] = useState(0.35);
  const [c, setC] = useState(2);
  const [r, setR] = useState(0.15);

  // Evaluate PSE decision function in real-time
  const evaluatePolicy = () => {
    if (c >= 4 && n >= 0.5) {
      return {
        policy: 'hierarchical',
        ruleIndex: 1,
        ruleText: 'Priority 1: High Complexity (C ≥ 4) & Novelty (N ≥ 0.5)',
        agentCount: 5,
        agents: ['deploy_market', 'deploy_sentiment', 'deploy_fundamental', 'deploy_risk', 'deploy_macro'],
      };
    }
    if (n < 0.4 && u >= 0.7) {
      return {
        policy: 'pool_based',
        ruleIndex: 2,
        ruleText: 'Priority 2: Low Novelty (N < 0.4) & Urgent (U ≥ 0.7)',
        agentCount: c,
        agents: ['deploy_market', 'deploy_sentiment', 'deploy_fundamental', 'deploy_risk', 'deploy_macro'].slice(0, c),
      };
    }
    if (r >= 0.6 && u < 0.7) {
      return {
        policy: 'predictive',
        ruleIndex: 3,
        ruleText: 'Priority 3: High Recurrence (R ≥ 0.6) & Non-Urgent (U < 0.7)',
        agentCount: c,
        agents: ['deploy_market', 'deploy_sentiment', 'deploy_fundamental', 'deploy_risk', 'deploy_macro'].slice(0, c),
      };
    }
    if (n >= 0.7 && c <= 2 && u < 0.6) {
      return {
        policy: 'on_demand',
        ruleIndex: 4,
        ruleText: 'Priority 4: Novel (N ≥ 0.7), Simple (C ≤ 2), Non-Urgent (U < 0.6)',
        agentCount: c,
        agents: ['deploy_market', 'deploy_sentiment', 'deploy_fundamental', 'deploy_risk', 'deploy_macro'].slice(0, c),
      };
    }
    const bumped = Math.min(5, c + 1);
    return {
      policy: 'composite',
      ruleIndex: 5,
      ruleText: 'Priority 5: Mixed signals fallback — hedges by bumping cardinality +1',
      agentCount: bumped,
      agents: ['deploy_market', 'deploy_sentiment', 'deploy_fundamental', 'deploy_risk', 'deploy_macro'].slice(0, bumped),
    };
  };

  const currentDecision = evaluatePolicy();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="glass-panel" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <Cpu size={24} color="#06b6d4" />
          <div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800 }}>PSE Policy Decision Simulator</h2>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Interactive playground testing the Policy Selection Engine: Φ : F(Q) → π ∈ Π
            </div>
          </div>
        </div>

        <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          Adjust the four query feature dimensions below in real-time to observe how the PSE rules evaluate
          priority boundaries and determine the dynamic agent spawning manifest.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '1.5rem' }}>
        {/* Sliders Panel */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sliders size={18} color="var(--cyan-bright)" />
            <span>Query Feature Dimensions F(Q)</span>
          </div>

          {/* Novelty Slider */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem' }}>
              <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Novelty (N)</span>
              <span className="mono" style={{ color: 'var(--cyan-bright)', fontWeight: 700 }}>
                {n.toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={n}
              onChange={(e) => setN(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--cyan-bright)' }}
            />
            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
              1 - max_similarity(query, history). High = completely unprecedented query.
            </div>
          </div>

          {/* Urgency Slider */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem' }}>
              <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Urgency (U)</span>
              <span className="mono" style={{ color: '#f59e0b', fontWeight: 700 }}>
                {u.toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min="0.3"
              max="0.95"
              step="0.05"
              value={u}
              onChange={(e) => setU(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: '#f59e0b' }}
            />
            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
              Presence of real-time, live, instant keywords.
            </div>
          </div>

          {/* Complexity Slider */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem' }}>
              <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Complexity (C)</span>
              <span className="mono" style={{ color: '#8b5cf6', fontWeight: 700 }}>
                {c}/5
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="5"
              step="1"
              value={c}
              onChange={(e) => setC(parseInt(e.target.value))}
              style={{ width: '100%', accentColor: '#8b5cf6' }}
            />
            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
              Predicted agent cardinality needed (1 = simple price, 5 = full multi-domain research).
            </div>
          </div>

          {/* Recurrence Slider */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem' }}>
              <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Recurrence (R)</span>
              <span className="mono" style={{ color: '#10b981', fontWeight: 700 }}>
                {r.toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={r}
              onChange={(e) => setR(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: '#10b981' }}
            />
            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
              Semantic frequency of this query pattern across session history.
            </div>
          </div>
        </div>

        {/* Real-time Result Decision Card */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div
            className="glass-panel"
            style={{
              padding: '1.5rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
              border: '1px solid rgba(6, 182, 212, 0.4)',
              background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, var(--bg-card) 100%)',
            }}
          >
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Selected Spawning Policy
            </span>

            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.75rem' }}>
              <span
                className="mono"
                style={{
                  fontSize: '1.85rem',
                  fontWeight: 900,
                  color: 'var(--cyan-bright)',
                  letterSpacing: '0.02em',
                }}
              >
                {currentDecision.policy.toUpperCase()}
              </span>
              <span className="node-badge" style={{ background: 'rgba(6, 182, 212, 0.2)' }}>
                Rule #{currentDecision.ruleIndex}
              </span>
            </div>

            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', background: 'var(--bg-input)', padding: '0.75rem', borderRadius: '6px' }}>
              {currentDecision.ruleText}
            </div>

            <div style={{ marginTop: '0.5rem' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                Agents Spawned ({currentDecision.agentCount}/5):
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                {MOCK_AGENTS.map((agent) => {
                  const isSpawned = currentDecision.agents.includes(agent.id);
                  return (
                    <span
                      key={agent.id}
                      className="mono"
                      style={{
                        padding: '0.3rem 0.65rem',
                        borderRadius: '6px',
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        backgroundColor: isSpawned ? `${agent.color}25` : 'rgba(255, 255, 255, 0.03)',
                        color: isSpawned ? agent.color : 'var(--text-dim)',
                        border: `1px solid ${isSpawned ? `${agent.color}50` : 'transparent'}`,
                      }}
                    >
                      {isSpawned ? '✓ ' : '✗ '} {agent.name.replace(' Agent', '')}
                    </span>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Policy Space Matrix Reference */}
          <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Policy Space Rules Matrix (Π)
            </span>
            {MOCK_POLICIES.map((p) => {
              const isMatch = p.type === currentDecision.policy;
              return (
                <div
                  key={p.type}
                  style={{
                    padding: '0.6rem 0.85rem',
                    borderRadius: '6px',
                    background: isMatch ? 'rgba(6, 182, 212, 0.15)' : 'transparent',
                    border: `1px solid ${isMatch ? 'rgba(6, 182, 212, 0.35)' : 'var(--border-subtle)'}`,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.2rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong style={{ fontSize: '0.8rem', color: isMatch ? 'var(--cyan-bright)' : 'var(--text-secondary)' }}>
                      {p.name}
                    </strong>
                    <span className="mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                      {p.condition}
                    </span>
                  </div>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                    {p.best_for}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
