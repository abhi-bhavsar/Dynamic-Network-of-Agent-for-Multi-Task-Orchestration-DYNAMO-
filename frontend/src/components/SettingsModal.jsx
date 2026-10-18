import React, { useState } from 'react';
import { X, Server, Check, Key, RotateCcw, Cpu } from 'lucide-react';
import { getApiBaseUrl, setApiBaseUrl, checkHealth } from '../services/api';

export default function SettingsModal({ isOpen, onClose, onResetSession, health, onRefreshHealth }) {
  if (!isOpen) return null;

  const [url, setUrl] = useState(getApiBaseUrl());
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const handleSave = async () => {
    setApiBaseUrl(url);
    setTesting(true);
    const h = await checkHealth();
    setTesting(false);
    setTestResult(h);
    onRefreshHealth();
  };

  return (
    <div className="modal-overlay animate-fade-in" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Server size={20} color="var(--cyan-bright)" />
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>System Configuration</h3>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Backend Endpoint Config */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
          <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-main)' }}>
            FastAPI Backend Endpoint URL
          </label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="http://localhost:8000"
              style={{
                flex: 1,
                padding: '0.65rem 0.85rem',
                background: 'var(--bg-input)',
                border: '1px solid var(--border-medium)',
                borderRadius: '8px',
                color: 'var(--text-main)',
                fontSize: '0.88rem',
                fontFamily: 'JetBrains Mono',
                outline: 'none',
              }}
            />
            <button className="btn-primary" onClick={handleSave} disabled={testing}>
              {testing ? 'Testing...' : 'Connect'}
            </button>
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
            FastAPI server address (defaults to localhost:8000 or containerized network backend:8000)
          </div>
        </div>

        {testResult && (
          <div
            style={{
              padding: '0.75rem',
              borderRadius: '6px',
              fontSize: '0.78rem',
              background: testResult.online ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
              border: `1px solid ${testResult.online ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
              color: testResult.online ? '#34d399' : '#f87171',
            }}
          >
            {testResult.online
              ? `✓ Connected successfully to DYNAMO Backend (Model: ${testResult.model})`
              : `✗ Could not connect to ${url}. Running in Interactive Demo Mode.`}
          </div>
        )}

        {/* Groq Information */}
        <div style={{ background: 'var(--bg-input)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-main)' }}>
            <Key size={14} color="var(--amber-bright)" />
            <span>Groq LLM Configuration</span>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            DYNAMO uses Groq's high-speed inference engine for specialist agent execution and LangGraph synthesis.
            Set your key in <code className="mono" style={{ color: 'var(--cyan-bright)' }}>.env</code>:
          </p>
          <pre className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', background: 'rgba(0,0,0,0.3)', padding: '0.5rem', borderRadius: '4px' }}>
            GROQ_API_KEY=gsk_...
          </pre>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem', marginTop: '0.5rem' }}>
          <button
            className="btn-secondary"
            onClick={() => {
              onResetSession();
              onClose();
            }}
            style={{ color: '#f87171', borderColor: 'rgba(239, 68, 68, 0.3)' }}
          >
            <RotateCcw size={14} />
            Clear Session & Cache
          </button>

          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
