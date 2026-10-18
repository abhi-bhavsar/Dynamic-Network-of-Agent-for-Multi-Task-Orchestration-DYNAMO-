import React, { useState } from 'react';
import {
  TrendingUp,
  MessageSquare,
  PieChart,
  ShieldAlert,
  Globe,
  CheckCircle,
  Clock,
  ChevronDown,
  ChevronUp,
  Coins,
  Gauge,
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

export default function AgentTraceView({ agentOutputs, agentsUsed }) {
  const [expandedAgents, setExpandedAgents] = useState({});

  const toggleExpand = (agentKey) => {
    setExpandedAgents((prev) => ({
      ...prev,
      [agentKey]: !prev[agentKey],
    }));
  };

  const usedSet = new Set(agentsUsed || []);

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={18} color="#06b6d4" />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Specialist Agent Trace</h3>
          <span className="node-badge" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
            {usedSet.size} Active / {5 - usedSet.size} Pruned (Tokens Saved)
          </span>
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Concurrent execution via asyncio.gather()
        </div>
      </div>

      <div className="agents-grid">
        {MOCK_AGENTS.map((agent) => {
          const isActive = usedSet.has(agent.id);
          const output = agentOutputs?.[agent.id];
          const isExpanded = expandedAgents[agent.id] ?? isActive;
          const IconComponent = AGENT_ICON_MAP[agent.id] || Sparkles;

          const confidence = output?.confidence ?? (isActive ? 0.88 : 0);
          const tokens = output?.tokens_used ?? 0;
          const findings = output?.findings;

          return (
            <div
              key={agent.id}
              className={`agent-card ${isActive ? 'active' : 'standby'}`}
            >
              <div className="agent-card-header">
                <div className="agent-identity">
                  <div
                    className="agent-icon"
                    style={{
                      backgroundColor: `${agent.color}20`,
                      color: agent.color,
                      border: `1px solid ${agent.color}40`,
                    }}
                  >
                    <IconComponent size={18} />
                  </div>
                  <div>
                    <div className="agent-title">{agent.name}</div>
                    <div className="agent-role">{agent.role}</div>
                  </div>
                </div>

                <span className={`agent-badge ${isActive ? 'active' : 'standby'}`}>
                  {isActive ? 'Active' : 'Standby'}
                </span>
              </div>

              {isActive ? (
                <>
                  <div className="agent-stats">
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <Gauge size={13} color="var(--cyan-bright)" />
                      Confidence: <strong>{(confidence * 100).toFixed(0)}%</strong>
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <Coins size={13} color="var(--amber-bright)" />
                      Tokens: <strong>{tokens}</strong>
                    </span>
                  </div>

                  {findings && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                      <button
                        onClick={() => toggleExpand(agent.id)}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: 'var(--cyan-bright)',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          alignSelf: 'flex-start',
                        }}
                      >
                        {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                        {isExpanded ? 'Hide Findings' : 'Show Agent Findings'}
                      </button>

                      {isExpanded && (
                        <div className="agent-findings animate-fade-in">
                          {findings}
                        </div>
                      )}
                    </div>
                  )}
                </>
              ) : (
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontStyle: 'italic', padding: '0.5rem 0' }}>
                  Pruned by PSE: Query complexity did not trigger {agent.name.toLowerCase()} rules. Preserved tokens & latency.
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
