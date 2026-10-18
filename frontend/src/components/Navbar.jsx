import React from 'react';
import {
  Zap,
  Activity,
  Cpu,
  Layers,
  BarChart3,
  Settings,
  RotateCcw,
  Wifi,
  WifiOff,
  Server,
} from 'lucide-react';

export default function Navbar({
  activeTab,
  setActiveTab,
  health,
  onResetSession,
  onOpenSettings,
  isSimulated,
}) {
  return (
    <header className="navbar">
      <div className="nav-brand">
        <div className="brand-icon-wrap">
          <Zap size={24} color="#06b6d4" />
        </div>
        <div>
          <div className="brand-title">
            DYNAMO
            <span className="badge-version">v2.0</span>
          </div>
          <div className="brand-subtitle">
            Policy-Selective Adaptive Multi-Agent Orchestrator
          </div>
        </div>
      </div>

      <nav className="nav-tabs">
        <button
          className={`nav-tab-btn ${activeTab === 'command' ? 'active' : ''}`}
          onClick={() => setActiveTab('command')}
        >
          <Activity size={16} />
          Command Center
        </button>

        <button
          className={`nav-tab-btn ${activeTab === 'pse' ? 'active' : ''}`}
          onClick={() => setActiveTab('pse')}
        >
          <Cpu size={16} />
          PSE Simulator
        </button>

        <button
          className={`nav-tab-btn ${activeTab === 'fleet' ? 'active' : ''}`}
          onClick={() => setActiveTab('fleet')}
        >
          <Layers size={16} />
          Agent Fleet
        </button>

        <button
          className={`nav-tab-btn ${activeTab === 'telemetry' ? 'active' : ''}`}
          onClick={() => setActiveTab('telemetry')}
        >
          <BarChart3 size={16} />
          Telemetry & IEEE Benchmarks
        </button>
      </nav>

      <div className="nav-actions">
        {/* Backend Connectivity Status */}
        <div
          className={`status-badge ${
            health.online ? (health.groqConnected ? 'online' : 'degraded') : 'offline'
          }`}
          title={
            health.online
              ? `Connected to ${health.model} (Groq API OK)`
              : 'Backend offline — Running in Interactive Simulation Mode'
          }
        >
          <span className="status-dot"></span>
          {health.online ? (
            <span>{health.groqConnected ? 'Backend Live' : 'Groq Key Missing'}</span>
          ) : (
            <span>Demo Mode</span>
          )}
        </div>

        <button
          className="btn-icon"
          onClick={onResetSession}
          title="Reset Session History & Telemetry"
        >
          <RotateCcw size={16} />
        </button>

        <button
          className="btn-icon"
          onClick={onOpenSettings}
          title="System Configuration"
        >
          <Settings size={16} />
        </button>
      </div>
    </header>
  );
}
