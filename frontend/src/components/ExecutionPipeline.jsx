import React, { useState } from 'react';
import {
  FileText,
  Sliders,
  Cpu,
  Layers,
  Zap,
  Scissors,
  CheckCircle2,
  Clock,
  ArrowRight,
  Info,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

export default function ExecutionPipeline({ isRunning, result, activeStep }) {
  const [selectedNode, setSelectedNode] = useState(null);

  // Compute node status based on execution state
  const getNodeStatus = (stepIndex) => {
    if (isRunning) {
      if (activeStep === stepIndex) return 'running';
      if (activeStep > stepIndex) return 'completed';
      return 'idle';
    }
    if (result) return 'completed';
    return 'idle';
  };

  const policy = result?.policy || result?.policy_selected || 'Pending';
  const fv = result?.feature_vector || {};
  const agentsUsed = result?.agents_used || [];
  const memorySlices = result?.memory_slices || {};
  const confidence = result?.confidence || 0;

  const nodes = [
    {
      id: 'input',
      step: '01',
      title: 'Query Ingestion',
      icon: FileText,
      meta: result ? `Len: ${result.query.length} chars` : 'Awaiting input',
      badge: 'Input',
      color: '#06b6d4',
      details: {
        query: result?.query,
        history_window: 'Last 10 queries',
      },
    },
    {
      id: 'feature',
      step: '02',
      title: 'Feature Extraction F(Q)',
      icon: Sliders,
      meta: result ? `N:${fv.N || 0} U:${fv.U || 0} C:${fv.C || 1} R:${fv.R || 0}` : 'Keyword analysis',
      badge: fv.C ? `C = ${fv.C}/5` : 'F(Q)',
      color: '#3b82f6',
      details: {
        feature_vector: fv,
        description: 'Computes Novelty, Urgency, Complexity, and Recurrence without LLM latency.',
      },
    },
    {
      id: 'pse',
      step: '03',
      title: 'PSE Decision Engine',
      icon: Cpu,
      meta: result ? policy.toUpperCase() : 'Policy mapping',
      badge: policy !== 'Pending' ? policy.toUpperCase() : 'Policy',
      color: '#8b5cf6',
      details: {
        selected_policy: policy,
        rule_evaluated: `Evaluated across policy space Π (ON_DEMAND, POOL_BASED, PREDICTIVE, HIERARCHICAL, COMPOSITE)`,
      },
    },
    {
      id: 'orchestrator',
      step: '04',
      title: 'Spawn Manifest',
      icon: Layers,
      meta: result ? `${agentsUsed.length} agents routed` : 'Pydantic validation',
      badge: 'Manifest',
      color: '#ec4899',
      details: {
        manifest: result?.spawn_manifest || {
          agents: agentsUsed,
          policy,
          complexity: fv.C || 1,
        },
      },
    },
    {
      id: 'agents',
      step: '05',
      title: 'Concurrent Agents',
      icon: Zap,
      meta: result ? `asyncio.gather(${agentsUsed.length})` : 'Ephemeral execution',
      badge: `${agentsUsed.length}/5 Active`,
      color: '#10b981',
      details: {
        activated: agentsUsed,
        execution_model: 'Parallel Ephemeral Execution via asyncio.gather()',
        latency_formula: 'L_dynamic(Q) = max{ λ(ai) : ai ∈ S(Q) }',
      },
    },
    {
      id: 'memory',
      step: '06',
      title: 'Memory Slicing',
      icon: Scissors,
      meta: result ? 'Context partitioned' : 'M(ai) ⊆ GlobalContext',
      badge: 'Scoped',
      color: '#f59e0b',
      details: {
        slices: memorySlices,
        formula: 'M(ai) = { k ∈ G : Relevance(k, role(ai)) ≥ θ }',
        advantage: 'Zero context flooding, eliminates cross-agent hallucination',
      },
    },
    {
      id: 'synthesis',
      step: '07',
      title: 'Confidence Synthesis',
      icon: CheckCircle2,
      meta: result ? `Confidence: ${(confidence * 100).toFixed(0)}%` : 'Confidence merge',
      badge: `${(confidence * 100).toFixed(0)}% Conf`,
      color: '#06b6d4',
      details: {
        overall_confidence: confidence,
        tokens_used: result?.tokens_used || result?.dynamic_tokens || 0,
        latency_ms: result?.latency_ms || result?.dynamic_latency_ms || 0,
      },
    },
  ];

  return (
    <div className="glass-panel pipeline-section">
      <div className="section-header">
        <div className="section-title">
          <Zap size={20} color="#06b6d4" />
          <span>Real-Time Execution Pipeline</span>
          {isRunning && (
            <span className="node-badge" style={{ background: 'rgba(6, 182, 212, 0.2)' }}>
              ⚡ Orchestrating Stage {activeStep}/7...
            </span>
          )}
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Click any stage node to inspect data payload
        </div>
      </div>

      <div className="pipeline-flow">
        {nodes.map((node, idx) => {
          const status = getNodeStatus(idx + 1);
          const isSelected = selectedNode?.id === node.id;
          const IconComponent = node.icon;

          return (
            <div
              key={node.id}
              className={`pipeline-node ${status} ${isSelected ? 'selected' : ''}`}
              onClick={() => setSelectedNode(isSelected ? null : node)}
              style={{
                borderColor: isSelected ? 'var(--cyan-bright)' : undefined,
              }}
            >
              <div className="node-header">
                <span className="node-step">{node.step}</span>
                <div style={{ color: node.color }}>
                  <IconComponent size={18} />
                </div>
              </div>

              <div className="node-title">{node.title}</div>
              <div className="node-meta">{node.meta}</div>

              <div
                className="node-badge"
                style={{
                  color: node.color,
                  backgroundColor: `${node.color}18`,
                  borderColor: `${node.color}35`,
                }}
              >
                {node.badge}
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Node Inspector Drawer */}
      {selectedNode && (
        <div
          className="glass-panel animate-fade-in"
          style={{
            marginTop: '0.5rem',
            padding: '1.25rem',
            background: 'var(--bg-elevated)',
            border: '1px solid rgba(6, 182, 212, 0.3)',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '0.75rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="node-step" style={{ background: 'var(--cyan-deep)', color: '#fff' }}>
                {selectedNode.step}
              </span>
              <strong style={{ color: 'var(--cyan-bright)' }}>{selectedNode.title} Inspector</strong>
            </div>
            <button
              className="btn-secondary"
              style={{ padding: '0.2rem 0.6rem', fontSize: '0.75rem' }}
              onClick={() => setSelectedNode(null)}
            >
              Close
            </button>
          </div>

          <pre
            className="mono"
            style={{
              background: 'var(--bg-input)',
              padding: '0.85rem',
              borderRadius: '6px',
              fontSize: '0.8rem',
              color: '#38bdf8',
              overflowX: 'auto',
              maxHeight: '220px',
            }}
          >
            {JSON.stringify(selectedNode.details, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
