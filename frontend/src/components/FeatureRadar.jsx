import React from 'react';
import { Target, HelpCircle } from 'lucide-react';

export default function FeatureRadar({ featureVector }) {
  const fv = featureVector || { N: 0.75, U: 0.35, C: 2, R: 0.1 };

  const dimensions = [
    { key: 'N', label: 'Novelty (N)', val: fv.N || 0, max: 1, desc: 'How different is this query from session history? (1 = completely new)', color: '#06b6d4' },
    { key: 'U', label: 'Urgency (U)', val: fv.U || 0, max: 1, desc: 'Does the query require real-time / immediate live data?', color: '#f59e0b' },
    { key: 'C', label: 'Complexity (C)', val: (fv.C || 1) / 5, raw: `${fv.C || 1}/5`, max: 1, desc: 'Predicted agent cardinality required (1 = single, 5 = full suite)', color: '#8b5cf6' },
    { key: 'R', label: 'Recurrence (R)', val: fv.R || 0, max: 1, desc: 'Fraction of session history semantically similar to this query', color: '#10b981' },
  ];

  // SVG Radar coordinates calculation (center = 110, 110; radius = 80)
  const cx = 110;
  const cy = 110;
  const radius = 75;

  const getCoordinates = (index, value) => {
    const angle = (Math.PI / 2) + (index * (2 * Math.PI / 4));
    const r = radius * Math.min(1, Math.max(0.1, value));
    const x = cx + r * Math.cos(angle);
    const y = cy - r * Math.sin(angle);
    return { x, y };
  };

  const points = dimensions.map((d, i) => {
    const { x, y } = getCoordinates(i, d.val);
    return `${x},${y}`;
  }).join(' ');

  const gridCircles = [0.25, 0.5, 0.75, 1.0];

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, fontSize: '1.05rem' }}>
          <Target size={18} color="#06b6d4" />
          <span>PSE Analysis — Feature Vector F(Q)</span>
        </div>
        <span className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          F(Q) = (N, U, C, R)
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
        {/* Radar SVG */}
        <div style={{ flex: '0 0 220px', display: 'flex', justifyContent: 'center' }}>
          <svg width="220" height="220" viewBox="0 0 220 220">
            {/* Background grid concentric circles */}
            {gridCircles.map((ratio) => (
              <circle
                key={ratio}
                cx={cx}
                cy={cy}
                r={radius * ratio}
                fill="none"
                stroke="rgba(255, 255, 255, 0.08)"
                strokeDasharray={ratio < 1 ? '3 3' : 'none'}
              />
            ))}

            {/* Axis Lines */}
            <line x1={cx} y1={cy - radius} x2={cx} y2={cy + radius} stroke="rgba(255, 255, 255, 0.12)" />
            <line x1={cx - radius} y1={cy} x2={cx + radius} y2={cy} stroke="rgba(255, 255, 255, 0.12)" />

            {/* Radar Polygon */}
            <polygon
              points={points}
              fill="rgba(6, 182, 212, 0.25)"
              stroke="#06b6d4"
              strokeWidth="2.5"
            />

            {/* Corner dots */}
            {dimensions.map((d, i) => {
              const { x, y } = getCoordinates(i, d.val);
              return (
                <circle
                  key={d.key}
                  cx={x}
                  cy={y}
                  r="4.5"
                  fill={d.color}
                  stroke="#ffffff"
                  strokeWidth="1.5"
                />
              );
            })}

            {/* Axis Labels */}
            <text x={cx} y={cy - radius - 8} fill="#06b6d4" fontSize="10" fontWeight="700" textAnchor="middle" fontFamily="JetBrains Mono">
              Novelty
            </text>
            <text x={cx - radius - 10} y={cy + 3} fill="#f59e0b" fontSize="10" fontWeight="700" textAnchor="end" fontFamily="JetBrains Mono">
              Urgency
            </text>
            <text x={cx} y={cy + radius + 15} fill="#8b5cf6" fontSize="10" fontWeight="700" textAnchor="middle" fontFamily="JetBrains Mono">
              Complexity
            </text>
            <text x={cx + radius + 10} y={cy + 3} fill="#10b981" fontSize="10" fontWeight="700" textAnchor="start" fontFamily="JetBrains Mono">
              Recurrence
            </text>
          </svg>
        </div>

        {/* Feature Cards Grid */}
        <div style={{ flex: '1', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.85rem' }}>
          {dimensions.map((dim) => (
            <div
              key={dim.key}
              style={{
                padding: '0.9rem',
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.35rem',
              }}
              title={dim.desc}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                  {dim.label}
                </span>
                <HelpCircle size={12} color="var(--text-dim)" />
              </div>

              <div className="mono" style={{ fontSize: '1.35rem', fontWeight: 800, color: dim.color }}>
                {dim.raw || (typeof dim.val === 'number' ? dim.val.toFixed(2) : dim.val)}
              </div>

              {/* Progress bar */}
              <div style={{ height: '4px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '999px', overflow: 'hidden' }}>
                <div
                  style={{
                    height: '100%',
                    width: `${Math.min(100, Math.max(8, dim.val * 100))}%`,
                    backgroundColor: dim.color,
                    borderRadius: '999px',
                  }}
                />
              </div>

              <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', lineHeight: 1.3 }}>
                {dim.desc}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
