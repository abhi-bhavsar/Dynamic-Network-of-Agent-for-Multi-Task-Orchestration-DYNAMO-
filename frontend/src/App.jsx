import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ExecutionPipeline from './components/ExecutionPipeline';
import FeatureRadar from './components/FeatureRadar';
import AgentTraceView from './components/AgentTraceView';
import MemorySlicingDemo from './components/MemorySlicingDemo';
import ReportViewer from './components/ReportViewer';
import BenchmarkComparison from './components/BenchmarkComparison';
import PseSimulator from './components/PseSimulator';
import AgentFleetExplorer from './components/AgentFleetExplorer';
import TelemetryDashboard from './components/TelemetryDashboard';
import SettingsModal from './components/SettingsModal';
import { checkHealth, executeQuery, executeBenchmark } from './services/api';
import { MOCK_QUERIES, generateSimulatedResponse } from './services/mockData';
import {
  Sparkles,
  Zap,
  BarChart2,
  SlidersHorizontal,
  Flame,
  Search,
  CheckCircle2,
  Layers,
  ArrowRight,
  TrendingDown,
  Coins,
  Timer,
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('command');
  const [query, setQuery] = useState('');
  const [isBenchmark, setIsBenchmark] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [activeStep, setActiveStep] = useState(1);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [sessionStats, setSessionStats] = useState({
    totalQueries: 0,
    totalTokens: 0,
    totalSaved: 0,
  });
  const [health, setHealth] = useState({
    online: false,
    model: 'Initializing...',
    groqConnected: false,
  });
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [showMemorySlices, setShowMemorySlices] = useState(true);
  const [showAgentTrace, setShowAgentTrace] = useState(true);

  // Initial health check on mount & periodic polling
  const refreshHealth = async () => {
    const h = await checkHealth();
    setHealth(h);
  };

  useEffect(() => {
    refreshHealth();
    const interval = setInterval(refreshHealth, 8000);
    return () => clearInterval(interval);
  }, []);

  // Set an initial simulated result so page has rich context immediately
  useEffect(() => {
    const initialQuery = MOCK_QUERIES[1].query;
    setQuery(initialQuery);
    const initialRes = generateSimulatedResponse(initialQuery, false);
    setResult(initialRes);
    setHistory([
      {
        ...initialRes,
        timestamp: Date.now() - 60000,
      },
    ]);
    setSessionStats({
      totalQueries: 1,
      totalTokens: initialRes.tokens_used,
      totalSaved: Math.round(initialRes.tokens_used * 0.95),
    });
  }, []);

  const handleRun = async () => {
    if (!query.trim() || isRunning) return;

    setIsRunning(true);
    setActiveStep(1);

    // Step animation timer sequence
    const stepInterval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev < 6) return prev + 1;
        return prev;
      });
    }, 280);

    try {
      const sessionHistory = history.map((h) => h.query).slice(-10);
      let data;
      if (isBenchmark) {
        data = await executeBenchmark(query.trim());
      } else {
        data = await executeQuery(query.trim(), sessionHistory);
      }

      clearInterval(stepInterval);
      setActiveStep(7);
      setResult(data);

      const tokens = data.tokens_used || data.dynamic_tokens || 0;
      const staticTokens = data.static_tokens || Math.round(tokens * 2.1);
      const saved = Math.max(0, staticTokens - tokens);

      setSessionStats((prev) => ({
        totalQueries: prev.totalQueries + 1,
        totalTokens: prev.totalTokens + tokens,
        totalSaved: prev.totalSaved + saved,
      }));

      setHistory((prev) => [
        {
          ...data,
          timestamp: Date.now(),
        },
        ...prev,
      ]);
    } catch (err) {
      console.error('Execution error:', err);
    } finally {
      clearInterval(stepInterval);
      setTimeout(() => {
        setIsRunning(false);
      }, 400);
    }
  };

  const handleResetSession = () => {
    setHistory([]);
    setSessionStats({ totalQueries: 0, totalTokens: 0, totalSaved: 0 });
    setResult(null);
  };

  const handleSelectSample = (sampleText) => {
    setQuery(sampleText);
  };

  return (
    <div className="app-container">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
        onResetSession={handleResetSession}
        onOpenSettings={() => setSettingsOpen(true)}
      />

      {/* View Switcher */}
      {activeTab === 'command' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
          {/* Hero Query Input Card */}
          <section className="glass-panel-glow query-card">
            <div className="query-header">
              <div className="query-title-wrap">
                <Flame size={20} color="#06b6d4" />
                <span className="query-title">Research Query Orchestrator</span>
              </div>

              {/* Mode Toggle: Standard vs Benchmark */}
              <div className="mode-toggle-group">
                <button
                  className={`mode-toggle-btn ${!isBenchmark ? 'active' : ''}`}
                  onClick={() => setIsBenchmark(false)}
                >
                  ⚡ Dynamic Execution
                </button>
                <button
                  className={`mode-toggle-btn ${isBenchmark ? 'active' : ''}`}
                  onClick={() => setIsBenchmark(true)}
                >
                  📊 Benchmark Mode (vs Static)
                </button>
              </div>
            </div>

            <div className="textarea-wrap">
              <textarea
                className="query-textarea"
                rows={3}
                placeholder="Enter financial research query, e.g., 'Analyze Tesla Q4 earnings and margin expansion' or 'Comprehensive investment thesis for Reliance Industries across Jio and Retail'..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                    handleRun();
                  }
                }}
              />
            </div>

            <div className="query-footer">
              <div className="sample-queries">
                <span className="sample-label">Try Preset:</span>
                {MOCK_QUERIES.map((sample, idx) => (
                  <button
                    key={idx}
                    className="sample-pill"
                    onClick={() => handleSelectSample(sample.query)}
                  >
                    {sample.label}
                  </button>
                ))}
              </div>

              <button
                className="btn-primary"
                onClick={handleRun}
                disabled={isRunning || !query.trim()}
              >
                {isRunning ? (
                  <>
                    <Zap size={18} className="status-dot" />
                    <span>Orchestrating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    <span>Run DYNAMO</span>
                  </>
                )}
              </button>
            </div>
          </section>

          {/* Real-Time Visual Execution Pipeline */}
          <ExecutionPipeline
            isRunning={isRunning}
            result={result}
            activeStep={activeStep}
          />

          {/* Quick Telemetry KPI Bar */}
          {result && (
            <div className="metrics-row animate-fade-in">
              <div className="glass-panel metric-card">
                <span className="metric-label">
                  <SlidersHorizontal size={14} color="var(--cyan-bright)" />
                  PSE Policy Selected
                </span>
                <span className="metric-value" style={{ color: 'var(--cyan-bright)', fontSize: '1.45rem' }}>
                  {(result.policy || result.policy_selected || 'on_demand').toUpperCase()}
                </span>
                <span className="metric-delta neutral">Rule priority evaluated</span>
              </div>

              <div className="glass-panel metric-card">
                <span className="metric-label">
                  <Layers size={14} color="#10b981" />
                  Agents Spawned
                </span>
                <span className="metric-value">
                  {result.agents_used?.length || result.agents_spawned || 1}
                  <span style={{ fontSize: '1rem', color: 'var(--text-dim)', fontWeight: 500 }}> / 5</span>
                </span>
                <span className="metric-delta positive">
                  -{5 - (result.agents_used?.length || result.agents_spawned || 1)} idle pruned
                </span>
              </div>

              <div className="glass-panel metric-card">
                <span className="metric-label">
                  <Coins size={14} color="#f59e0b" />
                  Tokens Consumed
                </span>
                <span className="metric-value">
                  {(result.tokens_used || result.dynamic_tokens || 0).toLocaleString()}
                </span>
                <span className="metric-delta positive">
                  {result.token_savings_pct ? `-${result.token_savings_pct}% saved` : 'Tightly scoped context'}
                </span>
              </div>

              <div className="glass-panel metric-card">
                <span className="metric-label">
                  <Timer size={14} color="#8b5cf6" />
                  Execution Latency
                </span>
                <span className="metric-value">
                  {(result.latency_ms || result.dynamic_latency_ms || 0).toFixed(0)}
                  <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}> ms</span>
                </span>
                <span className="metric-delta neutral">Parallel asyncio.gather</span>
              </div>

              <div className="glass-panel metric-card">
                <span className="metric-label">
                  <CheckCircle2 size={14} color="#34d399" />
                  Synthesis Confidence
                </span>
                <span className="metric-value" style={{ color: '#34d399' }}>
                  {Math.round((result.confidence || 0.88) * 100)}%
                </span>
                <span className="metric-delta positive">Confidence-weighted</span>
              </div>
            </div>
          )}

          {/* Benchmark Comparison Mode View */}
          {(isBenchmark || result?.token_savings_pct !== undefined) && result && (
            <BenchmarkComparison benchmarkResult={result} />
          )}

          {/* 2-Column Responsive Dashboard */}
          <div className="dashboard-grid">
            {/* Left Column: Deep Dive Telemetry & Observability */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Feature Vector Polar Radar */}
              <FeatureRadar featureVector={result?.feature_vector} />

              {/* Subagent Execution Trace */}
              {showAgentTrace && (
                <AgentTraceView
                  agentOutputs={result?.agent_outputs}
                  agentsUsed={result?.agents_used || []}
                />
              )}

              {/* Memory Slicing Deep Dive */}
              {showMemorySlices && (
                <MemorySlicingDemo
                  memorySlices={result?.memory_slices}
                  agentsUsed={result?.agents_used || []}
                />
              )}
            </div>

            {/* Right Column: Synthesized Final Research Report */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <ReportViewer
                report={result?.report}
                confidence={result?.confidence}
                query={result?.query || query}
              />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'pse' && <PseSimulator />}

      {activeTab === 'fleet' && <AgentFleetExplorer />}

      {activeTab === 'telemetry' && (
        <TelemetryDashboard
          history={history}
          sessionStats={sessionStats}
          onSelectQuery={(pastQuery) => {
            setQuery(pastQuery);
            setActiveTab('command');
          }}
        />
      )}

      {/* Settings Modal */}
      <SettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        onResetSession={handleResetSession}
        health={health}
        onRefreshHealth={refreshHealth}
      />
    </div>
  );
}
